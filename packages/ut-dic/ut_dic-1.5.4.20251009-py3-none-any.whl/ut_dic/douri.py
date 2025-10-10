from ut_obj.uri import Uri

from typing import Any, TypedDict
TyDic = dict[Any, Any]
TyPath = str
TyUri = str | bytes


class TyDoUri(TypedDict):
    authority: str
    schema: str
    path: TyPath
    query: str


TnDic = None | TyDic
TnDoUri = None | TyDoUri
TnUri = None | TyUri


class DoUri:

    @staticmethod
    def sh_uri(d_uri: TnDoUri) -> TnUri:
        if not d_uri:
            return None
        schema = d_uri.get('schema')
        authority = d_uri.get('schema')
        path = d_uri.get('path')
        query = d_uri.get('query')
        _uri: TnUri = None
        if schema is not None:
            _uri = f"{schema}"
        if authority is not None:
            _uri = f"{_uri!r}://{authority}"
        if path is not None:
            _uri = f"{_uri!r}{path}"
        if query is not None:
            _uri = f"{_uri!r}?{query}"
        return _uri

    @classmethod
    def sh_uri_by_params(cls, d_uri: TnDoUri, kwargs: TnDic) -> TnUri:
        if not d_uri:
            return None
        _uri: TnUri = cls.sh_uri(d_uri)
        if _uri is None:
            return None
        if kwargs is None:
            return _uri
        _params = kwargs.get('params')
        if _params is None:
            return _uri
        _uri = Uri.add_params(_uri, _params)
        return _uri
