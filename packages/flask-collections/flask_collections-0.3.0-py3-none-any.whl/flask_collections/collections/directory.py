import os
from ..collection import BaseCollection, CollectionEntry


class DirectoryCollection(BaseCollection):
    file_types = ("html", "md")
    entry_cls = CollectionEntry

    @classmethod
    def matches_config(cls, config):
        return config.get("path") and os.path.isdir(config["path"])

    def __init__(self, name, path, **kwargs):
        super().__init__(name, **kwargs)
        self.path = path

    def load(self):
        for filename in sorted(os.listdir(self.path)):
            yield self._create_entry(filename)

    def _create_entry(self, filename):
        return self.entry_cls.from_file(self, os.path.join(self.path, filename))
