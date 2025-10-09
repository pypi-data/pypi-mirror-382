# coding=utf-8
import orjson
import ujson
import json

from ut_dic.dic import Dic

from typing import Any, Callable

TyCallable = Callable[..., Any]
TyDoC = dict[Any, TyCallable]
TyDic = dict[Any, Any]
TyAoD = list[TyDic]
TyPath = str
TyStr = str

TnAny = None | Any
TnStr = None | str


class Json:

    type2loads: TyDoC = {
        'orjson': orjson.loads,
        'ujson': ujson.loads,
        'json': json.loads}

    type2dumps: TyDoC = {
        'orjson': orjson.dumps,
        'ujson': ujson.dumps,
        'json': json.dumps}

    type2dump: TyDoC = {
        'orjson': json.dump,
        'ujson': json.dump,
        'json': json.dump}

    @classmethod
    def dumps(cls, obj: Any, **kwargs: Any) -> TyStr:
        json_type = kwargs.get('json_type', 'orjson')
        indent = kwargs.get('indent')
        dumps: TyCallable = Dic.locate(cls.type2dumps, json_type)
        _json_str: TyStr = dumps(obj, indent=indent)
        return _json_str

    @classmethod
    def dump(cls, obj: Any, fd, **kwargs) -> None:
        json_type = kwargs.get('json_type', 'orjson')
        dump: TyCallable = Dic.locate(cls.type2dump, json_type)
        indent = kwargs.get('indent', 2)
        sort_keys = kwargs.get('sort_keys', False)
        ensure_ascii = kwargs.get('ensure_ascii', False)
        dump(
            obj, fd,
            indent=indent,
            sort_keys=sort_keys,
            ensure_ascii=ensure_ascii)

    @classmethod
    def loads(cls, json_str: TyStr, **kwargs) -> Any:
        json_type = kwargs.get('json_type', 'orjson')
        _loads: TyCallable = Dic.locate(cls.type2loads, json_type)
        _obj = _loads(json_str)
        return _obj

    @classmethod
    def read(cls, path_file: TyPath, **kwargs) -> TnAny:
        mode = kwargs.get('mode', 'rb')
        with open(path_file, mode) as fd:
            _json_str: TyStr = fd.read()
            _obj: Any = cls.loads(_json_str, **kwargs)
            return _obj
        return None

    @classmethod
    def write(cls, obj, path: TyPath, **kwargs) -> None:
        if obj is None:
            return
        json_type = kwargs.get('json', 'orjson')
        dump: TyCallable = Dic.locate(cls.type2dump, json_type)
        with open(path, 'w') as fd:
            dump(obj, fd, **kwargs)
