# coding=utf-8
from ut_dic.dic import Dic
from ut_obj.obj import Obj

from collections.abc import Callable
from typing import Any, Dict, Union

TyArr = list[Any]
TyCallable = Callable[..., Any]
TyDic = dict[Any, Any]
TyStr = str
TyArr_Str = str | TyArr
TyDnDoC = Dict[Any, Union['TyDnDoC', Callable[..., Any]]]

TnStr = None | TyStr
TnArr_Str = None | TyArr_Str
TnCallable = None | TyCallable
TnDnDoC = None | TyDnDoC


class DoC:
    """
    Dictionary of Callables
    """
    @classmethod
    def ex_cmd(cls, doc: TnDnDoC, kwargs: TyDic) -> None:
        """
        Get the cmd from arguments and keyword argument list kwargs
        and call the ex function with the given cmd.
        """
        cmd: TyArr_Str = Dic.locate_key(kwargs, 'cmd')
        cls.ex(doc, cmd, kwargs)

    @classmethod
    def ex(cls, doc: TnDnDoC, cmd: TnArr_Str, kwargs: TyDic) -> None:
        """
        Locate the function with the given cmd in the Dictionary of
        callables and execute the function with the keyword arguments.
        """
        _a_cmd = Obj.sh_arr(cmd)
        if not doc:
            _msg = "Function table: 'doc' is not defined"
            raise Exception(_msg)
        fnc: TyCallable = Dic.locate_key(doc, _a_cmd)
        fnc(kwargs)
