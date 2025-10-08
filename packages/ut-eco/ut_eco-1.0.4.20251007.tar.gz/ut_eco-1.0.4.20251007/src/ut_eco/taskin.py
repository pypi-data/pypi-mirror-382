"""
This module provides task input classes for the management of
Sustainability Risk Rating (SRR) processing.
"""
import pandas as pd
import openpyxl as op

from ut_dfr.pddf import PdDf
from ut_xls.op.ioipathnmwb import IoiPathnmWb as OpIoiPathnmWb

from ut_eco.cfg import Cfg
from ut_eco.utils import Evin, Evex, Evup

from typing import Any
TyOpWb = op.workbook.workbook.Workbook
TyPdDf = pd.DataFrame

TyArr = list[Any]
TyBool = bool
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoAoA = dict[Any, TyAoA]
TyDoAoD = dict[Any, TyAoD]

TyPath = str
TyStr = str

TnAoD = None | TyAoD
TnDic = None | TyDic
TnPdDf = None | TyPdDf
TnOpWb = None | TyOpWb


class TaskTmpIn:

    @classmethod
    def evupadm(cls, aod: TnAoD, kwargs: TyDic) -> TnOpWb:
        """
        Administration processsing for evup xlsx workbooks
        """
        _wb: TnOpWb = OpIoiPathnmWb.sh_wb_adm(
                Cfg.InPathnm.evup_tmp, aod, Cfg.sheet_adm, kwargs)
        return _wb

    @classmethod
    def evupdel(cls, aod: TnAoD, kwargs: TyDic) -> TnOpWb:
        """
        Delete processsing for evup xlsx workbooks
        """
        _wb: TnOpWb = OpIoiPathnmWb.sh_wb_del(
                Cfg.InPathnm.evup_tmp, aod, Cfg.sheet_del, kwargs)
        return _wb

    @classmethod
    def evupreg(
            cls, aod_adm: TnAoD, aod_del: TnAoD, kwargs: TyDic
    ) -> TnOpWb:
        """
        EcoVadus Upload Processing:
        Regular Processing (create, update, delete) of partners using
        one Xlsx Workbook with a populated admin- or delete-sheet
        """
        _wb: TnOpWb = OpIoiPathnmWb.sh_wb_reg(
                Cfg.InPathnm.evup_tmp, aod_adm, aod_del,
                Cfg.sheet_adm, Cfg.sheet_del,  kwargs)
        return _wb


class TaskIn:

    @staticmethod
    def evupadm(EvexIoc, kwargs: TyDic) -> tuple[TnAoD, TyDoAoD]:
        """
        Administration processsing for evup
        """
        _aod: TnAoD = Evin.read_wb_adm_to_aod(kwargs)
        _df = EvexIoc.read_wb_exp_to_df(kwargs)
        _tup_adm: tuple[TnAoD, TyDoAoD] = Evup.sh_aod_evup_adm(_aod, _df, kwargs)
        return _tup_adm

    @staticmethod
    def evupdel(EvexIoc, kwargs: TyDic) -> tuple[TnAoD, TyDoAoD]:
        """
        Delete processsing for evup
        """
        _aod_evin_del: TnAoD = Evin.read_wb_del_to_aod(kwargs)
        _pddf_evin_adm: TnPdDf = Evin.read_wb_adm_to_df(kwargs)

        if Cfg.DoSwDel.use_evex:
            _pddf_evex: TnPdDf = EvexIoc.read_wb_exp_to_df(kwargs)
            _aod_evex: TnAoD = PdDf.to_aod(_pddf_evex)
            _tup_del: tuple[TnAoD, TyDoAoD] = Evup.sh_aod_evup_del_use_evex(
                    _aod_evin_del, _pddf_evin_adm, _aod_evex, _pddf_evex)
        else:
            _tup_del = Evup.sh_aod_evup_del(_aod_evin_del, _pddf_evin_adm)

        return _tup_del

    @staticmethod
    def evupreg(EvexIoc, kwargs: TyDic) -> tuple[TnAoD, TyDoAoD, TnAoD, TyDoAoD]:
        """
        Regular processsing for evup
        """
        _pddf_evin_adm: TnPdDf = Evin.read_wb_adm_to_df(kwargs)
        _aod_evin_adm: TnAoD = PdDf.to_aod(_pddf_evin_adm)
        _pddf_evex: TnPdDf = EvexIoc.read_wb_exp_to_df(kwargs)
        _tup_adm: tuple[TnAoD, TyDoAoD] = Evup.sh_aod_evup_adm(
                _aod_evin_adm, _pddf_evex, kwargs)

        _aod_evin_del: TnAoD = Evin.read_wb_del_to_aod(kwargs)

        if Cfg.DoSwDel.use_evex:
            _aod_evex: TnAoD = PdDf.to_aod(_pddf_evex)
            _tup_del: tuple[TnAoD, TyDoAoD] = Evup.sh_aod_evup_del_use_evex(
                _aod_evin_del, _pddf_evin_adm, _aod_evex, _pddf_evex)
        else:
            _tup_del = Evup.sh_aod_evup_del(_aod_evin_del, _pddf_evin_adm)

        return _tup_adm + _tup_del

    @staticmethod
    def evdomap(EvexIoc, kwargs: TyDic) -> TyAoD:
        """
        EcoVadus Download Processing: Mapping of EcoVadis export xlsx workbook
        """
        _d_ecv_iq2umh_iq = Cfg.Utils.d_ecv_iq2umh_iq
        _aod = EvexIoc.read_wb_exp_to_aod(kwargs)
        _aod_evex_new: TyAoD = Evex.map(_aod, _d_ecv_iq2umh_iq)
        return _aod_evex_new

    @staticmethod
    def evdoexp(EvexIoc, kwargs: TyDic) -> tuple[TyAoD, TyDoAoD]:
        """
        Administration processsing for evup
        """
        _aod: TnAoD = Evin.read_wb_adm_to_aod(kwargs)
        _df = EvexIoc.read_wb_exp_to_df(kwargs)
        _tup_adm: tuple[TyAoD, TyDoAoD] = Evup.sh_aod_evup_adm(_aod, _df, kwargs)
        return _tup_adm
