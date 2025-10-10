from datetime import date, datetime
from typing import Union, List, Any, Optional
from uuid import UUID

import pytz

from sysnet_pyutils.models.general import CodeValueType
from sysnet_pyutils.utils import is_valid_email, TZ, is_valid_uuid

PAGE_SIZE = 10

def get_dict_value(data: dict, item_name: str) -> Union[Any, None]:
    """
    Extrahuje hodnotu ze slovníku. Používá se pro load dat JSON do objektů

    :param data:        Slovník s daty JSON
    :param item_name:   Název položky
    :return:            Hodnota
    """
    if data is None or item_name in [None, '']:
        return None
    if item_name in data:
        return data[item_name]
    return None


def get_dict_value_string(data: dict, item_name: str) -> str:
    """
    Extrahuje textovou hodnotu ze slovníku. Pokud je vstupní hodnota None, vrací prázdný string.

    :param data:        Slovník s daty JSON
    :param item_name:   Název položky
    :return:            Hodnota
    """
    out = ''
    if data is None or item_name in [None, '']:
        return out
    v = get_dict_value(data, item_name)
    if v not in [None, '']:
        out = str(v)
    return out


def get_dict_value_email(data: dict, item_name: str) -> Union[Any, None]:
    """
    Extrahuje emailovou adresu ze slovníku.

    :param data:        Slovník s daty JSON
    :param item_name:   Název položky
    :return:            Hodnota
    """
    if data is None or item_name in [None, '']:
        return None
    out = get_dict_value(data, item_name)
    if not is_valid_email(out):
        return None
    return out


def get_dict_value_bool(data: dict, item_name: str) -> bool:
    """
    Extrahuje logickou hodnotu ze slovníku

    :param data:        Slovník s daty JSON
    :param item_name:   Název položky
    :return:            Hodnota
    """
    if data is None or item_name in [None, '']:
        return False
    v = get_dict_value(data, item_name)
    if v in [None, '']:
        return False
    if v.lower() in ('true', '1', 't', 'ano', 'a', 'on', 'yes', 'y'):
        return True
    return False


def get_dict_value_int(data: dict, item_name: str, spare_item_name: Union[str, None] = None) -> int:
    """
    Extrahuje celočíselnou hodnotu ze slovníku. Pokud nenajde hlavní položku, hledá záložní.

    :param data:                Slovník s daty JSON
    :param item_name:           Název položky
    :param spare_item_name:     Název záložní položky
    :return:                    Hodnota
    """
    if data is None or item_name in [None, '']:
        return 0
    v = get_dict_value(data, item_name)
    out = 0
    if v is not None:
        try:
            out = int(v)
        except (ValueError, TypeError):
            out = 0
    if (out == 0) and (spare_item_name is not None):
        v1 = get_dict_value(data, spare_item_name)
        if v1 is not None:
            try:
                out = int(v1)
            except (ValueError, TypeError):
                out = 0
    return out


def get_dict_value_list(data: dict, item_name: str, spare_item_name: str = None) -> Union[List[str], None]:
    v = get_dict_value(data, item_name)
    if v in [None, '']:
        v = get_dict_value(data, spare_item_name)
    if v in [None, '']:
        return None
    out = [i.strip() for i in v[1:-1].replace('"',"").split(';')]
    if len(out) == 1 and out[0] == '':
        out = []
    return out


def get_dict_value_float(data: dict, item_name: str, spare_item_name: str = None) -> Union[float, None]:
    v = get_dict_value(data, item_name)
    out: float = float(0)
    if v is not None:
        try:
            if isinstance(v, str):
                v = v.replace(',', '.')
            out = float(v)
        except (ValueError, TypeError):
            out = float(0)
    if (out == float(0)) and (spare_item_name is not None):
        v1 = get_dict_value(data, spare_item_name)
        if v1 is not None:
            try:
                out = float(v1)
            except (ValueError, TypeError):
                out = float(0)
    return out


def get_dict_value_date(data: dict, item_name: str) -> Union[date, None]:
    """
    Konvertuje ISO nebo český formát do data

    :param data:
    :param item_name:
    :return:
    """
    v = get_dict_value(data, item_name)
    if v is None:
        return None
    out = convert_iso_to_date(v)
    if out is None:
        out = convert_cz_to_date(v)
    return out


def get_dict_value_code(data: dict, item_name: str) -> Optional[CodeValueType]:
    code = get_dict_value(data=data, item_name=item_name)
    if code is None:
        return None
    if '|' in code:
        cv = code.split('|')
        out = CodeValueType(code=cv[1], value=cv[0])
    else:
        value = None
        if str(code).upper() == 'CZ':
            value = 'Česká republika / Czech Republic'
        out = CodeValueType(code=code, value=value)
    return out


def get_dict_value_uuid(data: dict, item_name: str) -> Optional[str]:
    out = None
    code = get_dict_value(data=data, item_name=item_name)
    if code is None:
        return None
    if is_valid_uuid(str(code)):
        out = str(UUID(code))
    return out


def convert_iso_to_date(text: str) -> Union[date, None]:
    try:
        out = date.fromisoformat(text)
        return out
    except (ValueError, TypeError):
        return None


def convert_iso_to_datetime(text: str) -> Union[datetime, None]:
    try:
        out = datetime.fromisoformat(text)
        local_tz = pytz.timezone(TZ)
        out = out.astimezone(local_tz)
        return out
    except (ValueError, TypeError):
        return None


def convert_cz_to_date(text: str) -> Union[date, None]:
    try:
        out = datetime.strptime(text, '%d.%m.%Y').date()
        return out
    except (ValueError, TypeError):
        return None


