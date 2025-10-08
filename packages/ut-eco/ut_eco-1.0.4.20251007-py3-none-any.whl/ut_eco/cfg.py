"""
This module provides utility classes for the management of
EcoVadis Sustainablitity Risk (SRR) processing
"""
from ut_eco.cfgde import UtilsDe
from ut_eco.cfgen import UtilsEn

from typing import Any
TyDic = dict[Any, Any]


class Cfg:

    Utils: Any = UtilsDe
    eco_lang: str = 'De'
    eco_if: str = 'xls'

    Url = {

        'd_sandbox': {
            'url': 'https://api-sandboc.ecovadis-survey.com',
            'description': 'Used to test the API calls in a dummy database',
        },
        'd_live': {
            'url': 'https://api.ecovadis-survey.com',
            'description': 'Set calls here to interact with live data',
        },
        'version': 'v2.2',
    }

    Request = {

        'post_token': {
            'command':  'POST',
            'endpoint': '/EVToken',
        },
        'post_upsert': {
            'command':  'POST',
            'endpoint': '/v2.2/IqPartners/UpdatePartnerRL',
        },
        'post_delete': {
            'command': 'POST',
            'endpoint': '/v2.2/IqPartners/UpdatePartnerRL',
        },
        'get_status': {
            'command': 'GET',
            'endpoint': '/v2.2/IqPartners/GetOperationStatus',
        },
        'get_partner_by_uniqueid': {
            'command':  'GET',
            'endpoint': '/v2.2/IqPartners/GetPartnerByUniqueId',
        },
        'get_risk_by_duns': {
            'command':  'GET',
            'endpoint': '/v2.2/risk',
        },
    }

    sheet_adm = 'Partner verwalten'
    sheet_del = 'Partner entfernen'
    sheet_exp = 'IQ-Export'
    sheet_help = 'Hilfe'

    class InPathnm:

        evex = 'in_path_evex'
        evup_tmp = 'in_path_evup_tmp'
        evin = 'in_path_evin'

    class OutPathnm:

        evin_adm_vfy = 'out_path_evin_adm_vfy'
        evin_del_vfy = 'out_path_evin_del_vfy'
        evin_reg_vfy = 'out_path_evin_reg_vfy'

        evup_adm = 'out_path_evup_adm'
        evup_del = 'out_path_evup_del'
        evup_reg = 'out_path_evup_reg'
        evex = 'out_path_evex'

    class Task:

        d_pathnm2datetype = {
            'in_path_evin': 'last',
            'in_path_evex': 'last',
            'in_path_evup_tmp': '',
            'out_path_evin_adm_vfy': 'now',
            'out_path_evin_del_vfy': 'now',
            'out_path_evin_reg_vfy': 'now',
            'out_path_evup_adm': 'now',
            'out_path_evup_del': 'now',
            'out_path_evup_reg': 'now',
            'out_path_evex': 'now',
        }

    class DoSwAdm:

        vfy = True
        vfy_duns = True
        vfy_duns_is_unique = True
        vfy_coynmdis = True
        vfy_coynmoff = True
        vfy_regno = True
        vfy_ctryco = True
        vfy_uniqueid = True
        vfy_uniqueid_is_unique = True
        vfy_town = True
        vfy_town_with_ctryco = True
        vfy_postco = True
        use_duns = True
        use_evex = False

    class DoSwDel:

        vfy = True
        vfy_uniqueid = True
        vfy_uniqueid_is_unique = True
        vfy_iq_id = True
        vfy_iq_id_is_unique = True
        use_evex = True

    @classmethod
    def set_kwargs(cls, kwargs: TyDic) -> None:
        kwargs['d_pathnm2datetype'] = cls.Task.d_pathnm2datetype
        cls.eco_if = kwargs.get('eco_if', 'xls')
        cls.eco_lang = kwargs.get('eco_lang', 'De')
        match cls.eco_lang:
            case 'De':
                cls.Utils = UtilsDe
            case 'En':
                cls.Utils = UtilsEn
            case _:
                msg = f"usupported language = {cls.eco_lang}; supported languages are: 'De', 'En'"
                raise Exception(msg)

        cls.DoSwAdm.vfy = kwargs.get('sw_adm_vfy', True)
        cls.DoSwAdm.vfy_duns = kwargs.get('sw_adm_vfy_duns', True)
        cls.DoSwAdm.vfy_duns_is_unique = kwargs.get('sw_adm_vfy_duns_is_unique', True)
        cls.DoSwAdm.vfy_coynmdis = kwargs.get('sw_adm_vfy_coynmdis', True)
        cls.DoSwAdm.vfy_coynmoff = kwargs.get('sw_adm_vfy_coynmoff', True)
        cls.DoSwAdm.vfy_regno = kwargs.get('sw_adm_vfy_regno', True)
        cls.DoSwAdm.vfy_ctryco = kwargs.get('sw_adm_vfy_ctryco', True)
        cls.DoSwAdm.vfy_uniqueid = kwargs.get('sw_adm_vfy_uniqueid', True)
        cls.DoSwAdm.vfy_uniqueid_is_unique = kwargs.get(
                'sw_adm_vfy_uniqueid_is_unique', True)
        cls.DoSwAdm.vfy_town = kwargs.get('sw_adm_vfy_town', False)
        cls.DoSwAdm.vfy_town_with_ctryco = kwargs.get('sw_adm_vfy_town_with_ctryco', False)
        cls.DoSwAdm.vfy_postco = kwargs.get('sw_adm_vfy_postco', True)

        cls.DoSwAdm.use_duns = kwargs.get('sw_adm_use_duns', True)
        cls.DoSwAdm.use_evex = kwargs.get('sw_adm_use_evex', False)

        cls.DoSwDel.vfy = kwargs.get('sw_del_vfy', True)
        cls.DoSwDel.vfy_uniqueid = kwargs.get('sw_del_vfy_uniqueid', True)
        cls.DoSwDel.vfy_uniqueid_is_unique = kwargs.get(
                'sw_del_vfy_uniqueid_is_unique', True)
        cls.DoSwDel.vfy_iq_id = kwargs.get('sw_del_vfy_iq_id', True)
        cls.DoSwDel.vfy_iq_id_is_unique = kwargs.get('sw_del_vfy_iq_id_is_unique', True)

        cls.DoSwDel.use_evex = kwargs.get('sw_del_use_evex', False)
