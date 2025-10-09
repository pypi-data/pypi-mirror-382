# coding=utf-8
from typing import Any

import os
from ut_pac.pac import Pac

TyArr = list[Any]
TyDic = dict[Any, Any]
TyPackage = str
TyPath = str
TnPath = None | TyPath


class Cls:

    @staticmethod
    def sh_path_of_pac_by_path(cls_app, path: TyPath) -> Any:
        """
        show directory
        """
        _package = Pac.sh_pac_path(cls_app)
        return Pac.sh_path_by_path(_package, path)

    @staticmethod
    def sh_path_of_pac_by_paths(cls_app, *paths: TyPath) -> Any:
        """
        show directory
        """
        _package = Pac.sh_pac_path(cls_app)
        _path = os.sep.join(paths)
        return Pac.sh_path_by_path(_package, _path)
