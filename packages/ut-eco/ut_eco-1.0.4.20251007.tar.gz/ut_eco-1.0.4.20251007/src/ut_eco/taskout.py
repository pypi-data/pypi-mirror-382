"""
This module provides task scheduling classes for the management of OmniTracker
SRR (NHRR) processing for Department UMH.
    SRR: Sustainability Risk Rating
    NHRR: Nachhaltigkeits Risiko Rating
"""
import openpyxl as op

from ut_xls.op.ioopathnmwb import IooPathnmWb as OpIooPathnmWb
from ut_xls.pe.ioopathnmwb import IooPathnmWb as PeIooPathnmWb

from ut_eco.cfg import Cfg
from ut_eco.taskin import TaskTmpIn

from typing import Any
TyOpWb = op.workbook.workbook.Workbook

TyArr = list[Any]
TyBool = bool
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoAoA = dict[Any, TyAoA]
TyDoAoD = dict[Any, TyAoD]
TyCmd = str
TyPath = str
TyStr = str

TnAoD = None | TyAoD
TnDic = None | TyDic
TnOpWb = None | TyOpWb
TnPath = None | TyPath


class TaskOut:

    @classmethod
    def evupadm(cls, tup_adm: tuple[TnAoD, TyDoAoD], kwargs: TyDic) -> None:
        """
        Administration processsing for evup xlsx workbooks
        """
        _aod_evup_adm, _doaod_evin_adm_vfy = tup_adm
        _wb: TnOpWb = TaskTmpIn.evupadm(_aod_evup_adm, kwargs)
        OpIooPathnmWb.write(_wb, Cfg.OutPathnm.evup_adm, kwargs)
        PeIooPathnmWb.write_wb_from_doaod(
                _doaod_evin_adm_vfy, Cfg.OutPathnm.evin_adm_vfy, kwargs)

    @classmethod
    def evupdel(cls, tup_del: tuple[TnAoD, TyDoAoD], kwargs: TyDic) -> None:
        """
        Delete processsing for evup xlsx workbooks
        """
        _aod_evup_del, _doaod_evin_del_vfy = tup_del
        _wb: TnOpWb = TaskTmpIn.evupdel(_aod_evup_del, kwargs)
        OpIooPathnmWb.write(_wb, Cfg.OutPathnm.evup_del, kwargs)
        PeIooPathnmWb.write_wb_from_doaod(
                _doaod_evin_del_vfy, Cfg.OutPathnm.evin_del_vfy, kwargs)

    @classmethod
    def evupreg_reg_wb(
            cls, tup_adm_del: tuple[TnAoD, TyDoAoD, TnAoD, TyDoAoD], kwargs: TyDic
    ) -> None:
        """
        EcoVadus Upload Processing:
        Regular Processing (create, update, delete) of partners using
        one Xlsx Workbook with a populated admin- or delete-sheet
        """
        _aod_evup_adm: TnAoD
        _doaod_evin_adm_vfy: TyDoAoD
        _aod_evup_del: TnAoD
        _doaod_evin_del_vfy: TyDoAoD
        _aod_evup_adm, _doaod_evin_adm_vfy, _aod_evup_del, _doaod_evin_del_vfy = tup_adm_del
        _wb: TnOpWb = TaskTmpIn.evupreg(_aod_evup_adm, _aod_evup_del, kwargs)
        OpIooPathnmWb.write(_wb, Cfg.OutPathnm.evup_reg, kwargs)
        _doaod: TyDoAoD = _doaod_evin_adm_vfy | _doaod_evin_del_vfy
        PeIooPathnmWb.write_wb_from_doaod(_doaod, Cfg.OutPathnm.evin_reg_vfy, kwargs)

    @classmethod
    def evupreg_adm_del_wb(
            cls, tup_adm_del: tuple[TnAoD, TyDoAoD, TnAoD, TyDoAoD], kwargs: TyDic
    ) -> None:
        """
        EcoVadus Upload Processing:
        Regular Processing (create, update, delete) of partners using
        two xlsx Workbooks:
          the first one contains a populated admin-sheet
          the second one contains a populated delete-sheet
        """
        _aod_evup_adm: TnAoD
        _doaod_evin_adm_vfy: TyDoAoD
        _aod_evup_del: TnAoD
        _doaod_evin_del_vfy: TyDoAoD
        _aod_evup_adm, _doaod_evin_adm_vfy, _aod_evup_del, _doaod_evin_del_vfy = tup_adm_del
        _wb: TnOpWb = TaskTmpIn.evupadm(_aod_evup_adm, kwargs)
        OpIooPathnmWb.write(_wb, Cfg.OutPathnm.evup_adm, kwargs)
        _wb = TaskTmpIn.evupdel(_aod_evup_del, kwargs)
        OpIooPathnmWb.write(_wb, Cfg.OutPathnm.evup_del, kwargs)
        _doaod: TyDoAoD = _doaod_evin_adm_vfy | _doaod_evin_del_vfy
        PeIooPathnmWb.write_wb_from_doaod(_doaod, Cfg.OutPathnm.evin_reg_vfy, kwargs)

    @classmethod
    def evdomap(cls, aod_evex: TyAoD, kwargs: TyDic) -> None:
        """
        EcoVadus Download Processing: Mapping of EcoVadis export xlsx workbook
        """
        PeIooPathnmWb.write_wb_from_aod(
                aod_evex, Cfg.OutPathnm.evex, Cfg.sheet_exp, kwargs)

    @classmethod
    def evdoexp(cls, tup_adm: tuple[TnAoD, TyDoAoD], kwargs: TyDic) -> None:
        """
        Administration processsing for evup xlsx workbooks
        """
        _aod_evup_adm, _doaod_evin_adm_vfy = tup_adm
        _wb: TnOpWb = TaskTmpIn.evupadm(_aod_evup_adm, kwargs)
        OpIooPathnmWb.write(_wb, Cfg.OutPathnm.evup_adm, kwargs)
        PeIooPathnmWb.write_wb_from_doaod(
                _doaod_evin_adm_vfy, Cfg.OutPathnm.evin_adm_vfy, kwargs)