def convert_cz_to_datetime(text: str) -> Union[datetime, None]:
    try:
        out = datetime.strptime(text, '%d.%m.%Y %H:%M:%S')
        local_tz = pytz.timezone(TZ)
        out = out.astimezone(local_tz)
        return out
    except (ValueError, TypeError):
        return None


def get_dict_value_datetime(data: dict, item_name: str) -> Union[datetime, None]:
    """
    Konvertuje ISO nebo český formát do datatime

    :param data:
    :param item_name:
    :return:
    """
    v = get_dict_value(data, item_name)
    out = None
    if v is None:
        return None
    try:
        if isinstance(v, datetime):
            return v
        elif isinstance(v, date):
            gmt_tz = pytz.timezone('GMT')
            return datetime(year=v.year, month=v.month, day=v.day, tzinfo=gmt_tz)
        elif isinstance(v, str):
            out = convert_iso_to_datetime(v)
            if out is None:
                out = convert_cz_to_datetime(v)
        return out
    except (ValueError, TypeError):
        return None


def get_object_attr(obj: Any, attr: str) -> Union[Any, None]:
    """
    Získa hodnotu atributu z datového objektu

    :param obj:
    :param attr:
    :return:
    """
    if obj is None:
        return None
    if hasattr(obj, attr):
        return getattr(obj, attr)
    return None


def get_dict_item_value_list(data: dict, item_name: str, alt_item_names: List[str] = None) -> Union[list, None]:
    out = []
    v = get_dict_item_value(data=data, item_name=item_name, alt_item_names=alt_item_names, blank=False)
    if v is None:
        return out
    if isinstance(v, list):
        out = v
    else:
        out.append(v)
    return out


def get_dict_item_value(data: dict, item_name: str, alt_item_names: List[str] = None, blank=True) -> Union[Any, None]:
    out = None
    if blank:
        out = ''
    if (data is None) or (item_name is None):
        return out
    if item_name in data:
        out = data[item_name]
    elif alt_item_names is not None:
        if alt_item_names:
            for name in alt_item_names:
                if name in data:
                    out = data[name]
                    break
    return out


def get_dict_code_value_list(data: dict, item_name_code: str, item_name_value: str) -> Union[list[tuple[Any, Any]], None]:
    """
    Vrátí z dvojice položek slovníku tuple code/value

    :param data:
    :param item_name_code:
    :param item_name_value:
    :return:
    """
    codes = get_dict_value_list(data, item_name_code)
    values = get_dict_value_list(data, item_name_value)
    if not codes or not values:
        return None
    if len(codes) != len(values):
        return None
    out = []
    i = 0
    for c in codes:
        v = values[i]
        i += 1
        out.append((c,v))
    return out

def adjust_datetime_to_utc(date_value: Union[date, datetime], for_store: bool = False) -> Union[datetime, date]:
    """
    Nastavení času pro uložení. Použije se časová zóna UTF

    :param date_value:      Datová hodnota
    :param for_store:       Pro uložení (převede se vždy na datetime)
    :return:                nastavená hodnota
    """
    if date_value in [None, '']:
        return date_value
    if for_store:
        if isinstance(date_value, date):
            return datetime(year=date_value.year, month=date_value.month, day=date_value.day, tzinfo=pytz.UTC)
    if isinstance(date_value, datetime):
        if date_value.tzinfo is None:
            date_value.replace(tzinfo=pytz.UTC)
        return date(year=date_value.year, month=date_value.month, day=date_value.day)
    return date_value


def dict_convert_date_to_str(data: dict):
    """
    Rekurzivně převede všechny časové položky ve slovníku na ISO text

    :param data:    dictionary
    :return:
    """
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, datetime):
                if v.tzinfo is None:
                    v_gmt = v.replace(tzinfo=pytz.utc)
                else:
                    v_gmt = v.astimezone(pytz.utc)
                data[k] = v_gmt.strftime('%Y-%m-%dT%H:%M:%SZ')
            elif isinstance(v, dict):
                dict_convert_date_to_str(v)
            elif isinstance(v, list):
                for item in v:
                    dict_convert_date_to_str(item)
            else:
                pass


def paging_to_mongo(start=0, page_size=PAGE_SIZE, page=0):
    if start is None:
        start = 0
    if page_size is None:
        page_size = PAGE_SIZE
    if page is None:
        page = 0
    page += start // page_size
    start = start % page_size
    # pokud pocatecni dokument nesouhlasí se začátkem stránky, zkrátí se stránka
    skip = start + page * page_size
    limit = page_size
    if start != 0:
        limit = page_size - start
    out = {
        'start': start,
        'page_size': page_size,
        'page': page,
        'skip': skip,
        'limit': limit}
    return out


def recursive_update(out_object, original, updated):
    """
    Rekurzivní aktualizace slovníků

    :param out_object:  Datový objekt k aktualizaci
    :param original:    Uložený slovník
    :param updated:     Aktualizace (dodaná metodou PUT)
    :return:            Aktualizovaný původní slovník
    """
    out = original
    for k, v in updated.items():
        if k not in out:
            # Ignoruj položky, které nejsou v originále
            continue
        if (v is None) and (isinstance(out.get(k), dict) or isinstance(out.get(k), list)):
            # Pokud je místo slovníku nebo seznamu None, přeskočit
            continue
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            # Pokud je aktualizován slovník, rekurze
            recursive_update(getattr(out_object, k), out[k], v)
        else:
            out[k] = v
            setattr(out_object, k, v)
    return out
