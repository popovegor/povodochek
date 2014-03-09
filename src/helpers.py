#!/usr/bin/python
# -*- coding: utf-8 -*-


from flask import (Markup)
from pymorphy2 import MorphAnalyzer
import re
from datetime import datetime

def str2date(str_date, format = "%d/%m/%Y"):
    dt = None
    try:
        return datetime.strptime(str_date, format)
    except ValueError, e:
        print(e)
    return None    

def date2str(dt, format = "%d/%m/%Y"):
    try:
        return dt.strftime(format) if dt else None
    except ValueError, e:
         print(e)
    return None

def num(value, default = None):
    if (isinstance(value, str) or \
        isinstance(value, unicode)) and value.isdigit():
        return int(value)
    elif isinstance(value, int):
        return value
    elif isinstance(value, float):
        return int(value)
    return default

def qoute_rus(msg):
    return Markup(u"&#8222;%s&#8220;" % msg)

#pymorphy

morph = MorphAnalyzer()

def morph_restore_register(morphed_word, word):
    """ Восстановить регистр слова """
    if '-' in word:
        parts = zip(morphed_word.split('-'), word.split('-'))
        return '-'.join(morph_restore_register(*p) for p in parts)
    if word.isupper():
        return morphed_word.upper()
    elif word.islower():
        return morphed_word.lower()
    elif word.istitle():
        return morphed_word.title()
    else:
        return morphed_word.lower()

def morph_word(word, grammemes = None, count = None):
    morphed_word = word
    if word:
        parts = re.findall(u"[а-яА-Я-]+", word, re.U | re.I)
        for part in filter(lambda x: len(x) > 2, parts):
            parse = morph.parse(part)
            morphed_part = part
            if grammemes:
                grammemes = set(grammemes)
                inflect_word = parse[0].inflect(grammemes) if parse[0] else None
                morphed_part = inflect_word.word if inflect_word else part
            elif count >= 0:
                morphed_part = parse[0].make_agree_with_number(count).word if parse[0] else part
            morphed_part = morph_restore_register(morphed_part, part)
            morphed_word = morphed_word.replace(part, morphed_part)
    return morphed_word

if __name__ == "__main__":
    import glob
    for infile in glob.glob("/tmp/*.*"):
        create_thumbnail(infile)