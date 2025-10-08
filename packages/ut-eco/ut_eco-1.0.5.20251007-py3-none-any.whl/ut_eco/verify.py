"""
This module provides input verification classes for the management of Sustainability Risk Rating (SRR) processing.
"""
from __future__ import annotations
from typing import Any, TypeAlias

import pandas as pd

from ut_dic.dic import Dic
from ut_doa.doa import DoA
from ut_eco.cfg import Cfg

TyPdDf: TypeAlias = pd.DataFrame

TyArr = list[Any]
TyAoStr = list[str]
TyBool = bool
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoAoA = dict[Any, TyAoA]
TyDoAoD = dict[Any, TyAoD]
TyDoD = dict[Any, TyDic]
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


class EvinVfyAdm:
    """
    OmniTracker EcoVadis class
    """
    ctryco_is_empty = 'adm_wrn_ctryco_is_empty'
    ctryco_length_is_invalid = 'adm_err_ctryco_length_is_gt_2'
    ctryco_is_invalid = 'adm_wrn_ctryco_is_invalid'
    coynmdis_is_empty = 'adm_err_coynmdis_is_empty'
    coynmdis_length_is_invalid = 'adm_err_coynmdis_length_is_gt_500'
    coynmoff_is_empty = 'adm_wrn_coynmoff_is_empty'
    coynmoff_length_is_invalid = 'adm_err_coynmoff_length_is_gt_500'
    duns_is_empty = 'adm_err_duns_is_empty'
    duns_length_is_invalid = 'adm_err_duns_length_is_gt_9'
    duns_isnot_numeric = 'adm_err_duns_is_not_numeric'
    duns_isnot_unique = 'adm_wrn_duns_is_not_unique'
    postco_is_empty = 'adm_wrn_postco_is_empty'
    postco_length_is_invalid = 'adm_err_postco_length_is_gt_30'
    postco_is_invalid = 'adm_wrn_postco_is_invalid'
    uniqueid_is_empty = 'adm_err_uniqueid_is_empty'
    uniqueid_length_is_invalid = 'adm_err_postco_length_is_gt_50'
    uniqueid_isnot_unique = 'adm_err_uniqueid_is_not_unique'
    regno_is_empty = 'adm_wrn_regno_is_empty'
    town_is_empty = 'adm_wrn_town_is_empty'
    town_is_invalid = 'adm_wrn_town_is_invalid'

    @classmethod
    def vfy_duns(
            cls,
            d_sw: TyDoB,
            d_evin: TyDic,
            dod: TyDoD,
            doaod_vfy: TyDoAoD
    ) -> None:
        """
        Verify DUNS number
        """
        _key: TnStr = Cfg.Utils.evin_key_duns
        _val: TnStr = d_evin.get(_key)
        if not _val:
            DoA.append_by_key_unique_value(doaod_vfy, cls.duns_is_empty, d_evin)
            d_sw['duns'] = False
            return
        if len(_val) > 9:
            DoA.append_by_key_unique_value(doaod_vfy, cls.duns_length_is_invalid, d_evin)
            d_sw['duns'] = False
            return
        if not _val.isdigit():
            DoA.append_by_key_unique_value(doaod_vfy, cls.duns_isnot_numeric, d_evin)
            d_sw['duns'] = False
            return
        if Cfg.DoSwAdm.vfy_duns_is_unique:
            if dod[_key][_val] > 1:
                DoA.append_by_key_unique_value(doaod_vfy, cls.duns_isnot_unique, d_evin)
                # d_sw['duns'] = False
                # return
        if len(_val) < 9:
            _val = f"{_val:09}"
        Dic.set_by_key(d_evin, _key, _val)
        d_sw['duns'] = True
        return

    @classmethod
    def vfy_coynmdis(cls, d_sw: TyDoB, d_evin: TyDic, doaod_vfy: TyDoAoD) -> None:
        """
        Verify Company display name
        """
        _key: TnStr = Cfg.Utils.evin_key_coynmdis
        _val = d_evin.get(_key)
        if not _val:
            DoA.append_by_key_unique_value(doaod_vfy, cls.coynmdis_is_empty, d_evin)
            d_sw['coynmdis'] = False
            return
        if len(_val) > 500:
            DoA.append_by_key_unique_value(doaod_vfy, cls.coynmdis_length_is_invalid, d_evin)
            d_sw['coynmdis'] = False
            return
        d_sw['coynmdis'] = True
        return

    @classmethod
    def vfy_coynmoff(cls, d_sw: TyDoB, d_evin: TyDic, doaod_vfy: TyDoAoD) -> None:
        """
        Verify Company official name
        """
        _key: TnStr = Cfg.Utils.evin_key_coynmoff
        _val = d_evin.get(_key)
        if not _val:
            DoA.append_by_key_unique_value(doaod_vfy, cls.coynmoff_is_empty, d_evin)
            d_sw['coynmoff'] = False
            return
        if len(_val) > 500:
            DoA.append_by_key_unique_value(doaod_vfy, cls.coynmoff_length_is_invalid, d_evin)
            d_sw['coynmoff'] = False
            return
        d_sw['coynmoff'] = True
        return

    @classmethod
    def vfy_regno(cls, d_sw: TyDoB, d_evin: TyDic, doaod_vfy: TyDoAoD) -> None:
        """
        Verify Registration number
        """
        _key: TnStr = Cfg.Utils.evin_key_regno
        _val = d_evin.get(_key)
        if not _val:
            DoA.append_by_key_unique_value(doaod_vfy, cls.regno_is_empty, d_evin)
            d_sw['regno'] = False
            return
        d_sw['regno'] = True
        return

    @classmethod
    def vfy_ctryco(cls, d_sw: TyDoB, d_evin: TyDic, doaod_vfy: TyDoAoD) -> None:
        """
        Verify Country Code
        """
        _key: TyStr = Cfg.Utils.evin_key_ctryco
        _val = d_evin.get(_key)
        if not _val:
            DoA.append_by_key_unique_value(doaod_vfy, cls.ctryco_is_empty, d_evin)
            d_sw['ctryco'] = False
            return
        if len(_val) > 2:
            DoA.append_by_key_unique_value(doaod_vfy, cls.ctryco_length_is_invalid, d_evin)
            d_sw['ctryco'] = False
            return
        import pycountry
        try:
            _country = pycountry.countries.get(alpha_2=_key.upper())
        except KeyError:
            DoA.append_by_key_unique_value(doaod_vfy, cls.ctryco_is_invalid, d_evin)
            d_sw['ctryco'] = False
            return
        d_sw['ctryco'] = True
        return

    @classmethod
    def vfy_uniqueid(
            cls, d_sw: TyDoB, d_evin: TyDic, dod: TyDoD, doaod_vfy: TyDoAoD
    ) -> None:
        """
        Verify Country Code
        """
        _key: TyStr = Cfg.Utils.evin_key_uniqueid
        _val = d_evin.get(_key)
        if not _val:
            DoA.append_by_key_unique_value(doaod_vfy, cls.uniqueid_is_empty, d_evin)
            d_sw['uniqueid'] = False
            return
        if len(_val) > 50:
            DoA.append_by_key_unique_value(doaod_vfy, cls.uniqueid_length_is_invalid, d_evin)
            d_sw['uniqueid'] = False
            return
        if Cfg.DoSwAdm.vfy_uniqueid_is_unique:
            if dod[_key][_val] > 1:
                DoA.append_by_key_unique_value(
                        doaod_vfy, cls.uniqueid_isnot_unique, d_evin)
                d_sw['uniqueid'] = False
                return
        d_sw['uniqueid'] = True
        return

    @classmethod
    def vfy_town(cls, d_sw: TyDoB, d_evin: TyDic, doaod_vfy: TyDoAoD) -> None:
        """
        Verify Town by Country Code
        """
        _key_town: TyStr = Cfg.Utils.evin_key_town
        _val_town: TnStr = d_evin.get(_key_town)
        if not _val_town:
            DoA.append_by_key_unique_value(doaod_vfy, cls.town_is_empty, d_evin)
            d_sw['town'] = False
            return
        if not Cfg.DoSwAdm.vfy_town_with_ctryco:
            d_sw['town'] = True
            return
        _key_ctryco: TyStr = Cfg.Utils.evin_key_ctryco
        _val_ctryco: TnStr = d_evin.get(_key_ctryco)
        if not _val_ctryco:
            d_sw['town'] = True
            return

        from geopy.geocoders import Nominatim
        from geopy.exc import GeocoderTimedOut
        _geolocator = Nominatim(user_agent="geo_verifier")
        try:
            _location = _geolocator.geocode(_val_town)
        except GeocoderTimedOut:
            DoA.append_by_key_unique_value(doaod_vfy, cls.town_is_invalid, d_evin)
            d_sw['town'] = False
            return
        if _location is None:
            DoA.append_by_key_unique_value(doaod_vfy, cls.town_is_invalid, d_evin)
            d_sw['town'] = False
            return
        _address: TyStr = _location.address
        if _val_ctryco.lower() not in _address.lower():
            DoA.append_by_key_unique_value(doaod_vfy, cls.town_is_invalid, d_evin)
            d_sw['town'] = False
            return
        d_sw['town'] = True
        return

    @classmethod
    def vfy_postco(cls, d_sw: TyDoB, d_evin: TyDic, doaod_vfy: TyDoAoD) -> None:
        """
        Verify Postal Code
        """
        _key_postco: TyStr = Cfg.Utils.evin_key_postco
        _val_postco: TnStr = d_evin.get(_key_postco)
        if not _val_postco:
            DoA.append_by_key_unique_value(doaod_vfy, cls.postco_is_empty, d_evin)
            d_sw['postco'] = False
            return
        if len(_val_postco) > 30:
            DoA.append_by_key_unique_value(doaod_vfy, cls.postco_length_is_invalid, d_evin)
            d_sw['postco'] = False
            return
        _key_ctryco: TyStr = Cfg.Utils.evin_key_ctryco
        _val_ctryco: TnStr = d_evin.get(_key_ctryco)
        from postal_codes_tools.postal_codes import verify_postal_code_format
        if not verify_postal_code_format(postal_code=_val_postco, country_iso2=_val_ctryco):
            DoA.append_by_key_unique_value(doaod_vfy, cls.postco_is_invalid, d_evin)
            d_sw['postco'] = False
            return
        d_sw['postco'] = True
        return

    @classmethod
    def vfy_d_evin(cls, d_evin: TyDic, dod, doaod_vfy: TyDoAoD) -> TyBool:
        if not Cfg.DoSwAdm.vfy:
            return True

        # Set verification summary switch
        _d_sw: TyDoB = {}

        if Cfg.DoSwAdm.vfy_duns:
            # Verify DUNS
            cls.vfy_duns(_d_sw, d_evin, dod, doaod_vfy)
        if Cfg.DoSwAdm.vfy_coynmdis:
            # Verify Company display name
            cls.vfy_coynmdis(_d_sw, d_evin, doaod_vfy)
        if Cfg.DoSwAdm.vfy_coynmoff:
            # Verify Company official name
            cls.vfy_coynmoff(_d_sw, d_evin, doaod_vfy)
        if Cfg.DoSwAdm.vfy_regno:
            # Verify Country display name
            cls.vfy_regno(_d_sw, d_evin, doaod_vfy)
        if Cfg.DoSwAdm.vfy_ctryco:
            # Verify Country Code
            cls.vfy_ctryco(_d_sw, d_evin, doaod_vfy)
        if Cfg.DoSwAdm.vfy_uniqueid:
            # Verify Unique ID
            cls.vfy_uniqueid(_d_sw, d_evin, dod, doaod_vfy)
        if Cfg.DoSwAdm.vfy_town:
            # Verify Town in Country
            cls.vfy_town(_d_sw, d_evin, doaod_vfy)
        if Cfg.DoSwAdm.vfy_postco:
            # Verify Postal Code
            cls.vfy_postco(_d_sw, d_evin, doaod_vfy)

        if Cfg.DoSwAdm.use_duns:
            return _d_sw['duns'] and _d_sw['coynmdis'] and _d_sw['uniqueid']

        if _d_sw['duns'] and _d_sw['coynmdis'] and _d_sw['uniqueid']:
            return True
        if _d_sw['regno'] and _d_sw['ctryco'] and _d_sw['coynmdis']:
            return True
        if _d_sw['coynmoff'] and _d_sw['ctryco'] and _d_sw['coynmdis']:
            return True

        return False

    @staticmethod
    def set_dod(dod: TyDoD, key, val) -> None:
        if key not in dod:
            dod[key] = {}
        if val in dod[key]:
            dod[key][val] = dod[key][val] + 1
        else:
            dod[key][val] = 1

    @classmethod
    def sh_dod(cls, aod_evin: TnAoD) -> TyDoD:
        _dod: TyDoD = {}
        if not aod_evin:
            return _dod
        for _d_evin in aod_evin:
            if Cfg.DoSwAdm.vfy_duns_is_unique:
                _key = Cfg.Utils.evin_key_duns
                _val: TnStr = Dic.get(_d_evin, _key)
                cls.set_dod(_dod, _key, _val)
            if Cfg.DoSwAdm.vfy_uniqueid_is_unique:
                _key = Cfg.Utils.evin_key_uniqueid
                _val = Dic.get(_d_evin, _key)
                cls.set_dod(_dod, _key, _val)
        return _dod

    @classmethod
    def vfy_aod_evin(cls, aod_evin: TnAoD) -> tuple[TyAoD, TyDoAoD]:
        _aod_evin: TyAoD = []
        _doaod_vfy: TyDoAoD = {}
        if not aod_evin:
            return _aod_evin, _doaod_vfy
        _dod = cls.sh_dod(aod_evin)
        for _d_evin in aod_evin:
            _sw: bool = cls.vfy_d_evin(_d_evin, _dod, _doaod_vfy)
            if _sw:
                _aod_evin.append(_d_evin)
        return _aod_evin, _doaod_vfy


