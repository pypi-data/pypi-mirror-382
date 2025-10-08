"""
This module provides task input output control classes for the management of Sustainability Risk Rating (SRR) processing.
"""

# import pandas as pd
import openpyxl as op

from ut_eco.taskin import TaskIn
from ut_eco.taskout import TaskOut
from ut_eco.xls.utils import EvexIoc

from typing import Any, TypeAlias

TyOpWb: TypeAlias = op.Workbook

TyArr = list[Any]
TyBool = bool
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyCmd = str
TyPath = str
TyStr = str

TnAoD = None | TyAoD
TnDic = None | TyDic
TnOpWb = None | TyOpWb


class TaskIoc:
    """
    I/O Control Tasks class for EcoVadis IQ upload Excel workbooks
    """
    @classmethod
    def evupadm(cls, kwargs: TyDic) -> None:
        """
        Administration processsing for EcoVadis IQ upload Excel workbooks
        """
        TaskOut.evupadm(TaskIn.evupadm(EvexIoc, kwargs), kwargs)

    @classmethod
    def evupdel(cls, kwargs: TyDic) -> None:
        """
        Delete processsing for EcoVadis IQ upload Excel workbooks
        """
        TaskOut.evupdel(TaskIn.evupdel(EvexIoc, kwargs), kwargs)

    @classmethod
    def evupreg(cls, kwargs: TyDic) -> None:
        """
        Regular processsing for EcoVadis IQ upload Excel workbooks
        Regular Processing (create, update, delete) of partners using
          single Xlsx Workbook with a populated admin- or delete-sheet
          two xlsx Workbooks:
            the first one contains a populated admin-sheet
            the second one contains a populated delete-sheet
        """
        _sw_single_wb: TyBool = kwargs.get('sw_single_wb', True)
        if _sw_single_wb:
            # write single workbook which contains admin and delete worksheets
            TaskOut.evupreg_reg_wb(TaskIn.evupreg(EvexIoc, kwargs), kwargs)
        else:
            # write separate workbooks for admin and delete worksheets
            TaskOut.evupreg_adm_del_wb(TaskIn.evupreg(EvexIoc, kwargs), kwargs)

    @classmethod
    def evdomap(cls, kwargs: TyDic) -> None:
        """
        EcoVadis Download Processing: Mapping of EcoVadis export xlsx workbook
        """
        TaskOut.evdomap(TaskIn.evdomap(EvexIoc, kwargs), kwargs)
