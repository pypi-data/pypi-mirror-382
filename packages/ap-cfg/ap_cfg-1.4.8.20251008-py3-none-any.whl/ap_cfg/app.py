import sys

import ut_com.dec as dec
from ut_com.com import Com
from ut_cli.task import Task

from ap_cfg.parms import Parms as CfgParms
from ap_cfg.task import Task as CfgTask

from typing import Any

TyDic = dict[Any, Any]
TyTup = tuple[Any, Any]
TyDoT = tuple[TyTup, TyTup]


class App:

    t_parms_task: TyTup = (CfgParms, CfgTask)

    @classmethod
    @dec.handle_error
    @dec.timer
    def do(cls) -> None:
        Task.do(Com.sh_kwargs(cls, sys.argv))


if __name__ == "__main__":
    App.do()
