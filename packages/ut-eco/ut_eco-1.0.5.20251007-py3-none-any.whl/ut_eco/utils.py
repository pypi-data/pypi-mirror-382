"""
This module provides utilities classes for the management of Sustainability Risk Rating (SRR)
processing.
"""
from __future__ import annotations
from typing import Any, TypeAlias

import pandas as pd
import numpy as np

from ut_aod.aod import AoD
from ut_dic.dic import Dic
from ut_tod.tod import ToD
from ut_doa.doa import DoA
from ut_doa.doaod import DoAoD
from ut_dfr.pddf import PdDf
from ut_log.log import Log
from ut_xls.pd.ioipathnmwb import IoiPathnmWb as PdIoiPathnmWb

from ut_eco.cfg import Cfg
from ut_eco.verify import EvinVfyAdm, EvinVfyDel

TyPdDf: TypeAlias = pd.DataFrame

TyArr = list[Any]
TyAoStr = list[str]
TyBool = bool
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoAoA = dict[Any, TyAoA]
TyDoAoD = dict[Any, TyAoD]
TyDoB = dict[Any, bool]
TyAoD_DoAoD = TyAoD | TyDoAoD
TyPath = str
TyStr = str
TyTup = tuple[Any]
TyTask = Any
TyDoPdDf = dict[Any, TyPdDf]
TyPdDf_DoPdDf = TyPdDf | TyDoPdDf
TyToAoDDoAoD = tuple[TyAoD, TyDoAoD]

TnDic = None | TyDic
TnAoD = None | TyAoD
TnDoAoA = None | TyDoAoA
TnDoAoD = None | TyDoAoD
TnPdDf = None | TyPdDf
TnStr = None | str


class Evup:
    """
    EcoVadis Upload class
    """
    @classmethod
    def sh_aod_evup_adm(
            cls, aod_evin: TnAoD, pddf_evex: TnPdDf, kwargs: TyDic
    ) -> tuple[TyAoD, TyDoAoD]:
        _doaod_evup_adm = EvinEvex.join_adm(aod_evin, pddf_evex)
        if Cfg.DoSwAdm.use_evex:
            _keys = ['new', 'ch_y']
            _aod = DoAoD.union_distinct_by_keys(_doaod_evup_adm, _keys)
        else:
            _aod = DoAoD.union_distinct(_doaod_evup_adm)
        _aod, _doaod_vfy = EvinVfyAdm.vfy_aod_evin(_aod)
        return _aod, _doaod_vfy

    @staticmethod
    def sh_aod_evup_del_use_evex(
            aod_evin_del: TnAoD, pddf_evin_adm: TnPdDf,
            aod_evex: TnAoD, pddf_evex: TnPdDf
    ) -> tuple[TnAoD, TyDoAoD]:
        _aod_evin_del, _doaod_vfy = EvinVfyDel.vfy_aod_evin(aod_evin_del)
        _aod_evup_del0: TyAoD = EvexEvin.join_del(aod_evex, pddf_evin_adm)
        _aod_evup_del1: TyAoD = EvinEvex.join_del(_aod_evin_del, pddf_evex)

        _aod_evup_del: TnAoD = AoD.union_distinct(_aod_evup_del0, _aod_evup_del1)
        return _aod_evup_del, _doaod_vfy

    @staticmethod
    def sh_aod_evup_del(
            aod_evin_del: TnAoD, pddf_evin_adm: TnPdDf
    ) -> tuple[TyAoD, TyDoAoD]:
        _aod_evin_del, _doaod_vfy = EvinVfyDel.vfy_aod_evin(aod_evin_del)
        return _aod_evin_del, _doaod_vfy


class Evex:
    """
    EcoVadis Export class
    """
    msg = "Evex Dataframe: {F} contains multiple records: {R}"

    @classmethod
    def sh_d_evex(
            cls, df_evex: TnPdDf
    ) -> TyDic:
        if df_evex is None:
            return {}
        _df_evex = df_evex.replace(to_replace=np.nan, value=None, inplace=False)
        _aod = _df_evex.to_dict(orient='records')
        if len(_aod) == 1:
            d_evex: TyDic = _aod[0]
            return d_evex
        Log.error(cls.msg.format(F=df_evex, R=_aod))
        return {}

    @staticmethod
    def sh_d_evup_del_from_dic(d_evex: TnDic) -> TnDic:
        d_evup: TyDic = {}
        if d_evex is None:
            return d_evup
        _d_del_evup2evex = Cfg.Utils.d_del_evup2evex
        ToD.set_tgt_with_src_by_d_tgt2src(
                d_evup, d_evex, _d_del_evup2evex)
        return d_evup

    @classmethod
    def sh_d_evup_del_from_df(cls, df_evex_row: TyPdDf) -> TnDic:
        _d_evex: TnDic = cls.sh_d_evex(df_evex_row)
        return cls.sh_d_evup_del_from_dic(_d_evex)

    @staticmethod
    def map(aod_evex: TnAoD, d_map_evex: TyDic) -> TyAoD:
        aod_evex_new: TyAoD = []
        if not aod_evex:
            return aod_evex_new
        for dic in aod_evex:
            dic_new = {}
            for key, value in dic.items():
                dic_new[key] = d_map_evex.get(value, value)
            aod_evex_new.append(dic_new)
        return aod_evex_new


