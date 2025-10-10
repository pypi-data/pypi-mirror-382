# coding=utf-8
from typing import Any

import os

from ut_pac.pac import Pac

TyArr = list[Any]
TyDic = dict[Any, Any]
TyPac = str
TyPath = str
TyAoPac = str | list[str]
TyAoPath = list[TyPath]

TnPath = None | TyPath


class AoPac:

    @staticmethod
    def sh_path_by_path_exists(
            aopac: TyAoPac, path: TyPath) -> TnPath:
        """ show directory
        """
        if not isinstance(aopac, (list, tuple)):
            _aopac = [aopac]
        else:
            _aopac = aopac
        _aopath : TyAoPath = []
        for _pac in _aopac:
            _path: TyPath = Pac.sh_path_by_path(_pac, path)
            if os.path.exists(_path):
                return _path
            _aopath.append(_path)
        msg = f"No path in array _aopath={_aopath} exists"
        raise Exception(msg)

    @staticmethod
    def sh_path_by_path(
            aopac: TyAoPac, path: TyPath) -> TyAoPac:
        """ show directory
        """
        if not isinstance(aopac, list):
            _aopac = [aopac]
        else:
            _aopac = aopac
        _aopac_new = []
        for _pac in _aopac:
            _path = Pac.sh_path_by_path(_pac, path)
            _aopac_new.append(_path)
        return _aopac_new

    @classmethod
    def sh_path_by_path_and_prefix(
            cls, aopac: TyAoPac, path: TyPath, prefix: TyPath = '') -> TyAoPac:
        # def sh_path_by_packs(
        """ show directory
        """
        if prefix:
            _path = os.path.join(prefix, path)
            if os.path.exists(_path):
                return _path
        return cls.sh_path_by_path(aopac, path)
