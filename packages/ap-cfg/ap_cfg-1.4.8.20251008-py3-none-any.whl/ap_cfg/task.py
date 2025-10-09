from typing import Any

from ut_dic.doc import DoC
from ap_cfg.doc import doc

TyDic = dict[Any, Any]


class Task:
    """
    General Task class
    """
    @classmethod
    def do(cls, kwargs: TyDic) -> None:
        """
        Select the task method from the task command table for the given
        command (value of 'cmd' in kwargs) and execute the selected method.
        """
        DoC.ex_cmd(doc, kwargs)
