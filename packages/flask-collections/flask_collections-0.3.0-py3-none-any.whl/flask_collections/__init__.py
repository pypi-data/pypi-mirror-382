import os
from .collections import discover_collection_cls


class Collections:
    def __init__(self, app=None, **kwargs):
        self.collections = {}
        if app:
            self.init_app(app, **kwargs)

    def init_app(
        self,
        app,
        collections_folder="collections",
        markdown_options=None,
        base_collection_config=None,
    ):
        self.app = app
        self.base_collection_config = (
            app.config.get("COLLECTIONS_BASE_CONFIG", base_collection_config) or {}
        )
        markdown_options = app.config.get("COLLECTIONS_MARKDOWN_OPTIONS", markdown_options) or {}
        if markdown_options:
            self.base_collection_config["markdown_options"] = markdown_options
        if os.path.exists(os.path.join(app.root_path, collections_folder)):
            self.register_from_dir(
                os.path.join(app.root_path, collections_folder),
                app.config.setdefault("COLLECTIONS", {}),
            )
        app.jinja_env.globals["collections"] = self.collections

    def __getattr__(self, name):
        return self.collections[name]

    def register_from_dir(self, path, config=None, register=True):
        if not os.path.isabs(path):
            path = os.path.join(self.app.root_path, path)
        if config is None:
            config = {}

        for f in os.listdir(path):
            if f.startswith(".") or f.startswith("_"):
                continue
            if os.path.isdir(os.path.join(path, f)):
                if os.path.exists(os.path.join(path, f, ".flaskignore")):
                    continue
                name = f
            else:
                name = f.split(".", 1)[0]
            config.setdefault(name, {}).update({"path": os.path.join(path, f)})

        return self.register_from_config(config, register)

    def register_from_config(self, config, register=True):
        for name, collection_config in config.items():
            collection_cls = discover_collection_cls(collection_config)
            if not collection_cls:
                raise Exception(f"Failed to initalize collection {name}")
            self.collections[name] = collection_cls(
                name, **dict(self.base_collection_config, **collection_config)
            )
            if register and self.collections[name].url:
                self.collections[name].register(self.app)

    def register_freezer_generator(self, freezer, collections=None):
        @freezer.register_generator
        def collections_generator():
            _collections = self.collections.values() if not collections else collections
            for collection in _collections:
                for entry in collection:
                    yield collection.endpoint, {"slug": entry.slug}
