# coding=utf-8
# from collections.abc import Callable
from typing import Any

import os
import yaml
import jinja2

TyAny = Any
TyDic = dict[Any, Any]
TyPath = str
TyStr = str
TyJinja2Env = jinja2.environment.Environment
TyJinja2Tmpl = jinja2.environment.Template

TnDic = None | TyDic
TnStr = None | TyStr


class Jinja2_:
    """
    Manage Object to Json file affilitation
    """
    @staticmethod
    def read_template(path: TyPath) -> TyJinja2Tmpl:
        directory, file = os.path.split(path)
        env: TyJinja2Env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(directory))
        _tmpl: TyJinja2Tmpl = env.get_template(file)
        return _tmpl

    @classmethod
    def read(cls, path: TyPath, **kwargs: Any) -> Any:
        try:
            # read jinja template from file
            template: TyJinja2Tmpl = cls.read_template(path)

            # render template as yaml string
            template_rendered: str = template.render(kwargs)

            # load yaml string into object
            _obj = yaml.safe_load(template_rendered)
            return _obj
        except IOError as exc:
            msg = f"Exception: {exc}\nNo such file or directory with path='{path}'"
            raise Exception(msg)
