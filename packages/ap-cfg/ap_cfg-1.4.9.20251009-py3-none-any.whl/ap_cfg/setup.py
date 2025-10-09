from typing import Any

import os
import shutil

from ut_log.log import Log, LogEq
from ut_path.path import Path
from ut_dic.dic import Dic
from ut_ioc.yaml_ import Yaml_

TyAny = Any
TyDic = dict[Any, Any]
TyAoD = list[TyDic]
TyPath = str
TyStr = str

TnAny = None | TyAny
TnDic = None | TyDic
TnAoD = None | TyAoD
TnPath = None | TyPath
TyToPath = tuple[TnPath, TnPath]
TyAoToPath = list[TyToPath]


class Setup:
    """
    Setup function class
    """
    @staticmethod
    def copytree(d_copy: TyDic) -> None:
        """
        Copy source path tree to destination path tree while preserving timestamps,
        and allow existing destination.
        """
        src = Dic.locate_key(d_copy, 'src')
        dst = Dic.locate_key(d_copy, 'dst')
        if not src:
            msg = f"source path `{src}` is undefined or empty"
            Log.error(msg)
            return
        if not dst:
            msg = f"destination path `{dst}` is undefined or empty"
            Log.error(msg)
            return
        if not os.path.exists(dst):
            os.makedirs(dst)
        # Copy the entire directory tree
        try:
            shutil.copytree(
                    src, dst, copy_function=shutil.copy2, dirs_exist_ok=True)
            _msg = f"Directory tree copied from {src} to {dst}"
            Log.debug(_msg)
        except Exception as e:
            _msg = f"Could not copy Directory tree from {src} to {dst}"
            raise Exception(_msg) from e

    @staticmethod
    def get_aod_copy(kwargs: TyDic) -> TyAoD:
        _aod_copy: TnAoD = kwargs.get('aod_copy')
        LogEq.debug("_aod_copy", _aod_copy)
        if _aod_copy is not None:
            return _aod_copy

        _in_path_copy: TnPath = kwargs.get('in_path_copy')
        _path: TnPath = Path.sh_path_by_tpl_pac_sep(_in_path_copy, kwargs)
        _aod_copy_new: Any | TyAoD = Yaml_.read_with_safeloader(_path)
        if not _aod_copy_new:
            _msg = f"Content of yaml file={_path} is undefined or empty"
            raise Exception(_msg)
        return _aod_copy_new

    @classmethod
    def setup(cls, kwargs: TyDic) -> None:
        _aod_copy: TyAoD = cls.get_aod_copy(kwargs)
        LogEq.debug("_aod_copy", _aod_copy)
        for _d_path in _aod_copy:
            cls.copytree(_d_path)
