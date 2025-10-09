# coding=utf-8

from typing import Any, List

TyArr = List[Any]


class Py:

    @staticmethod
    def write(obj, path):
        with open(path, 'w') as fd:
            for line in obj:
                fd.write(line)
