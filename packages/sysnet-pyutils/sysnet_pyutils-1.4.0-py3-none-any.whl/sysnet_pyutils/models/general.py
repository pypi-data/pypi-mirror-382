from __future__ import annotations

import json
from datetime import datetime
from enum import Enum
from typing import Optional, List, Tuple, Any

from pydantic import BaseModel, Field, EmailStr
from typing_extensions import Self

from sysnet_pyutils.utils import local_now, is_valid_unid, is_valid_pid, is_valid_uuid


class ApiError(Exception):
    def __init__(self, code: int = 500, message: str = None):
        self.code = code
        self.message = message


class ErrorModel(BaseModel):
    code: int
    message: str


class UserType(BaseModel):
    identifier: Optional[str] = Field(
        default=None,
        description='identifikátor uživatele (PID nebo UUID)',
        examples=['ABC123456789'],
    )
    name: Optional[str] = Field(
        default=None, description='Jméno uživatele', examples=['Jiří Novák']
    )
    dn: Optional[str] = Field(
        default=None,
        description='Příznačné jméno (distinguished name) LDAP',
        examples=['cn=Jiří Novák, o=AOPK, c=CZ'],
    )
    email: Optional[EmailStr] = Field(default=None, description='Adresa elektronické pošty', examples=['jiri.novak@aopk.cz'])
    phone: Optional[str] = Field(default=None, description='Telefonní číslo uživatele')
    name_first: Optional[str] = Field(default=None, description='Křestní jméno uživatele', examples=['Jiří'])
    name_last: Optional[str] = Field(default=None, description='Příjmení uživatele', examples=['Novák'])
    name_full: Optional[str] = Field(default=None, description='Úplné jméno uživatele', examples=['MUDr. Jiří Novák, PhD.'])


