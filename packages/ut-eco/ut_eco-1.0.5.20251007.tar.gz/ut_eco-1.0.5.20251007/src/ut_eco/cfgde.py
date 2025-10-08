"""
This module provides utility classes for the management of
EcoVadis Sustainablitity Risk (SRR) processing
"""
from typing import Any
TyDic = dict[Any, Any]


class UtilsDe:

    d_ecv_iq2umh_iq = {
        'Sehr niedrig': '1',
        'Niedrig': '2',
        'Mittelniedrig': '3',
        'Mittelhoch': '4',
        'Hoch': '4',
        'Sehr hoch': '4',
        'Undefiniert': '4',
    }
    evin_key_ctryco = 'Landesvorwahl'
    evin_key_coynmdis = 'Anzeigename des Unternehmens (Ihr Name)'
    evin_key_coynmoff = 'Offizieller Name des Unternehmens'
    evin_key_duns = 'DUNS-Nummer'
    evin_key_iq_id = 'IQ-ID'
    evin_key_uniqueid = 'Eindeutige ID'
    evin_key_postco = 'Postleitzahl'
    evin_key_regno = 'Steuer-ID oder andere Identifikationsnummer'
    evin_key_town = 'Stadt'

    evex_key_ctryco = 'Land'

    a_evin_key = [
        'DUNS-Nummer',
        'Steuer-ID',
        'Umsatzsteuer-ID',
        'Handelsregister-Nr',
        'Offizieller Name des Unternehmens',
        'LEI',
    ]
    d_evin2evex_keys = {
        'DUNS-Nummer': 'DUNS-Nummer',
        'Steuer-ID': 'Steuer-ID oder andere Identifikationsnummer',
        'Umsatzsteuer-ID': 'Steuer-ID oder andere Identifikationsnummer',
        'Handelsregister-Nr': 'Steuer-ID oder andere Identifikationsnummer',
        'Offizieller Name des Unternehmens': 'Name des Unternehmens',
        'LEI': 'Steuer-ID oder andere Identifikationsnummer',
        'Eindeutige ID': 'Eindeutige ID',
    }
    d_evex2evin_keys = {
        'Eindeutige ID': 'Eindeutige ID',
        'IQ-ID': 'IQ-ID',
    }
    d_evup_en2de = {
        "UniqueId": "Eindeutige ID",
        "CompanyName": "Offizieller Name des Unternehmens",
        "CriticalityScale": "ScaleAbc",
        "CriticalityLevel": "Kritikalitätsstufe",
        "SpendScale": "ScaleAbc",
        "SpendLevel": "Spend Level",
        "DunsNumber": "DUNS-Nummer",
        "RegistrationNumber": "Steuer-ID oder andere Identifikationsnummer",
        "CountryCode": "Landesvorwahl",
        "Tags": "Tags",
        "contactFirstName": "Vorname des Ansprechpartners beim Unternehmen",
        "contactLastName": "Nachname des Ansprechpartners beim Unternehmen",
        "contactEmail": "Kontakt-Telefonnummer für das Unternehmen",
    },
    d_evup2const = {
        'Anzeigename des Unternehmens (Ihr Name)': None,
        'DUNS-Nummer': '',
        'Steuer-ID oder andere Identifikationsnummer': '',
        'Offizieller Name des Unternehmens': '',

        'Landesvorwahl': '',
        'Postleitzahl': '',
        'Stadt': '',
        'Adresse': '',
        'Eindeutige ID': '',
        'IQ-ID': '',
        'Kritikalitätsstufe': '',
        'Spend Level': '',

        'Vorname des Ansprechpartners beim Unternehmen': '',
        'Nachname des Ansprechpartners beim Unternehmen': '',
        'E-Mail-Adresse des Ansprechpartners beim Unternehmen': '',
        'Kontakt-Telefonnummer für das Unternehmen': '',
        'E-Mail der anfordernden Kontaktperson': '',

        'Tags': 'Union Investment 2024; KRG',
    }

    doaod_evup2evin_keys = {
        'id1': [
            {
                'DUNS-Nummer': 'DUNS-Nummer'
            }
        ],
        'id2': [
            {
                'Steuer-ID oder andere Identifikationsnummer': 'Steuer-ID',
                'Landesvorwahl': 'Landesvorwahl'
            },
            {
                'Steuer-ID oder andere Identifikationsnummer':
                    'Umsatzsteuer-ID',
                'Landesvorwahl': 'Landesvorwahl',
                'Postleitzahl': 'Postleitzahl',
                'Stadt': 'Stadt',
                'Adresse': 'Adresse',
            },
            {
                'Steuer-ID oder andere Identifikationsnummer':
                    'Handelsregister-Nr',
                'Landesvorwahl': 'Landesvorwahl',
                'Postleitzahl': 'Postleitzahl',
                'Stadt': 'Stadt',
                'Adresse': 'Adresse',
            },
            {
                'Steuer-ID oder andere Identifikationsnummer': 'LEI',
                'Landesvorwahl': 'Landesvorwahl',
                'Postleitzahl': 'Postleitzahl',
                'Stadt': 'Stadt',
                'Adresse': 'Adresse',
            }
        ],
        'id3': [
            {
                'Offizieller Name des Unternehmens':
                    'Offizieller Name des Unternehmens',
                'Landesvorwahl': 'Land',
                'Postleitzahl': 'Postleitzahl',
                'Stadt': 'Stadt',
                'Adresse': 'Adresse',
            }
        ]
    }
    d_evup2evin_nonkeys = {
        'Landesvorwahl': 'Landesvorwahl',
        'Postleitzahl': 'Postleitzahl',
        'Stadt': 'Stadt',
        'Adresse': 'Adresse',
        'Eindeutige ID': 'Eindeutige ID',
        'Anzeigename des Unternehmens': 'Anzeigename des Unternehmens',
        'Offizieller Name des Unternehmens': 'Offizieller Name des Unternehmens'
    }
    d_evup2evin_plz_ort_strasse = {
        'Postleitzahl': 'Postleitzahl',
        'Stadt': 'Stadt',
        'Adresse': 'Adresse',
    }
    a_evup_key = [
        'DUNS-Nummer',
        'Steuer-ID oder andere Identifikationsnummer',
        'Offizieller Name des Unternehmens'
    ]
    d_del_evup2evex = {
        'Eindeutige ID': 'Eindeutige ID',
        'IQ-ID': 'IQ-ID',
    }
    d_evup2evex = {
        'IQ-ID': 'IQ-ID',
        'Kritikalitätsstufe': 'Kritikalitätsstufe',
        'Spend Level': 'Spend Level',

        'Vorname des Ansprechpartners beim Unternehmen':
            'Vorname des Ansprechpartners beim Unternehmen',
        'Nachname des Ansprechpartners beim Unternehmen':
            'Nachname des Ansprechpartners beim Unternehmen',
        'E-Mail-Adresse des Ansprechpartners beim Unternehmen':
            'E-Mail-Adresse des Ansprechpartners beim Unternehmen',
        'Kontakt-Telefonnummer für das Unternehmen':
            'Kontakt-Telefonnummer für das Unternehmen',
        'E-Mail der anfordernden Kontaktperson':
            'E-Mail der anfordernden Kontaktperson',
        'Tags': 'Tags'
    }
    d_evup2evin = {
        'Anzeigename des Unternehmens (Ihr Name)':
            'Anzeigename des Unternehmens (Ihr Name)',
        'DUNS-Nummer': 'DUNS-Nummer', 'Offizieller Name des Unternehmens':
            'Offizieller Name des Unternehmens',

        'Landesvorwahl': 'Landesvorwahl',
        'Postleitzahl': 'Postleitzahl',
        'Stadt': 'Stadt',
        'Adresse': 'Adresse',
        'Eindeutige ID': 'Eindeutige ID',
    }
    d_evin2evex = {
        'IQ-ID': 'IQ-ID',
        'Kritikalitätsstufe': 'Kritikalitätsstufe',
        'Spend Level': 'Spend Level',

        'Vorname des Ansprechpartners beim Unternehmen':
            'Vorname des Ansprechpartners beim Unternehmen',
        'Nachname des Ansprechpartners beim Unternehmen':
            'Nachname des Ansprechpartners beim Unternehmen',
        'E-Mail-Adresse des Ansprechpartners beim Unternehmen':
            'E-Mail-Adresse des Ansprechpartners beim Unternehmen',
        'Kontakt-Telefonnummer für das Unternehmen':
            'Kontakt-Telefonnummer für das Unternehmen',
        'E-Mail der anfordernden Kontaktperson':
            'E-Mail der anfordernden Kontaktperson',
        'Tags': 'Tags'
    }
    d_evex2evin = {
        'IQ-ID': 'IQ-ID',
        'Kritikalitätsstufe': 'Kritikalitätsstufe',
        'Spend Level': 'Spend Level',

        'Vorname des Ansprechpartners beim Unternehmen':
            'Vorname des Ansprechpartners beim Unternehmen',
        'Nachname des Ansprechpartners beim Unternehmen':
            'Nachname des Ansprechpartners beim Unternehmen',
        'E-Mail-Adresse des Ansprechpartners beim Unternehmen':
            'E-Mail-Adresse des Ansprechpartners beim Unternehmen',
        'Kontakt-Telefonnummer für das Unternehmen':
            'Kontakt-Telefonnummer für das Unternehmen',
        'E-Mail der anfordernden Kontaktperson':
            'E-Mail der anfordernden Kontaktperson',
        'Tags': 'Tags',
    }
    d_evin2evup = {
        'Offizieller Name des Unternehmens':
            'Offizieller Name des Unternehmens',
        'DUNS-Nummer': 'DUNS-Nummer',
        'Steuer-ID': 'Steuer-ID oder andere Identifikationsnummer',
        'Landesvorwahl': 'Landesvorwahl',
        'Eindeutige ID': 'Eindeutige ID'
    }
