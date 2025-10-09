import os
import yaml
import markdown
import re
from flask import url_for, abort, render_template, render_template_string
from markupsafe import Markup


class MissingCollectionEntryLayoutError(Exception):
    pass


class CollectionEntry:
    @classmethod
    def from_data(cls, collection, data):
        props = dict(data)
        slug_prop = collection.config.get("slug_prop", "slug")
        if not props.get(slug_prop):
            raise ValueError(f"Missing required attribute '{slug_prop}' in data")
        slug = props.pop(slug_prop)
        content_prop = collection.config.get("content_prop")
        if content_prop and content_prop != "content":
            props["content"] = props.pop(content_prop, None)
        return cls(collection, slug, **props)

    @classmethod
    def from_file(cls, collection, filename):
        props = {
            "filename": filename,
            collection.config.get("is_markdown_prop", "is_markdown"): filename.endswith(".md"),
        }

        slug = os.path.basename(filename).rsplit(".", 1)[0]
        m = re.match(collection.config.get("filename_template", ".*"), slug)
        if m and m.groups():
            props.update(m.groupdict())
            slug = props.pop(collection.config.get("slug_prop", "slug"), None)
        if not slug:
            raise ValueError(f"Invalid filename '{filename}' for slug extraction")

        with open(filename) as f:
            content, frontmatter = parse_frontmatter(f.read())
        if frontmatter:
            props.update(yaml.safe_load(frontmatter))

        return cls(collection, slug, content, **props)

    def __init__(self, collection, slug, content=None, layout=None, **props):
        self.collection = collection
        self.slug = slug
        self.content = content
        self.layout = layout
        self.props = props

    @property
    def url(self):
        return url_for(self.collection.endpoint, slug=self.slug)

    def __getattr__(self, name):
        return self.props[name]

    def render(self, with_layout=True):
        content = self.content

        if self.props.get(self.collection.config.get("is_template_prop", "is_template")):
            ctx = dict(self.props, entry=self)
            content = render_template_string(self.content, **ctx)

        if self.props.get(self.collection.config.get("is_markdown_prop", "is_markdown")):
            content = Markup(
                markdown.markdown(content, **self.collection.config.get("markdown_options", {}))
            )
        else:
            content = Markup(content)

        if not with_layout:
            return content

        layout = self.layout
        if layout is None or layout is True:
            layout = self.collection.layout
        if not layout:
            return content

        return render_template(layout, entry=self, content=content)


class CollectionEntryNotFoundError(Exception):
    pass


class BaseCollection:
    default_config = {
        "slug_prop": "slug",
        "content_prop": "content",
        "is_template_prop": "is_template",
        "is_markdown_prop": "is_markdown",
        "filename_template": r"((?P<date>\d{4}-\d{2}-\d{2})-)?(?P<slug>.*)",
    }

    @classmethod
    def matches_config(cls, config):
        return False

    def __init__(self, name, url=None, url_rule=None, endpoint=None, layout=None, **config):
        self.name = name
        if url is False:
            self.url = None
            self.url_rule = None
            self.endpoint = None
        else:
            self.url = url or f"/{name}"
            self.url_rule = url_rule or f"/{self.url.strip('/')}/<path:slug>"
            self.endpoint = endpoint or f"collections.{name}"
        self.layout = layout
        self.config = config
        if self.default_config:
            self.config = {**self.default_config, **config}

    def load(self):
        raise NotImplementedError()

    def get(self, slug):
        for entry in self.entries:
            if entry.slug == slug:
                return entry
        raise CollectionEntryNotFoundError()

    def get_or_404(self, slug):
        try:
            return self.get(slug)
        except CollectionEntryNotFoundError:
            abort(404)

    def register(self, app):
        if self.url_rule is None:
            raise Exception("Cannot register collection without urls")
        app.add_url_rule(self.url_rule, self.endpoint, lambda slug: self.get_or_404(slug).render())

    @property
    def entries(self):
        if "entries" not in self.__dict__:
            self.__dict__["entries"] = list(self.load())
        return self.__dict__["entries"]

    def __iter__(self):
        return iter(self.entries)

    def __len__(self):
        return len(self.entries)

    def page(self, page, per_page=25):
        return self.entries[page * per_page : (page + 1) * per_page]

    def __getitem__(self, slug):
        if isinstance(slug, slice):
            return self.entries[slug]
        return self.get(slug)


def parse_frontmatter(source):
    if source.startswith("---\n"):
        frontmatter_end = source.find("\n---\n", 3)
        if frontmatter_end == -1:
            frontmatter = source[3:]
            source = ""
        else:
            frontmatter = source[3:frontmatter_end]
            source = source[frontmatter_end + 5 :]
        return source, frontmatter
    return source, None
