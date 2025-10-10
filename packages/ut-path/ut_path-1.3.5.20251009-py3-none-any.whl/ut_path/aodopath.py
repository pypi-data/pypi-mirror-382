# coding=utf-8

from ut_log.log import LogEq
from ut_path.path import Path

from typing import Any

TyDic = dict[Any, Any]
TyPath = str
TyDoPath = dict[Any, TyPath]
TyAoDoPath = list[TyDoPath]


class AoDoPath:

    @staticmethod
    def resolve_path(aodopath: TyAoDoPath, kwargs: TyDic) -> TyAoDoPath:
        _aodopath_new: TyAoDoPath = []
        for _dopath in aodopath:
            _dopath_new: TyDoPath = {}
            for _key, _path in _dopath.items():
                LogEq.debug("_path", _path)
                _dopath_new[_key] = Path.resolve_var(_path, kwargs)
            _aodopath_new.append(_dopath_new)
        return _aodopath_new
