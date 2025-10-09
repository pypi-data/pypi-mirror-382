# coding=utf-8

import datetime
import os
import string

from ut_ioc.csv import Csv
from ut_ioc.json_ import Json
from ut_ioc.toml_ import Toml
from ut_ioc.txt_ import Txt
from ut_ioc.yaml_ import Yaml_
from ut_ioc.py_ import Py
# from ut_app.ka_xlsx import Workbook

from typing import Any
TyArr = list[Any]
TyAoA = list[TyArr]
TyAoAoA = list[TyAoA]
TyBool = bool
TyDic = dict[Any, Any]
TyDoA = dict[Any, TyArr]
TyInt = int
TyPath = str
TyStr = str

TnStr = None | TyStr
TnPath = None | TyPath


class Arr:
    """ io for Array
    """
    @staticmethod
    def write(arr: TyArr, path: TyStr) -> None:
        with open(path, 'wt') as fd:
            string = '\n'.join(arr)
            fd.write(string)


class XmlStr:
    """ io for Xml String
    """
    @staticmethod
    def write(xmlstr: TyStr, path: TyStr) -> None:
        with open(path, 'w') as fd:
            fd.write(xmlstr)


class Dic:
    """ io for Dictionary
    """
    class Txt:
        @staticmethod
        def write(dic: TyDic, path: TyPath, indent: TyInt = 2) -> None:
            Txt.write(dic, path, indent=indent)

    class Json:
        @staticmethod
        def write(dic: TyDic, path: TyPath, indent: TyInt = 2) -> None:
            Json.write(dic, path, indent=indent)

    class Yaml:
        @staticmethod
        def write(path: TyPath, dic: TyDic) -> None:
            Yaml_.write(path, dic)


class ObjType:
    """ Manage I/O for Object
    """
    @staticmethod
    def sh_obj_type_short(obj_type: TyStr, **kwargs) -> TnStr:
        _obj_types = kwargs.get('obj_types')
        if _obj_types is None:
            return obj_type
        if obj_type in _obj_types:
            _obj_type: TyStr = _obj_types[obj_type]
            return _obj_type
        return obj_type

    @classmethod
    def sh_sw_out(cls, obj_type: TyStr, file_format: TyStr, **kwargs) -> TyBool:
        sw_out: TyBool = kwargs.get(f"sw_out_{obj_type}_{file_format}", False)
        if sw_out:
            return sw_out

        sw_out = kwargs.get(f"sw_out_{file_format}", False)
        if sw_out:
            return sw_out

        sw_out = kwargs.get("sw_out", False)
        if sw_out:
            return sw_out

        obj_type_short = cls.sh_obj_type_short(obj_type, **kwargs)
        if obj_type_short is None:
            return False
        sw_out = kwargs.get(f"sw_out_{obj_type_short}_{file_format}", False)
        return sw_out

    @classmethod
    def sh_dir_out(cls, obj_type: TyStr, **kwargs) -> TnPath:
        _obj_type_short: TnStr = cls.sh_obj_type_short(obj_type, **kwargs)
        if _obj_type_short is not None:
            _dir_out: TnPath = kwargs.get(f"dir_out_{_obj_type_short}", None)
            if _dir_out is not None:
                return _dir_out
        _dir_out = kwargs.get(f"dir_out_{obj_type}", None)
        if _dir_out is not None:
            return _dir_out
        _dir_out = kwargs.get("dir_out")
        return _dir_out

    @classmethod
    def sh_path_out(cls, obj_type: TyStr, **kwargs) -> TnPath:
        _path_out: TnPath = kwargs.get('path_out', None)
        if _path_out is not None:
            return _path_out
        _path_out = kwargs.get(f'path_out_{obj_type}', None)
        if _path_out is not None:
            return _path_out
        obj_type_short: TnStr = cls.sh_obj_type_short(obj_type, **kwargs)
        if obj_type_short is not None:
            _path_out = kwargs.get(f'path_out_{obj_type_short}')
        return _path_out

    @classmethod
    def sh_path_out_by_dir(
            cls, obj_type: TyStr, file_format: TyStr, **kwargs) -> TyStr:
        dir_out = cls.sh_dir_out(obj_type, **kwargs)
        file = kwargs.get('file')
        _file = f"{file}.{file_format}"
        if dir_out is None:
            return _file
        return os.path.join(dir_out, _file)

    @classmethod
    def sh_dic_substitute(
            cls, obj_type: TyStr, file_format: TyStr, **kwargs) -> TyDic:
        file = kwargs.get('file')
        dic = {}
        if file is None:
            dic['file'] = ""
        elif file != "":
            dic['file'] = f"{file}."
        if obj_type is not None:
            dic['obj_type'] = f"{obj_type}."

        obj_type_short = cls.sh_obj_type_short(obj_type, **kwargs)
        if obj_type_short is not None:
            dic['obj_type_short'] = obj_type_short
        if file_format is not None:
            dic['file_format'] = file_format

        sw_today = cls.sh_sw_out(obj_type, 'today', **kwargs)
        if sw_today:
            dic['today'] = f'.{datetime.date.today().strftime("%Y%m%d")}'
        else:
            dic['today'] = ''
        return dic

    @classmethod
    def get_path_out(
            cls, obj_type: TyStr, file_format: TyStr, **kwargs) -> TnStr:
        _path_out: TnPath = cls.sh_path_out(obj_type, **kwargs)
        if _path_out is None:
            _path_out = cls.sh_path_out_by_dir(obj_type, file_format, **kwargs)
        if _path_out is None:
            return None
        dic_substitute = cls.sh_dic_substitute(obj_type, file_format, **kwargs)
        path_out_template = string.Template(_path_out)
        _path_out = path_out_template.safe_substitute(dic_substitute)
        return _path_out