class EvinVfyDel:
    """
    OmniTracker EcoVadis class
    """
    uniqueid_is_empty = 'del_wrn_uniqueid_is_empty'
    uniqueid_isnot_unique = 'del_err_uniqueid_is_not_unique'
    iq_id_is_empty = 'del_wrn_iq_id_is_empty'
    iq_id_isnot_unique = 'del_err_iq_id_is_not_unique'

    @classmethod
    def vfy_uniqueid(
            cls, d_sw: TyDoB, d_evin: TyDic, dod: TyDoD, doaod_vfy: TyDoAoD
    ) -> None:
        """
        Verify Country Code
        """
        _key: TnStr = Cfg.Utils.evin_key_uniqueid
        _val = Dic.get(d_evin, _key)
        if not _val:
            DoA.append_by_key_unique_value(doaod_vfy, cls.uniqueid_is_empty, d_evin)
            d_sw['uniqueid'] = False
            return
        if Cfg.DoSwDel.vfy_uniqueid_is_unique:
            if dod[_key][_val] > 1:
                DoA.append_by_key_unique_value(
                        doaod_vfy, cls.uniqueid_isnot_unique, d_evin)
                d_sw['uniqueid'] = False
            return
        d_sw['uniqueid'] = True
        return

    @classmethod
    def vfy_iq_id(
            cls, d_sw: TyDoB, d_evin: TyDic, dod: TyDoD, doaod_vfy: TyDoAoD
    ) -> None:
        """
        Verify IQ_ID
        """
        _key: TnStr = Cfg.Utils.evin_key_uniqueid
        _val = Dic.get(d_evin, _key)
        if not _val:
            DoA.append_by_key_unique_value(doaod_vfy, cls.iq_id_is_empty, d_evin)
            d_sw['iq_id'] = False
            return
        if Cfg.DoSwDel.vfy_iq_id_is_unique:
            if dod[_key][_val] > 1:
                DoA.append_by_key_unique_value(doaod_vfy, cls.iq_id_isnot_unique, d_evin)
                d_sw['iq_id'] = False
            return
        d_sw['iq_id'] = True
        return

    @classmethod
    def vfy_d_evin(
            cls, d_evin: TyDic, dod: TyDoD, doaod_vfy: TyDoAoD
    ) -> TyBool:
        if not Cfg.DoSwDel.vfy:
            return True

        # Set verification summary switch
        _d_sw: TyDoB = {}

        if Cfg.DoSwDel.vfy_uniqueid:
            # Verify Unique ID
            cls.vfy_uniqueid(_d_sw, d_evin, dod, doaod_vfy)

        if Cfg.DoSwDel.vfy_iq_id:
            # Verify EcoVadis IQ Id
            cls.vfy_iq_id(_d_sw, d_evin, dod, doaod_vfy)

        if _d_sw['uniqueid'] or _d_sw['iq_id']:
            return True

        return False

    @staticmethod
    def sh_dod(aod_evin: TnAoD) -> TyDoD:
        _dod: TyDoD = {}
        if not aod_evin:
            return _dod
        for _d_evin in aod_evin:
            if Cfg.DoSwDel.vfy_iq_id_is_unique:
                _key = Cfg.Utils.evin_key_iq_id
                _val: TnStr = Dic.get(_d_evin, _key)
                if _key not in _dod:
                    _dod[_key] = {}
                if _val in _dod[_key]:
                    _dod[_key][_val] = _dod[_key][_val] + 1
                else:
                    _dod[_key][_val] = 1
            if Cfg.DoSwDel.vfy_uniqueid_is_unique:
                _key = Cfg.Utils.evin_key_uniqueid
                _val = Dic.get(_d_evin, _key)
                if _key not in _dod:
                    _dod[_key] = {}
                if _val in _dod[_key]:
                    _dod[_key][_val] = _dod[_key][_val] + 1
                else:
                    _dod[_key][_val] = 1
        return _dod

    @classmethod
    def vfy_aod_evin(cls, aod_evin: TnAoD) -> tuple[TyAoD, TyDoAoD]:
        _aod_evin: TyAoD = []
        _doaod_vfy: TyDoAoD = {}
        if not aod_evin:
            return _aod_evin, _doaod_vfy
        _dod = cls.sh_dod(aod_evin)
        for _d_evin in aod_evin:
            if cls.vfy_d_evin(_d_evin, _dod, _doaod_vfy):
                _aod_evin.append(_d_evin)
        return _aod_evin, _doaod_vfy
