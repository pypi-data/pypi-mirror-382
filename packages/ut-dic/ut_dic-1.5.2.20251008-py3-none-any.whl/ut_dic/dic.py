# import builtins
from collections.abc import Callable, Iterator
from typing import Any

TyAny = Any
TyArr = list[Any]
TyBool = bool
TyCallable = Callable[..., Any]
TyDic = dict[Any, Any]
TyAny_Dic = Any | TyDic
TyAoD = list[TyDic]
TyIterAny = Iterator[Any]
TyKey = Any
TyTup = tuple[Any, ...]
TyKeys = Any | TyArr | TyTup
TyStr = str
TyArrTup = TyArr | TyTup
TyToD = tuple[TyDic, ...]
TyToDD = tuple[TyDic, TyDic]

TnAny = None | Any
TnAny_Dic = None | TyAny_Dic
TnAoD = None | TyAoD
TnArr = None | TyArr
TnArrTup = None | TyArr | TyTup
TnBool = None | bool
TnCallable = None | TyCallable
TnDic = None | TyDic
TnKey = None | TyKey
TnKeys = None | TyKeys


class Dic:
    """
    Dictionary Management
    """
    loc_msg1 = "The 1. Parameter 'dic' is None or empty"
    loc_msg2 = "The 2. Parameter 'keys' is None or empty"
    loc_msg3 = "Key={} does not exist in Sub-Dictionary={} of Dictionary={}"
    loc_msg4 = "Value={} is not a Sub-Dictionary of Dictionary={}"

    """
    Miscellenous Methods
    """
    @classmethod
    def add_by_keys(cls, dic: TyDic, keys: TyKeys, value: TnAny) -> None:
        """
        Locate the values in a nested dictionary for the suceeding keys of
        a key array and replace the last value with the given value.
        """
        if not dic:
            return
        if not keys:
            return
        _dic = cls.locate_secondlast(dic, keys)
        cls.add_by_key(_dic, keys[-1], value)

    @staticmethod
    def add_by_key(dic: TyDic, key: TyKey, value: TnAny) -> None:
        """
        Locate the values in a nested dictionary for the suceeding keys of
        a key array and replace the last value with the given value.
        """
        if not dic:
            return
        if not key:
            return
        if key not in dic:
            dic[key] = value

    @classmethod
    def add_counter_by_keys(
            cls, dic: TyDic, keys: TyKeys, counter: Any = None) -> None:
        """
        Apply the function "add_counter_with key" to the last key of the
        key list and the dictionary localized by that key.
        """
        # def add_counter_to_values(
        if not isinstance(keys, (list, tuple)):
            cls.add_counter_by_key(dic, keys, counter)
        else:
            _dic: TnDic = cls.locate(dic, keys[:-1])
            cls.add_counter_by_key(_dic, keys[-1], counter)

    @staticmethod
    def add_counter_by_key(
            dic: TnDic, key: TyKey, counter: TyAny) -> None:
        # def cnt(
        """
        Initialize the unintialized counter with 1 and add it to the
        Dictionary value of the key.
        """
        # def add_counter_to_value(
        if not dic:
            return
        if counter is None:
            counter = 1
        if key not in dic:
            dic[key] = 0
        dic[key] = dic[key] + counter

    @staticmethod
    def filter_by_keys(dic: TyDic, keys: TyKeys) -> TyDic:
        """
        Filter Dictionary by a single key or an Array of Keys
        """
        if isinstance(keys, str):
            keys = [keys]
        dic_new: TyDic = {}
        for key, value in dic.items():
            if key in keys:
                dic_new[key] = value
        return dic_new

    @classmethod
    def increment_by_keys(
            cls, dic: TnDic, keys: TnKeys, item: Any = 1) -> None:
        # def increment(
        """
        Appply the function "increment_by_key" to the last key of
        the key list and the dictionary localized by that key.
        """
        # def increment_values(
        # def increment_by_keys(
        if not dic or keys is None:
            return
        if not isinstance(keys, list):
            keys = [keys]
        cls.increment_by_key(cls.locate(dic, keys[:-1]), keys[-1], item)

    @staticmethod
    def increment_by_key(
            dic: TnDic, key: Any, item: Any = 1) -> None:
        """
        Increment the value of the key if it is defined in the
        Dictionary, otherwise assign the item to the key.
        """
        # def increment_value(
        # def increment_by_key(
        # last element
        if not dic:
            pass
        elif key not in dic:
            dic[key] = item
        else:
            dic[key] += 1

    @staticmethod
    def is_not(dic: TyDic, key: TyStr) -> TyBool:
        """
        Return False if the key is defined in the Dictionary and
        the key value if not empty, othewise returm True.
        """
        if key in dic:
            if dic[key]:
                return False
        return True

    @staticmethod
    def lstrip_keys(dic: TyDic, string: TyStr) -> TyDic:
        """
        Remove the first string found in the Dictionary keys.
        """
        _dic_new: TyDic = {}
        for _k, _v in dic.items():
            _k_new = _k.replace(string, "", 1)
            _dic_new[_k_new] = _v
        return _dic_new

    @staticmethod
    def nvl(dic: TnDic) -> TyDic:
        """
        nvl function similar to SQL NVL function
        """
        if dic is None:
            return {}
        return dic

    @classmethod
    def rename_key_by_kwargs(cls, dic: TnDic, kwargs: TyDic) -> TnDic:
        """ rename old dictionary key with new dictionary key by kwargs
        """
        # def rename_key(
        # Dictionary is None or empty
        if not dic:
            return dic
        _key_old = kwargs.get("key_old")
        _key_new = kwargs.get("key_new")
        return cls.new_rename_key(dic, _key_old, _key_new)

    @staticmethod
    def to_aod(dic: TyDic, key_name: Any, value_name: Any) -> TyAoD:
        # def dic2aod(
        # Dictionary is None or empty
        if not dic:
            _aod = [dic, dic]
        _aod = []
        _dic = {}
        for _k, _v in dic.items():
            _dic[key_name] = _k
            _dic[value_name] = _v
            _aod.append(_dic)
            _dic = {}
        return _aod

    """
    Get Methods
    """
    @staticmethod
    def get_as_array(dic: TyDic, key: TyKey) -> TyArr:
        """
        show array of key value found for given key in dictionary
        """
        if not dic or not key:
            return []
        value: None | Any | TyArr = dic.get(key)
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]

    @staticmethod
    def get_by_keys(dic: TnDic, keys: TyKeys, default: Any = None) -> TnAny_Dic:
        # def get
        if dic is None:
            return None
        if not isinstance(keys, (list, tuple)):
            if keys in dic:
                return dic[keys]
            return default
        _dic = dic
        value = None
        for _key in keys:
            value = _dic.get(_key)
            if value is None:
                return None
            if not isinstance(value, dict):
                return value
            _dic = value
        return value

    @staticmethod
    def get_value_yn(
            dic: TyDic, key: str, value_y: Any, value_n: Any) -> Any:
        # def get_yn_value(dic: TyDic, key: str, value_y, value_n) -> Any:
        """
        Return value value_y if key is in dictionary otherwise
        return value value_n
        """
        if key in dic:
            return value_y
        return value_n

    @staticmethod
    def get(dic: TyDic, key: TyKey, default: Any = None) -> TnAny:
        # def get
        """
        Loop thru the nested dictionary with the keys from the
        key list until the key is found. If the last key of the
        key list is found return the value of the key, otherwise
        return None.
        """
        if dic is None:
            return None
        return dic.get(key, default)

    """
    Locate Methods
    """
    @classmethod
    def locate(cls, dic: TyDic, keys: TyKeys) -> TyAny:
        """
        Return the value of the key reached by looping thru the
        nested Dictionary with the keys from the key list until
        the value is None or the last key is reached.
        """
        if not dic:
            raise Exception(cls.loc_msg1)
        if not keys:
            return dic
        _dic: TyAny = dic
        if not isinstance(keys, (list, tuple)):
            keys = [keys]
        for _key in keys:
            if isinstance(_dic, dict):
                _dic_new = _dic.get(_key)
                if _dic_new is None:
                    raise Exception(cls.loc_msg3.format(_key, _dic, dic))
                _dic = _dic_new
            else:
                raise Exception(cls.loc_msg4.format(_dic, dic))
        return _dic

    @classmethod
    def locate_secondlast(cls, dic: TyDic, keys: TyKeys) -> Any:
        """
        locate the value by keys in a nested dictionary
        """
        return cls.locate(dic, keys[:-1])

    """
    New Methods
    """
    @classmethod
    def new(cls, keys: TyKeys, value: Any) -> TnDic:
        """ create a new Dictionary from keys and value
        """
        if value is None or keys is None:
            return None
        _dic_new: TyDic = {}
        if isinstance(keys, str):
            _dic_new[keys] = value
            return _dic_new
        cls.set_by_keys(_dic_new, keys, value)
        return _dic_new

    @staticmethod
    def new_normalize_values(dic: TyDic) -> TyDic:
        # def normalize_values(dic: TyDic) -> TyDic:
        """
        Replace every Dictionary value by the first list element
        of the value if it is a list with only one element.
        """
        # def normalize_value(dic: TyDic) -> TyDic:
        _dic_new: TyDic = {}
        for _k, _v in dic.items():
            # The value is a list with 1 element
            if isinstance(_v, list) and len(_v) == 1:
                _dic_new[_k] = _v[0]
            else:
                _dic_new[_k] = _v
        return _dic_new

    @staticmethod
    def new_by_fset_split_keys(dic: TyDic) -> TyToDD:
        # def sh_d_vals_d_cols(dic: TyDic) -> TyToDD:
        """
        Create new dictionary from old by creating the new keys as frozenset
        of the split of the old keys with comma as separator.
        """
        _d_cols: TyDic = {}
        _d_vals: TyDic = {}
        for _k, _v in dic.items():
            _a_k = _k.split("_")
            if len(_a_k) == 1:
                _k0 = _a_k[0]
                _d_vals[_k0] = _v
            else:
                _k0 = _a_k[0]
                _k1 = _a_k[1]
                if _k1 not in _d_cols:
                    _d_cols[_k1] = {}
                _d_cols[_k1][_k0] = _v
        return _d_vals, _d_cols

    @staticmethod
    def new_by_split_keys(dic: TyDic) -> TyDic:
        # def sh_dic(dic: TyDic) -> TyDic:
        """
        Create new nested dictionary from old by creating the new keys
        as the comma separator split of the old keys.
        """
        _dic_new = {}
        for _k, _v in dic.items():
            _frozenset_k = frozenset(_k.split(','))
            _dic_new[_frozenset_k] = _v
        return _dic_new

    @staticmethod
    def new_make_values2keys(dic: TyDic) -> TyDic:
        # def sh_value2keys(dic: TyDic) -> TyDic:
        _dic_new: TyDic = {}
        for _k, _v in dic.items():
            _k_new = _v
            _v_new = _k
            if _k_new not in _dic_new:
                _dic_new[_k_new] = []
            if _v_new not in _dic_new[_k_new]:
                _dic_new[_k_new].extend(_v_new)
        return _dic_new

    @staticmethod
    def new_prefix_keys(dic: TyDic, prefix: str) -> TyDic:
        # def sh_prefixed(dic: TyDic, prefix: str) -> TyDic:
        """
        Create new dictionary from old by using prefixed old keys as
        new keys and old values as new values.
        """
        _dic_new: TyDic = {}
        for _k, _v in dic.items():
            _key_new = f"{prefix}_{_k}"
            _dic_new[_key_new] = _v
        return _dic_new

    @staticmethod
    def new_rename_key(dic: TyDic, k_old: TyAny, k_new: TyAny) -> TyDic:
        # def rename_key(dic: TyDic, k_old: TyAny, k_new: TyAny) -> TyDic:
        """ rename old dictionary key with new dictionary key
        """
        _dic_new: TyDic = {k_new if k == k_old else k: v for k, v in dic.items()}
        return _dic_new

    @staticmethod
    def new_replace_string_in_keys(dic: TyDic, old: Any, new: Any) -> TyDic:
        # def replace_string_in_keys(
        # def replace_keys(
        if not dic:
            return dic
        _dic_new = {}
        for _k, _v in dic.items():
            _k_new = _k.replace(old, new)
            _dic_new[_k_new] = _v
        return _dic_new

    @staticmethod
    def new_round_values(dic: TyDic, keys: TnKeys, kwargs: TyDic) -> TyDic:
        # def round_values(
        # def round_value
        round_digits: int = kwargs.get('round_digits', 2)
        if not dic:
            msg = f"Parameter dic = {dic} is undefined"
            raise Exception(msg)
        if not keys:
            return dic
        _dic_new: TyDic = {}
        for _k, _v in dic.items():
            if _v is None:
                _dic_new[_k] = _v
            else:
                if _k in keys:
                    _dic_new[_k] = round(_v, round_digits)
                else:
                    _dic_new[_k] = _v
        return _dic_new

    """
    Set Methods
    """
    @classmethod
    def set_by_keys(cls, dic: TyDic, keys: TyKeys, value: Any) -> None:
        """
        Locate the values in a nested dictionary for the suceeding keys of
        a key array and replace the last value with the given value.
        """
        _dic = cls.locate_secondlast(dic, keys)
        cls.set_by_key(_dic, keys[-1], value)

    @staticmethod
    def set_by_key(dic: TyDic, key: TyKey, value: TnAny) -> None:
        """
        Locate the values in a nested dictionary for the suceeding keys of
        a key array and replace the last value with the given value.
        """
        if not dic:
            return
        if not key:
            return
        dic[key] = value

    @staticmethod
    def set_by_key_pair(dic: TyDic, src_key: Any, tgt_key: Any) -> None:
        """
        Replace value of source key by value of target key.
        """
        if src_key in dic and tgt_key in dic:
            dic[tgt_key] = dic[src_key]

    @staticmethod
    def set_by_div(dic: TnDic, key: str, key1: str, key2: str) -> None:
        """
        Replace the source key value by the division of the values of two
        target keys if they are of type float and the divisor is not 0.
        """
        # Dictionary is None or empty
        if not dic:
            return
        if key1 in dic and key2 in dic:
            _val1 = dic[key1]
            _val2 = dic[key2]
            if (isinstance(_val1, (int, float)) and
               isinstance(_val2, (int, float)) and
               _val2 != 0):
                dic[key] = _val1/_val2
            else:
                dic[key] = None
        else:
            dic[key] = None

    @staticmethod
    def set_format_value(dic: TnDic, key: Any, fmt: Any) -> None:
        """
        Replace the dictionary values by the formatted values by the given
        format string
        """
        if not dic:
            return
        if key in dic:
            value = dic[key]
            dic[key] = fmt.format(value)

    @staticmethod
    def set_multiply_with_factor(
            dic: TnDic, key_new: Any, key: Any, factor: Any) -> None:
        """
        Replace the dictionary values by the original value multiplied with the factor
        """
        # Dictionary is None or empty
        if not dic:
            return
        if key not in dic:
            return
        if dic[key] is None:
            dic[key_new] = None
        else:
            dic[key_new] = dic[key] * factor

    """
    Show Methods
    """
    @classmethod
    def sh_bool(cls, dic: TyDic, keys: TyKeys, switch: bool = False) -> bool:
        """
        locate the value by keys in a nested dictionary
        """
        value = cls.locate(dic, keys)
        if value is None:
            return switch
        if isinstance(value, bool):
            return value
        return switch

    @staticmethod
    def sh_keys(dic: TyDic, keys: TyKeys) -> TyArr:
        """
        show array of keys of key list found in dictionary.
        """
        if not dic or not keys:
            return []
        if not isinstance(keys, (list, tuple)):
            keys = [keys]
        _arr = []
        for _k in keys:
            if _k in dic:
                _arr.append(_k)
        return _arr

    @staticmethod
    def show_sorted_keys(dic: TnDic) -> TyArr:
        """
        show sorted array of keys of dictionary.
        """
        if not dic:
            return []
        a_key: TyArr = list(dic.keys())
        a_key.sort()
        return a_key

    @staticmethod
    def sh_value_by_keys(dic: TyDic, keys: TyKeys, default: Any = None) -> Any:
        """
        """
        # def sh_value(dic: TyDic, keys: TyKeys, default: Any = None) -> Any:
        if not dic:
            return dic
        if not keys:
            return dic
        if not isinstance(keys, (list, tuple)):
            keys = [keys]
        _dic = dic
        _value = None
        for _key in keys:
            _value = _dic.get(_key)
            if _value is None:
                return default
            if isinstance(_value, dict):
                _dic = _value
            else:
                if _value is None:
                    return default
                return _value
        return _value

    @staticmethod
    def sh_values_by_keys(dic: TyDic, keys: TyKeys) -> TyArr:
        # def sh_values_by_keys(dic: TyDic, keys: TyKeys) -> TyArr:
        """ locate the value for keys in a nested dictionary
        """
        # def sh_values
        if not dic or not keys:
            return []
        if not isinstance(keys, (list, tuple)):
            keys = [keys]
        _arr = []
        for _k in keys:
            if _k in dic:
                _arr.append(dic[_k])
        return _arr

    """
    Split Methods
    """
    @staticmethod
    def split_by_key(dic: TnDic, key: TnAny) -> TyTup:
        # Dictionary is None or empty
        if not dic or not key:
            return dic, None
        _dic_new = {}
        _obj_new = None
        for _k, _v in dic.items():
            if _k == key:
                _obj_new = _v
            else:
                _dic_new[_k] = _v
        return _obj_new, _dic_new

    @staticmethod
    def split_by_value(dic: TyDic, value: Any) -> TyTup:
        # Dictionary is None or empty
        if not dic:
            return dic, dic
        _dic0 = {}
        _dic1 = {}
        for _k, _v in dic.items():
            if _v == value:
                _dic0[_k] = _v
            else:
                _dic1[_k] = _v
        return _dic0, _dic1

    @staticmethod
    def split_by_value_endswith(dic: TyDic, value: Any) -> TyTup:
        # Dictionary is None or empty
        if not dic:
            return dic, dic
        _dic0 = {}
        _dic1 = {}
        for _k, _v in dic.items():
            if _v.endswith(value):
                _dic0[_k] = _v
            else:
                _dic1[_k] = _v
        return _dic0, _dic1

    @staticmethod
    def split_by_value_is_int(dic: TyDic) -> TyTup:
        # Dictionary is None or empty
        if not dic:
            return dic, dic
        _dic0 = {}
        _dic1 = {}
        for _k, _v in dic.items():
            if _v.isdigit():
                _dic0[_k] = _v
            else:
                _dic1[_k] = _v
        return _dic0, _dic1
