# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:         procedures
# Purpose:      Ident procedures
#
# Author:       Radim Jager
# Copyright:    (c) SYSNET s.r.o. 2019
# License:      CC BY-SA 4.0
# -------------------------------------------------------------------------------
import os
import uuid
from typing import Optional

import sysnet_pyutils.barcode as barcode

PID_PREFIX = os.getenv('PID_PREFIX', 'SNT')
ID_LENGTH = 12

DIGITS36 = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
            'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
            'U', 'V', 'W', 'X', 'Y', 'Z']


def to_id_string(ident_int):
    """
    Konvertuje numerický identifikátor na alfanumerický (modulo 36)

    :param ident_int:   Numerický identifikátor
    :return:    Alfanumerický identifikátor
    """
    out = ''
    w = ident_int
    while w > 0:
        c = DIGITS36[w % 36]
        out = c + out
        w = w // 36
    if out == '':
        out = '0'
    return out


def generate_tiny_uuid():
    """
    Vygeneruje 12místný identifikátor uuid

    :return:    12místný identifikátor uuid
    """
    u: uuid.UUID = uuid.uuid4()
    msb = to_id_string(u.time_hi_version)
    xsb = to_id_string(u.time_mid)
    lsb = to_id_string(u.time_low)
    out = '000000000000' + msb + xsb + lsb
    return out[-ID_LENGTH:]


def generate_id12(three_char_prefix: Optional[str]) -> str:
    """
    Vygeneruje 12místný alfanumerický identifikátor s pevným prefixem

    :param three_char_prefix:   Tříznakový prefix identifikátoru
    :return:    12místný alfanumerický identifikátor
    """
    out = PID_PREFIX
    if three_char_prefix is not None:
        out = three_char_prefix
    out = out[:3]
    identifier = generate_tiny_uuid()
    out += identifier[-9:]
    out = out.replace('$', 'S')
    return correct_pid(out)


def check_pid(pid: str) -> bool:
    """
    Kontroluje správnost PID pomocí kontrolního součtu

    :param pid: PID ke kontrole
    :return:    True/False
    """
    out = False
    if len(pid) == 12:
        pid = pid.upper()
        p_11 = pid[:11]
        p_last = pid[-1:]
        p_check = barcode.code39_mod36(p_11, 2)
        if p_last == p_check:
            out = True
    return out


def correct_pid(pid: str) -> str:
    """
    Opraví PID do korektní podoby. Doplní kontrolní součet.

    :param pid: PID k opravě
    :return:    Opravený PID
    """
    out = pid.upper()
    if not check_pid(out):
        p_11 = out[:11]
        p_check = barcode.code39_mod36(p_11, 2)
        out = p_11 + p_check
    return out


def generate_pid() -> str:
    """
    Vygeneruje nový PID

    :return:    PID
    """
    return generate_id12(None)