class BaseEnum(str, Enum):
    pass

    @classmethod
    def _missing_(cls, value):
        if value is None:
            return None
        value = str(value).lower()
        for member in cls:
            if member.lower() == value:
                return member
        return None

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of PersonTypeType from a JSON string"""
        return cls(json.loads(json_str))


class AclLevelEnum(BaseEnum):
    READ = 'R'
    WRITE = 'W'
    MANAGE = 'M'


class PersonTypeEnum(BaseEnum):
    """
    Typ osoby (zdroj CRŽP):
        - legalEntity: tuzemská právnická osoba
        - legalEntityWithoutIco: tuzemská právnická osoba bez IČO
        - foreignLegalEntity: zahraniční právnická osoba
        - businessNaturalPerson: tuzemská fyzická osoba podnikající
        - naturalPerson: tuzemská fyzická osoba nepodnikající
        - foreignNaturalPerson: zahraniční fyzická osoba podnikající
    """
    LEGAL_ENTITY = 'legalEntity'
    LEGAL_ENTITY_WO_ICO = 'legalEntityWithoutIco'
    FOREIGN_LEGAL_ENTITY = 'foreignLegalEntity'
    NATURAL_PERSON = 'naturalPerson'
    BUSINESS_NATURAL_PERSON = 'businessNaturalPerson'
    FOREIGN_NATURAL_PERSON = 'foreignNaturalPerson'
    EMPTY = ''
    NULL = None


class CodeValueType(BaseModel):
    # kód/hodnota
    code: Optional[str] = Field(default=None, description='Kód položky', examples=['CZ'])
    value: Optional[str] = Field(default=None, description='Hodnota položky', examples=['Česká republika / Czech republic'])

    def __eq__(self, other):
        if not isinstance(other, CodeValueType):
            return NotImplemented
        return self.code == other.code and self.value == other.value

    def load_data(self, data: Tuple[Any, Any]):
        self.code = data[0]
        self.value = data[1]
        return self

class RegionalValueType(CodeValueType):
    # kód/hodnota/rok/kraj
    year: Optional[int] = Field(default=None, description='Rok platnotsi položky', examples=[2022])
    region: Optional[str] = Field(default=None, description='Kraj platnosti položky', examples=['Středočeský kraj'])


class TimeLimitedType(CodeValueType):
    # kód/hodnota
    date_from: Optional[datetime] = Field(default=None, description='Platí od data')
    date_to: Optional[datetime] = Field(default=None, description='Platí do data')


class LogItemType(BaseModel):
    # položka logu
    timestamp: datetime = Field(default=local_now(), description='Časová značka logu')
    originator: Optional[str] = Field(default='SYSTEM', description='Zdroj logu', examples=['<NAME>'])
    message: Optional[str] = Field(default=None, description='Zpráva logu', examples=['Autorizováno'])

    def __str__(self):
        out = f"{self.timestamp.replace(microsecond=0).isoformat(' ')} [{self.originator}] {self.message}"
        return out


class ContainerHistoryItemType(BaseModel):
    # položka historie zařazení do kontejnerů
    timestamp: datetime = Field(default=local_now(), description='Časová značka logu')
    originator: Optional[str] = Field(default='SYSTEM', description='Zdroj logu', examples=['<NAME>'])
    container: Optional[str] = Field(default=None, description='Identifikátor kontejneru')
    message: Optional[str] = Field(default=None, description='Zpráva logu', examples=['Autorizováno'])

    def __str__(self):
        out = f"{self.timestamp.replace(microsecond=0).isoformat(' ')} [{self.originator}] container={self.container}: {self.message}"
        return out


class AclType(BaseModel):
    name: Optional[str] = Field(
        default=None,
        description='Uživatelské jméno nebo název role',
        examples=['jan.novak@email.com'],
    )
    level: Optional[AclLevelEnum] = Field(
        default=None, description='Úroveň přístupu (reader, writer, manager)'
    )
    can_delete: Optional[bool] = Field(
        default=False, description='Oprávnění odstraňovat dokumenty'
    )


class MetadataEssentialType(BaseModel):
    """
    Hlavní metadata
    """
    identifier: Optional[str] = Field(default=None, description="identifikátor uuid")
    date_created: Optional[datetime] = Field(default=None, description="Datum a čas")
    date_modified: Optional[datetime] = Field(default=None, description="Datum a čas")
    date_deleted: Optional[datetime] = Field(default=None, description="Datum a čas")
    deleted: Optional[bool] = Field(default=None, description="Dokument byl odstraněn")
    valid: Optional[bool] = Field(default=None, description="Dokument je platný/neplatný")
    duplicates: Optional[str] = Field(default=None, description="Dokument je duplicitní k jinému dokumentu s daným identifikátorem")



class MetadataTypeEntry(BaseModel):
    title: Optional[str] = Field(default=None, description='Název dokumentu')
    id_no: Optional[str] = Field(default=None, description='Číslo dokumentu', examples=['23CZ123456'])
    unid: Optional[str] = Field(default=None, description='Domino universal ID', examples=['3005277CB984B7FFC12587890060E2BF'])
    pid: Optional[str] = Field(default=None, description='Unique identifier', examples=['MBOA7HNBDJTR'])
    # uuid: Optional[UUID] = Field(default=None, description='Unique identifier')
    uuid: Optional[str] = Field(default=None, description='Unique identifier')
    form: Optional[str] = Field(default=None, description='Formulář', examples=['certificate'])
    authorized: Optional[bool] = Field(default=False, description='Dokument byl autorizován')
    archived: Optional[bool] = Field(default=False, description='Dokument byl archivován')
    deleted: Optional[bool] = Field(default=False, description='Dokument byl odstraněn')


class MetadataTypeBase(BaseModel):
    uuid_external: Optional[str] = Field(default=None, description='Unique identifier')
    title: Optional[str] = Field(default=None, description='Název dokumentu')
    id_no: Optional[str] = Field(default=None, description='Číslo dokumentu', examples=['23CZ123456'])
    id_no_local: Optional[str] = Field(default=None, description='Lokální číslo dokumentu', examples=['23CZ123456'])
    id_no_list: Optional[List[Optional[str]]] = Field(default=None, description='Seznam všech čísel dokumentu', examples=['23CZ123456'])
    creator: Optional[str] = Field(
        default=None,
        description='Tvůrce dokumentu - Subjekt primárně odpovědný za vytvoření dokument.',
        examples=['CN=Jan Novák/O=CITES/C=CZ'],
    )
    created_by_official: Optional[bool] = Field(default=False, description='Vytvořeno úředníkem')
    contributor: Optional[UserType] = Field(default=None, description='Přispěvatel (podílí se na obsahu dokumentu)')
    acl: Optional[List[Optional[AclType]]] = Field(default=None, description='seznam přístupových práv')
    comment: Optional[str] = Field(default=None, description='Libovolná poznámka k metadatům')


class MetadataType(MetadataTypeBase):
    date_created: Optional[datetime] = Field(
        default=local_now(),
        description='Datum a čas vytvoření dokumentu',
        examples=['2023-04-20T05:12:03Z'],
    )
    date_modified: Optional[datetime] = Field(
        default=local_now(),
        description='Datum a čas poslední úpravy dokumentu',
        examples=['2023-04-20T05:12:03Z'],
    )
    date_authorized: Optional[datetime] = Field(
        default=None,
        description='Datum a čas autorizace',
        examples=['2023-04-20T05:12:03Z'],
    )
    date_archived: Optional[datetime] = Field(
        default=None,
        description='Datum a čas archivace',
        examples=['2023-04-20T05:12:03Z'],
    )
    date_deleted: Optional[datetime] = Field(
        default=None,
        description='Datum a čas odstranění',
        examples=['2023-04-20T05:12:03Z'],
    )
    unid: Optional[str] = Field(default=None, description='Domino universal ID', examples=['3005277CB984B7FFC12587890060E2BF'])
    pid: Optional[str] = Field(default=None, description='Unique identifier', examples=['MBOA7HNBDJTR'])
    # uuid: Optional[UUID] = Field(default=None, description='Unique identifier')
    uuid: Optional[str] = Field(default=None, description='Unique identifier')
    form: Optional[str] = Field(default=None, description='Formulář', examples=['certificate'])
    authorized: Optional[bool] = Field(default=False, description='Dokument byl autorizován')
    archived: Optional[bool] = Field(default=False, description='Dokument byl archivován')
    deleted: Optional[bool] = Field(default=False, description='Dokument byl odstraněn')
    has_attachments: Optional[bool] = Field(default=False, description='Dokument má/nemá přílohy')
    # container: Optional[UUID] = Field(default=None, description='Identifikátor kontejneru, do kterého je dokument zařazen.')
    container: Optional[str] = Field(default=None, description='Identifikátor kontejneru, do kterého je dokument zařazen.')
    container_history: Optional[List[Optional[ContainerHistoryItemType]]] = Field(default=None, description='Historie kontejnerů')


class ListTypeBase(BaseModel):
    start: Optional[int] = Field(default=None, description='Počáteční dokument na stránce', examples=[0])
    page_size: Optional[int] = Field(default=None, description='Velikost stránky', examples=[10])
    page: Optional[int] = Field(default=None, description='Požadovaná stránka', examples=[0])
    count: Optional[int] = Field(default=None, description='celkový počet vrácených položek', examples=[25])


class LinkedType(BaseModel):
    # Identifikace pevně provázaného dokumemtu (nadřízený nebo jinak provázaný)
    title: Optional[str] = Field(default=None, description='Název provázaného dokumentu', examples=['Žádost o vydání permitu'])
    code: Optional[str] = Field(default=None, description='Kód vazby', examples=['CRŽP', 'CITS', 'IPPC'])
    id: Optional[str] = Field(default=None, description='Hlavní identifikátor', examples=['0c282c62-1918-4fbe-ad2c-e49a021f4801'])
    unid: Optional[str] = Field(default=None, description='Domino universal ID', examples=['3005277CB984B7FFC12587890060E2BF'])
    pid: Optional[str] = Field(default=None, description='PID (dvanáctimístný identifikátor', examples=['MBOA7HNBDJTR'])
    # uuid: Optional[UUID] = Field(default=None, description='Jednoznačný identifikátor', examples=['0c282c62-1918-4fbe-ad2c-e49a021f4801'])
    uuid: Optional[str] = Field(default=None, description='Jednoznačný identifikátor', examples=['0c282c62-1918-4fbe-ad2c-e49a021f4801'])


class GeoPointJtskType(BaseModel):
    x: Optional[float] = Field(default=None, description='JTSK - X', examples=[-1182833.13])
    y: Optional[float] = Field(default=None, description='JTSK - Y', examples=[-784886.70])


class GeoPointType(BaseModel):
    lat: Optional[float] = Field(default=None, description='WGS84 - latitude', examples=[-4.3202115])
    lon: Optional[float] = Field(default=None, description='WGS84 - longitude', examples=[55.7520211])


class MapSheet50Type(BaseModel):
    # objekt mapový list 1:50000
    id: Optional[str] = Field(default=None, description='Identifikátor mapového listu', examples=['03-44'])
    name: Optional[str] = Field(default=None, description='Název mapového listu', examples=['Dvůr Králové'])


class BasinType(BaseModel):
    # objekt povodí
    id: Optional[int] = Field(default=None, description='Identifikátor', examples=[4236])
    id_1: Optional[int] = Field(default=None, description='Identifikátor', examples=[1])
    id_2: Optional[int] = Field(default=None, description='Identifikátor', examples=[11])
    id_3: Optional[int] = Field(default=None, description='Identifikátor', examples=[49])
    chp: Optional[str] = Field(default=None, description='', examples=['1-11-04-0300-0-00'])
    chp_d: Optional[str] = Field(default=None, description='', examples=['1-11-04-0300-0-00'])
    chp_u: Optional[str] = Field(default=None, description='', examples=['1-11-04-0300-0-00'])
    basin_name_1: Optional[str] = Field(default=None, description='naz_pov_1', examples=['povodí Labe'])
    basin_name_2: Optional[str] = Field(default=None, description='naz_pov_2', examples=['Berounka od Úslavy po ústí'])
    basin_name_3: Optional[str] = Field(default=None, description='naz_pov_3', examples=['Litavka a Berounka od Litavky po Loděnici'])
    stream_name: Optional[str] = Field(default=None, description='naz_tok', examples=['Červený potok'])
    stream_name_2: Optional[str] = Field(default=None, description='naz_tok_2', examples=[''])


class LocationType(BaseModel):
    # Lokalita
    ruian_adm: Optional[int] = Field(default=None, description='Kód adresního místa RUIAN', examples=[21844895])
    ruian_adm_name: Optional[str] = Field(default=None, description='Název adresního místa RUIAN', examples=['Kaplanova 1931/1, 14800 Praha 11'])
    basin: Optional[BasinType] = Field(default=None, description='Povodí')
    sheet50: Optional[MapSheet50Type] = Field(default=None, description='Mapový list')
    street: Optional[str] = Field(default=None, description='Ulice nebo část obce a číslo popisné, evidenční, orientační', examples=['Kolmá 53/1230'])
    city: Optional[str] = Field(default=None, description='Název obce', examples=['Slepičí Lhota'])
    zip: Optional[str] = Field(default=None, description='PSČ', examples=['987 22'])
    region: Optional[str] = Field(default=None, description='Kraj', examples=['Středočeský kraj'])
    country: Optional[CodeValueType] = Field(default=None, description='Stát', examples=[{'code': 'SK', 'value': 'Slovensko'}])
    address_list: Optional[List[Optional[str]]] = Field(default=None, description='Seznam adresních položek', examples=['Kolmá 53/1230', 'Slepičí Lhota', '987 22', 'CZ'])
    note: Optional[str] = Field(default=None, description='Poznámka', examples=['Parcela číslo 113/7'])
    wgs: Optional[GeoPointType] = Field(default=None, description='WGS84')
    jtsk: Optional[GeoPointJtskType] = Field(default=None, description='JTSK')


class PersonCoreType(BaseModel):
    ico: Optional[str] = Field(default=None, description='IČO osoby')
    name: Optional[str] = Field(default=None, description='Název osoby', examples=['B.A.R. Reptofilia'])
    email: Optional[EmailStr] = Field(default=None, description='Email osoby')
    address: Optional[str] = Field(default=None, description='Adresa osoby (legacy)', examples=['Ulice Závodu Míru 2\n87423 Otrokovice'])
    country: Optional[CodeValueType] = Field(default=None, description='Země adresy osoby')

class PersonBaseType(PersonCoreType):
    # Osoba z Registru osob
    identifier: Optional[str] = Field(default=None, description='Hlavní jednoznačný identifikátor')
    unid: Optional[str] = Field(default=None, description='Domino universal ID', examples=['3005277CB984B7FFC12587890060E2BF'])
    pid: Optional[str] = Field(default=None, description='Unique identifier', examples=['MBOA7HNBDJTR'])
    uuid: Optional[str] = Field(default=None, description='Unique identifier (UUID)')
    person_printable: Optional[str] = Field(default=None, description='Název osoby pro tisk', examples=['B.A.R. Reptofilia'])
    main_person: Optional[LinkedType] = Field(default=None, description='Odkaz na hlavní osobu do registru')
    location: Optional[LocationType] = Field(default=None, description='Detailní adresa osoby (kompatibilní s CITES Toolkit)')
    linked_persons: Optional[List[Optional[LinkedType]]] = Field(default=None, description='Odkaz na další osoby do registru')

    def make_identifier(self) -> Optional[str]:
        if is_valid_unid(self.unid):
            self.identifier = self.unid
        if is_valid_pid(self.pid):
            self.identifier = self.pid
        if is_valid_uuid(self.uuid):
            self.identifier = str(self.uuid)
        return self.identifier

class WorkflowType(BaseModel):
    # Položka životního cyklu
    node_code: Optional[str] = Field(default=None, description='Kód schvalovacího  uzlu (APPROVE, AUTHORIZE, REJECT, ...)', examples=['APPROVE', 'AUTHORIZE', 'REJECT'])
    node_name: Optional[str] = Field(default=None, description='Název schvalovacího  uzlu (schválení, autorizace, ...)', examples=['Schválení'])
    responsible: Optional[PersonBaseType] = Field(default=None, description='Odpovědná osoba')
    date_execution: Optional[datetime] = Field(default=local_now(), description='Datum provedení')
    executor: Optional[UserType] = Field(default=None, description='Uživatel, který provedl událost')
    status_from: Optional[str] = Field(default=None, description='Předchozí stav')
    status_to: Optional[str] = Field(default=None, description='Následný stav')


class PhoneNumberType(BaseModel):
    """
    Telefonní číslo
    """
    name: Optional[str] = Field(default=None, description="Název telefonního čísla (mobil, práce, domů)")
    prefix: Optional[str] = Field(default=None, description="Národní prefix")
    number: Optional[str] = Field(default=None, description="Vlastní telefonní číslo")


class MailAddressType(BaseModel):
    """
    Adresa elektronické pošty
    """
    name: Optional[str] = Field(default=None, description="Název adresa elektronické pošty (práce, domů)")
    email: Optional[str] = Field(default=None, description="Adresa elektronické pošty")
