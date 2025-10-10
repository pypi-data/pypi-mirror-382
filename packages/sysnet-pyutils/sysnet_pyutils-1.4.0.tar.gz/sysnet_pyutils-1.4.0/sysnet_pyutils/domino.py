from datetime import date, datetime

import pytz

from utils import TZ


class DdsDictionaryFactory:
    """
    Třída pro získávání hodnot z dokumentu Notes v podobě dictionary
    Tyto dokumenty vrací služba HCL Domino Data Service
    """
    def __init__(self, data):
        if not isinstance(data, dict):
            raise ValueError('Invalid data')
        self.data = data

    def get_value(self, item_name):
        if item_name in self.data:
            return self.data[item_name]
        return None

    def get_value_string(self, item_name):
        v = self.get_value(item_name)
        out = ''
        if v not in [None, '']:
            out = v
        return out

    def get_value_bool(self, item_name):
        v = self.get_value(item_name)
        out = False
        if (v not in [None, '']) and v == '1':
            out = True
        return out

    def get_value_float(self, item_name, spare_itemname=None):
        v = self.get_value(item_name)
        out = 0.0
        if v is not None:
            out = float(v)
        if (out == 0.0) and (spare_itemname is not None):
            v1 = self.get_value(spare_itemname)
            if v1 is not None:
                out = float(v1)
        return out

    def get_value_int(self, item_name, spare_itemname=None):
        v = self.get_value(item_name)
        out = 0
        if v is not None:
            out = int(v)
        if (out == 0) and (spare_itemname is not None):
            v1 = self.get_value(spare_itemname)
            if v1 is not None:
                out = int(v1)
        return out

    def get_value_date(self, item_name):
        v = self.get_value(item_name)
        if v is None:
            return None
        try:
            out = date.fromisoformat(v)
            return out
        except [ValueError, TypeError]:
            return None

    def get_value_datetime(self, item_name):
        v = self.get_value(item_name)
        if v is None:
            return None
        try:
            out = datetime.fromisoformat(v)
            local_tz = pytz.timezone(TZ)
            out = out.astimezone(local_tz)
            return out
        except [ValueError, TypeError]:
            return None

    def set_value(self, item_name, value):
        self.data[item_name] = value

    def set_value_string(self, item_name, value):
        v = ''
        if value is not None:
            v = str(value)
        self.set_value(item_name, v)

    def set_value_bool(self, item_name, value):
        v = None
        if value is not None:
            if bool(value):
                v = '1'
        self.set_value(item_name, v)

    # TODO další settery
