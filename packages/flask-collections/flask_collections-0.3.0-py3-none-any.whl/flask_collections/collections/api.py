from ..collection import BaseCollection, CollectionEntry, CollectionEntryNotFoundError
import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth


class APICollection(BaseCollection):
    entry_cls = CollectionEntry

    @classmethod
    def matches_config(cls, config):
        return config.get("api_url")

    def __init__(
        self,
        name,
        api_url,
        headers=None,
        username=None,
        password=None,
        digest_auth=False,
        auth_token=None,
        auth=None,
        request_data_key=None,
        **kwargs,
    ):
        super().__init__(name, **kwargs)
        self.api_url = api_url
        self.request_data_key = request_data_key
        self.headers = headers or {}
        self.auth = auth
        if username or password:
            self.auth = (HTTPDigestAuth if digest_auth else HTTPBasicAuth)(
                username or "", password or ""
            )
        if auth_token:
            self.headers["Authorization"] = f"bearer {auth_token}"

    def _request(self, path=None, **kwargs):
        url = f"{self.url}/{path}" if path else self.url
        resp = requests.get(url, auth=self.auth, headers=self.headers, **kwargs)
        resp.raise_for_status()
        return resp

    def load(self):
        resp = self._request()
        next_page_params = None
        while True:
            data = resp.json()
            for entry in data[self.request_data_key] if self.request_data_key else data:
                yield self.entry_cls.from_data(self, entry)
            next_page_params = self.get_next_page_params(resp, next_page_params)
            if not next_page_params:
                break
            resp = self._request(**next_page_params)

    def get_next_page_params(self, resp, current_page_params):
        return None

    def get(self, slug):
        try:
            data = self._request(slug).json()
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                raise CollectionEntryNotFoundError()
            raise
        data = data[self.request_data_key] if self.request_data_key else data
        return self.entry_cls.from_data(self, data)


class StrapiCollectionEntry(CollectionEntry):
    @classmethod
    def from_data(cls, collection, data):
        return CollectionEntry.from_data(collection, data["attributes"])


class StrapiCollection(APICollection):
    entry_cls = StrapiCollectionEntry

    @classmethod
    def matches_config(cls, config):
        return config.get("strapi_url")

    def __init__(self, name, strapi_url, **kwargs):
        kwargs["request_data_key"] = "data"
        super().__init__(name, strapi_url, **kwargs)

    def get_next_page_params(self, resp, current_page_params):
        resp = resp.json()
        page_meta = resp.get("meta", {}).get("pagination")
        if page_meta and page_meta["page"] < page_meta["pageCount"]:
            return {"params": {"pagination[page]": page_meta["page"] + 1}}

    def get(self, slug):
        data = self._request(params={f"filters[{self.slug_attr}][$eq]": slug}).json()
        data = data[self.request_data_key] if self.request_data_key else data
        if not data:
            raise CollectionEntryNotFoundError()
        return self.entry_cls.from_data(self, data[0])
