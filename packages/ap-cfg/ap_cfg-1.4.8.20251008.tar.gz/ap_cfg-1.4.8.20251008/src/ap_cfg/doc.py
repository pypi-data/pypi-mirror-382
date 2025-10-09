from ap_cfg.setup import Setup

from typing import Any, Callable
TyCallable = Callable[..., Any]
TyDnDoC = dict[Any, "TyDnDoC" | TyCallable]


# Deeply Nested Dictionary of Callables as last value
doc: TyDnDoC = {
    'setup': Setup.setup,
}