class Evin:
    """
    EcoVadis input data (from Systems like OmniTracker) class
    """
    @classmethod
    def read_wb_adm_to_df(cls, kwargs: TyDic) -> TnPdDf:
        _pddf: TnPdDf = PdIoiPathnmWb.read_wb_to_df(
                Cfg.InPathnm.evin, Cfg.sheet_adm, kwargs)
        return _pddf

    @classmethod
    def read_wb_adm_to_aod(cls, kwargs: TyDic) -> TnAoD:
        _aod: TnAoD = PdIoiPathnmWb.read_wb_to_aod(
                Cfg.InPathnm.evin, Cfg.sheet_adm, kwargs)
        return _aod

    @classmethod
    def read_wb_del_to_aod(cls, kwargs: TyDic) -> TnAoD:
        _aod: TnAoD = PdIoiPathnmWb.read_wb_to_aod(
                Cfg.InPathnm.evin, Cfg.sheet_del, kwargs)
        return _aod

    @staticmethod
    def sh_d_evup_adm(d_evin: TyDic) -> TyDic:
        _d_evup2const = Cfg.Utils.d_evup2const
        _d_evup2evin = Cfg.Utils.d_evup2evin
        d_evup: TyDic = {}
        ToD.set_tgt_with_src(d_evup, _d_evup2const)
        ToD.set_tgt_with_src_by_d_tgt2src(d_evup, d_evin, _d_evup2evin)
        return d_evup

    @classmethod
    def sh_aod_evup_adm(cls, aod_evin: TyAoD) -> TyAoD:
        _aod_evup: TyAoD = []
        for _d_evin in aod_evin:
            _d_evup = cls.sh_d_evup_adm(_d_evin)
            AoD.append_unique(_aod_evup, _d_evup)
        return _aod_evup

    @classmethod
    def sh_doaod_adm_new(cls, aod_evin: TyAoD) -> TyDoAoD:
        _doaod_evup: TyDoAoD = {}
        for _d_evin in aod_evin:
            _d_evup = cls.sh_d_evup_adm(_d_evin)
            DoA.append_by_key_unique_value(_doaod_evup, 'new', _d_evup)
        return _doaod_evup


