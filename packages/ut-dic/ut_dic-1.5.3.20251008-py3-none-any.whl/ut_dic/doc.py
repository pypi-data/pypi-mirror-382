# coding=utf-8
from ut_dic.dic import Dic

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
        cmd: TnArr_Str = kwargs.get('cmd')
        cls.ex(doc, cmd, kwargs)

    @classmethod
    def ex(cls, doc: TnDnDoC, cmd: TnArr_Str, kwargs: TyDic) -> None:
        """
        Locate the function with the given cmd in the Dictionary of
        callables and execute the function with the keyword arguments.
        """
        if not cmd:
            msg = f"Command: {cmd} is not defined"
            raise Exception(msg)
            return
        if not doc:
            msg = f"Function table: {doc} is not defined"
            return
        if not isinstance(cmd, list):
            cmd = [cmd]
        fnc: TnCallable = Dic.locate(doc, cmd)
        if fnc is None:
            msg = f"Command: {cmd} is not defined in function table: {doc}"
            raise Exception(msg)
        fnc(kwargs)