class Obj:

    Format2Obj = {
        "csv": Csv.write_from_aod,
        "yaml": Yaml_.write,
        "json": Json.write,
        "toml": Toml.write,
        "py": Py.write}

    @classmethod
    def write_format(
            cls, obj, obj_type: TyStr, file_format: TyStr, **kwargs) -> None:
        sw_out = ObjType.sh_sw_out(obj_type, file_format, **kwargs)
        if not sw_out:
            return
        ioc = cls.Format2Obj[file_format]
        path_out = ObjType.get_path_out(obj_type, file_format, **kwargs)
        ioc(obj, path_out)

    @classmethod
    def write(cls, obj, obj_type: TyStr, **kwargs) -> None:
        for file_format in cls.Format2Obj.keys():
            cls.write_format(obj, obj_type, file_format, **kwargs)

    @classmethod
    def write_dic(cls, dic: TyDic, obj_typ: TyStr, **kwargs) -> None:
        if kwargs is None:
            kwargs = {}
        kwargs['file'] = dic['file']
        cls.write(dic[obj_typ], obj_typ, **kwargs)


# class Xlsx:
#
#     @staticmethod
#     def read_sheet_names(path: TyStr):
#         return Workbook.read_sheet_names(path)
#
#     @staticmethod
#     def read_sheet_2_dic(path: TyStr, **kwargs) -> TyDic:
#         sheet_id = kwargs.get("sheet_id")
#         return Workbook.read_sheet_2_dic(path, sheet_id)
#
#     @staticmethod
#     def read_sheet_2_arr(path: TyStr, **kwargs) -> TyArr:
#         sheet_id = kwargs.get("sheet_id")
#         return Workbook.read_sheet_2_arr(path, sheet_id)
#
#     @staticmethod
#     def read_sheets_2_aoa(path: TyStr, **kwargs) -> TyAoA:
#         sheet_ids = kwargs.get("sheet_ids")
#         return Workbook.read_sheets_2_aoa(path, sheet_ids)
#
#     @staticmethod
#     def read_sheets_2_doa(path: TyStr, **kwargs) -> TyDoA:
#         sheet_ids = kwargs.get("sheet_ids")
#         return Workbook.read_sheets_2_doa(path, sheet_ids)
#
#     @staticmethod
#     def read_workbooks_sheets_2_ao_aoa(path: TyStr, **kwargs) -> TyAoA:
#         sheet_ids = kwargs.get("sheet_ids")
#         return Workbook.read_workbook_sheets_2_aoa(
#             path, sheet_ids=sheet_ids)