class EvinEvex:
    """
    Check EcoVadis input data (from Systems like OmniTracker) against
    EcoVadis export data
    """
    msg_evex = ("No entries found in Evex dataframe for "
                "Evex key: '{K1}' and Evin value: {V1} and "
                "Evex key: '{K2}' and Evin value: {V2}")
    msg_evin = "Evin Key: '{K}' not found in Evin Dictionary {D}"

    @classmethod
    def query_with_key(
            cls, d_evin: TyDic, df_evex: TnPdDf, evin_key: Any, evin_value_ctryco: Any
    ) -> TnPdDf:
        if df_evex is None or df_evex.empty:
            return None
        _evin_value = Dic.get(d_evin, evin_key)
        if not _evin_value:
            Log.debug(cls.msg_evin.format(K=evin_key, D=d_evin))
            return None
        _evex_key_ctryco = Cfg.Utils.evex_key_ctryco
        _d_evin2evex_keys = Cfg.Utils.d_evin2evex_keys

        _evex_key = _d_evin2evex_keys[evin_key]
        _cond1 = df_evex[_evex_key] == _evin_value
        _cond2 = df_evex[_evex_key_ctryco] == evin_value_ctryco
        _cond = _cond1 & _cond2
        df: TnPdDf = df_evex.loc[_cond]
        Log.info(cls.msg_evex.format(
            K1=_evex_key, V1=_evin_value,
            K2=_evex_key_ctryco, V2=evin_value_ctryco))
        return df

    @classmethod
    def query_with_keys(
            cls, d_evin: TyDic, df_evex: TnPdDf) -> TnPdDf:
        _evin_key_ctryco = Cfg.Utils.evin_key_ctryco
        _evin_val_ctryco = d_evin.get(_evin_key_ctryco)
        if not _evin_val_ctryco:
            Log.error(cls.msg_evin.format(K=_evin_key_ctryco, D=d_evin))
            return None
        for _evin_key in Cfg.Utils.a_evin_key:
            df = cls.query_with_key(d_evin, df_evex, _evin_key, _evin_val_ctryco)
            if df is not None:
                return df
        return None

    @classmethod
    def query(cls, d_evin: TyDic, df_evex: TnPdDf) -> TyDic:
        _evin_key_uniqueid = Cfg.Utils.evin_key_uniqueid
        _evin_key_duns = Cfg.Utils.evin_key_duns
        _d_evin2evex_keys = Cfg.Utils.d_evin2evex_keys

        _df: TnPdDf = PdDf.query_with_key(
            df_evex, d_evin, dic_key=_evin_key_uniqueid, d_key2key=_d_evin2evex_keys)
        if _df is not None:
            return Evex.sh_d_evex(_df)

        _df = PdDf.query_with_key(
            df_evex, d_evin, dic_key=_evin_key_duns, d_key2key=_d_evin2evex_keys)
        if _df is not None:
            return Evex.sh_d_evex(_df)

        _df = cls.query_with_keys(d_evin, df_evex)
        return Evex.sh_d_evex(_df)

    @classmethod
    def join_adm(cls, aod_evin: TnAoD, df_evex: TnPdDf) -> TyDoAoD:
        if not aod_evin:
            return {}
        if df_evex is None:
            return Evin.sh_doaod_adm_new(aod_evin)

        _evin_key_uniqueid = Cfg.Utils.evin_key_uniqueid
        _d_evin2evex_keys = Cfg.Utils.d_evin2evex_keys
        _doaod_evup: TyDoAoD = {}
        for _d_evin in aod_evin:
            _df: TnPdDf = PdDf.query_with_key(
                df_evex, _d_evin,
                dic_key=_evin_key_uniqueid, d_key2key=_d_evin2evex_keys)
            if _df is None:
                _d_evup = Evin.sh_d_evup_adm(_d_evin)
                DoA.append_by_key_unique_value(_doaod_evup, 'new', _d_evup)
            else:
                _d_evex = Evex.sh_d_evex(_df)
                _change_status, _d_evup = cls.sh_d_evup_adm(_d_evin, _d_evex)
                DoA.append_by_key_unique_value(_doaod_evup, _change_status, _d_evup)
        return _doaod_evup

    @classmethod
    def join_del(cls, aod_evin: TnAoD, df_evex: TnPdDf) -> TyAoD:
        _evin_key_uniqueid = Cfg.Utils.evin_key_uniqueid
        _d_evin2evex_keys = Cfg.Utils.d_evin2evex_keys

        _aod_evup: TyAoD = []
        if not aod_evin:
            return _aod_evup

        for _d_evin in aod_evin:
            _df_evex_row: TnPdDf = PdDf.query_with_key(
                    df_evex, _d_evin,
                    dic_key=_evin_key_uniqueid, d_key2key=_d_evin2evex_keys)
            if _df_evex_row is not None:
                _d_evup_del: TnDic = Evex.sh_d_evup_del_from_df(_df_evex_row)
                if _d_evup_del:
                    AoD.append_unique(_aod_evup, _d_evup_del)
        return _aod_evup

    @staticmethod
    def sh_d_evup_adm(d_evin: TyDic, d_evex: TyDic) -> tuple[str, TyDic]:
        _sw_adm_use_evex: TyBool = Cfg.DoSwAdm.use_evex
        _d_evup2const: TyDic = Cfg.Utils.d_evup2const
        _d_evup2evex: TyDic = Cfg.Utils.d_evup2evex
        _d_evup2evin: TyDic = Cfg.Utils.d_evup2evin

        d_evup: TyDic = {}
        ToD.set_tgt_with_src(d_evup, _d_evup2const)
        ToD.set_tgt_with_src_by_d_tgt2src(d_evup, d_evex, _d_evup2evex)
        ToD.set_tgt_with_src_by_d_tgt2src(d_evup, d_evin, _d_evup2evin)

        if _sw_adm_use_evex:
            for key_evup, key_evex in _d_evup2evex.items():
                if d_evup[key_evup] != d_evex[key_evex]:
                    return 'ch_y', d_evup
            return 'ch_n', d_evup
        else:
            return '-', d_evup


class EvexEvin:
    """
    Check EcoVadis Export Data against
    EcoVadis input data (from Systems like OmniTracker)
    """
    @classmethod
    def join_del(cls, aod_evex: TnAoD, df_evin: TnPdDf) -> TyAoD:
        _aod_evup: TyAoD = []
        if not aod_evex or df_evin is None:
            return _aod_evup
        for _d_evex in aod_evex:
            _df_evin_row: TnPdDf = PdDf.query_with_key(
                df_evin, _d_evex,
                dic_key=Cfg.Utils.evin_key_uniqueid,
                d_key2key=Cfg.Utils.d_evex2evin_keys)
            if _df_evin_row is None:
                _d_evup = Evex.sh_d_evup_del_from_dic(_d_evex)
                if _d_evup:
                    AoD.append_unique(_aod_evup, _d_evup)
        return _aod_evup
