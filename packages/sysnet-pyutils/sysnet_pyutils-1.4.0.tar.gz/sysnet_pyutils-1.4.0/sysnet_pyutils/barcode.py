# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:         barcode
# Purpose:      Barcode obsahuje podmnozinu funkci pro tvorbu carovych kodu
#
# Author:       Radim Jager
# Copyright:    (c) SYSNET s.r.o. 2019
# License:      CC BY-SA 4.0
# -------------------------------------------------------------------------------


def code39_pid(pid_to_encode, return_type):
    """
    Formátovat PID pro tisk čarovým kódem

    :param pid_to_encode:   PID k fomrmátování. Oriznou se vsechny znaky krome cislic a pismen.
    :param return_type:     0 - vystup je formatovan pro tisk carovym fontem
                            1 - vystup je formatovan pro ulozeni hodnoty
                            2 - vystupem je pouze kontrolni cislice (posledni znak kodu)
    :return:    Formátovaný PID
    """
    pid11 = pid_to_encode[:len(pid_to_encode)-1]
    return code39_mod36(pid11, return_type)


def code39_mod36(data_to_encode, return_type):
    """
    Formátovat data pro tisk čarovým kódem

    :param data_to_encode:  Vstupni data. Oriznou se vsechny znaky krome cislic a pismen.
    :param return_type:     0 - vystup je formatovan pro tisk carovym fontem
                            1 - vystup je formatovan pro ulozeni hodnoty
                            2 - vystupem je pouze kontrolni cislice (posledni znak kodu)
    :return:    Formátovaný text
    """
    if (return_type != 0) and (return_type != 1) and (return_type != 2):
        return_type = 0
    data_to_encode = data_to_encode.upper()
    data_to_print = ''
    weighted_total = 0

    # Check to make sure data is numeric, $, +, -, /, or :, and remove all others.
    char_list = list(data_to_encode)
    for c in char_list:
        if (ord(c) > 47) and (ord(c) < 58):
            data_to_print += str(c)
            weighted_total += ord(c) - 48
        elif (ord(c) > 64) and (ord(c) < 91):
            data_to_print += str(c)
            weighted_total += ord(c) - 55

    # Divide the weighted_total by 37 and get the remainder, this is the check_digit
    check_digit_value = weighted_total % 36
    check_digit = check_digit_value
    if check_digit_value < 10:
        check_digit += 48  # 0-9
    elif (check_digit_value < 36) and (check_digit_value > 9):
        check_digit += 55  # A-Z
    if return_type == 0:
        out = '!' + data_to_print + str(chr(check_digit)) + '!' + ' '
    elif return_type == 1:
        out = data_to_print + str(chr(check_digit))
    elif return_type == 2:
        out = str(chr(check_digit))
    else:
        out = None
    return out
