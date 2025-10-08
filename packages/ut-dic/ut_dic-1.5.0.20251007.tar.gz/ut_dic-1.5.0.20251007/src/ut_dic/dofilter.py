from typing import Any, TypedDict
TyDic = dict[Any, Any]


class TyDoFilter(TypedDict):
    key: str
    value: Any
    method: str


TnDoFilter = None | TyDoFilter


class DoFilter:

    @staticmethod
    def new(key: str, value: Any, method: str = 'df') -> TyDoFilter:
        # def new_d_filter(key: str, value: Any, method: str = 'df') -> TyDoFilter:
        # def sh_d_filter(key: str, value: Any, method: str = 'df') -> TyDic:
        """
        Create new filter dictionary with key, value and method pairs
        """
        d_filter: TyDoFilter = {'key': key, 'value': value, 'method': method}
        return d_filter
