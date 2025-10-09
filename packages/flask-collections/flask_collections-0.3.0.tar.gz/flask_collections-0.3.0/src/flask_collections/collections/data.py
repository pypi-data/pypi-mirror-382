from ..collection import BaseCollection, CollectionEntry
import csv
import json
import yaml
import os
import sqlite3
import abc


class DataCollection(BaseCollection):
    entry_cls = CollectionEntry

    @classmethod
    def matches_config(cls, config):
        return isinstance(config.get("entries"), list)

    def __init__(self, name, entries, **kwargs):
        super().__init__(name, **kwargs)
        self._entries = entries

    def load(self):
        for obj in self._entries:
            yield self.entry_cls.from_data(self, obj)


class BaseDataFileCollection(BaseCollection, abc.ABC):
    entry_cls = CollectionEntry

    @classmethod
    def matches_config(cls, config):
        return (
            config.get("path")
            and os.path.isfile(config["path"])
            and os.path.basename(config["path"]).split(".", 1)[1].lower()
            in getattr(cls, "file_exts", [])
        )

    def __init__(self, app, name, path, **kwargs):
        super().__init__(app, name, **kwargs)
        self.path = path


class CSVCollection(BaseDataFileCollection):
    file_exts = ("csv",)

    def load(self):
        with open(self.path) as f:
            reader = csv.DictReader(f, **self.config.get("csv_options", {}))
            for row in reader:
                yield self.entry_cls.from_data(self, row)


class JSONCollection(BaseDataFileCollection):
    file_exts = ("json",)

    def load(self):
        with open(self.path) as f:
            for row in json.load(f):
                yield self.entry_cls.from_data(self, row)


class YAMLCollection(BaseDataFileCollection):
    file_exts = ("yaml", "yml")

    def load(self):
        with open(self.path) as f:
            for row in yaml.safe_load(f):
                yield self.entry_cls.from_data(self, row)


class SQLiteCollection(BaseDataFileCollection):
    file_exts = ("db", "sqlite", "sqlite3")

    def load(self):
        if self.config.get("query"):
            query = self.config["query"]
        elif self.config.get("table"):
            query = f"SELECT * FROM {self.config['table']}"
        else:
            raise ValueError("Either 'query' or 'table' must be specified in the config")
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        for row in c.execute(query):
            yield self.entry_cls.from_data(self, row)
        c.close()
        conn.close()
