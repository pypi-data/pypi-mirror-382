from typing import Any

from ut_log.log import LogEq
from ut_path.path import Path

TyDic = dict[Any, Any]
TyPath = str
TyPathnm = str

TnDic = None | TyDic
TnPath = None | TyPath
TnPathnm = None | TyPathnm


class Pathnm:

    @staticmethod
    def sh_path(pathnm: TyPathnm, kwargs: TyDic) -> TyPath:
        _path: TnPath = kwargs.get(pathnm)
        LogEq.debug("_path", _path)
        _path_new: TnPath = Path.sh_path_by_tpl_and_d_pathnm2datetype(
                _path, pathnm, kwargs)
        if not _path_new:
            msg = f"Path for pathnm = {pathnm} is undefined"
            raise Exception(msg)
        LogEq.debug("_path_new", _path_new)
        return _path_new
