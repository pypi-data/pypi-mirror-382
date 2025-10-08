"""
This module provides utility classes for the management of OmniTracker
EcoVadis NHRR (Nachhaltigkeits Risiko Rating) processing for Department UMH
"""
from ut_eco.rst.taskioc import TaskIoc as RstTaskIoc
from ut_eco.xls.taskioc import TaskIoc as XlsTaskIoc

from typing import Any, Dict, Callable, Union
TyCallable = Callable[..., Any]
TyDnDoC = dict[Any, Union['TyDnDoC', Callable[..., Any]]]


# Deeply Nested Dictionary of Callables as last value
doc: TyDnDoC = {
    'srr': {
        'xls': {
            'evupadm': XlsTaskIoc.evupadm,
            'evupdel': XlsTaskIoc.evupdel,
            'evupreg': XlsTaskIoc.evupreg,
            'evdomap': XlsTaskIoc.evdomap,
        },
        'rst': {
            'evupadm': RstTaskIoc.evupadm,
            'evupdel': RstTaskIoc.evupdel,
            'evupreg': RstTaskIoc.evupreg,
            'evdoexp': RstTaskIoc.evdoexp,
            'evdomap': RstTaskIoc.evdomap,
        },
    },
}
