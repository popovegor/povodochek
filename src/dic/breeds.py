#!/usr/bin/env 
# -*- coding: utf-8 -*-

dogs = {
1: u"Австралийская короткохвостая пастушья",
2: u"Австралийская овчарка",
3: u"Австралийский шелковистый терьер",
4: u"Акита ину",
5: u"Аляскинский маламут",
6: u"Американская акита",
7: u"Американский бульдог",
8: u"Американский кокер спаниель",
9: u"Американский питбультерьер",
10: u"Американский стаффордширский терьер",
11: u"Американский той фокстерьер",
12: u"Английский бульдог",
13: u"Английский кокер спаниель",
14: u"Английский мастиф",
15: u"Английский пойнтер",
16: u"Английский сеттер",
17: u"Аргентинский дог",
18: u"Афганская борзая",
19: u"Аффенпинчер",
20: u"Басенджи",
21: u"Бассет хаунд",
22: u"Бедлингтон терьер",
23: u"Белая швейцарская овчарка",
24: u"Бельгийская овчарка малинуа",
25: u"Бельгийский гриффон",
26: u"Бернский зенненхунд",
27: u"Бивер йорк",
28: u"Бигль",
29: u"Бишон фризе",
30: u"Бобтейл (староанглийская овчарка)",
31: u"Боксер (немецкий)",
32: u"Болонез (болонский бишон)",
33: u"Большая пиренейская",
34: u"Бордер колли",
35: u"Бордер терьер",
36: u"Бордоский дог",
37: u"Бородатая колли",
38: u"Босерон",
39: u"Бостон терьер",
40: u"Бриар (французская овчарка)",
41: u"Брюссельский гриффон",
42: u"Бульмастиф",
43: u"Бультерьер",
44: u"Веймаранер (веймарская легавая)",
45: u"Вельш корги кардиган",
46: u"Вельш корги пемброк",
47: u"Вельш терьер",
48: u"Венгерская короткошерстная легавая (выжла)",
49: u"Вест хайленд уайт терьер",
50: u"Восточно-европейская овчарка",
51: u"Восточносибирская лайка",
52: u"Гладкошёрстный фокстерьер",
53: u"Грейхаунд",
54: u"Гриффон кортальса",
55: u"Далматин",
56: u"Денди динмонт терьер",
57: u"Джек рассел терьер",
58: u"Доберман",
59: u"Дратхаар",
60: u"Западносибирская лайка",
61: u"Золотистый (голден) ретривер",
62: u"Ирландский волкодав",
63: u"Ирландский мягкошерстный пшеничный терьер",
64: u"Ирландский сеттер",
65: u"Ирландский терьер",
66: u"Испанский мастиф",
67: u"Итальянский бракк",
68: u"Йоркширский терьер",
69: u"Кавалер кинг чарльз спаниель",
70: u"Кавказская овчарка",
71: u"Ка Де Бо",
72: u"Канарская",
73: u"Итальянский кане корсо",
74: u"Карело-финская лайка",
75: u"Карликовый пинчер (цвергпинчер)",
76: u"Немецкий шпиц (Кеесхонд)",
77: u"Керн терьер",
78: u"Керри блю терьер",
79: u"Китайская хохлатая собака",
80: u"Кламбер спаниель",
81: u"Колли длинношерстная (шотландская овчарка)",
82: u"Комондор",
83: u"Лабрадор ретривер",
84: u"Левретка (итальянский грейхаунд)",
85: u"Леонбергер",
86: u"Лхаский апсо",
87: u"Мальтезе (мальтийская болонка)",
88: u"Мареммо-абруцкая овчарка",
89: u"Мексиканская голая собака",
90: u"Метис",
91: u"Миниатюрный бультерьер",
92: u"Миттельшнауцер",
93: u"Мопс",
94: u"Московская сторожевая",
95: u"Неаполитанский мастиф",
96: u"Немецкая овчарка длинношерстная",
97: u"Немецкая овчарка",
98: u"Немецкий дог",
99: u"Немецкий курцхаар",
100: u"Немецкий шпиц (Малый)",
101: u"Немецкий шпиц (Средний)",
102: u"Немецкий ягдтерьер",
103: u"Норвич терьер",
104: u"Ньюфаундленд",
105: u"Континентальный спаниель (папийон, фален)",
106: u"Парсон рассел терьер",
107: u"Пекинес",
108: u"Перуанская голая собака",
109: u"Петербургская орхидея",
110: u"Пинчер немецкий",
111: u"Пиренейская овчарка длинношерстная",
112: u"Польская подгалянская овчарка",
113: u"Немецкий шпиц (Померанский)",
114: u"Пражский крысарик",
115: u"Прямошерстный ретривер",
116: u"Пти брабансон",
117: u"Пудель большой (стандартный королевский пудель)",
118: u"Пудель карликовый (миниатюрный)",
119: u"Пудель малый",
120: u"Пудель той",
121: u"Ризеншнауцер",
122: u"Родезийский риджбек",
123: u"Ротвейлер",
124: u"Русская гончая",
125: u"Русская пегая гончая",
126: u"Русская псовая борзая",
127: u"Русская цветная болонка",
128: u"Русский охотничий спаниель",
129: u"Русский той терьер",
130: u"Русско-европейская лайка",
131: u"Салюки (арабская борзая)",
132: u"Самоед (самоедская собака)",
133: u"Сенбернар",
134: u"Сеттер гордон (шотландский)",
135: u"Сиба-ину",
136: u"Сибирская ездовая собака",
137: u"Силихем терьер",
138: u"Скай терьер",
139: u"Скотч терьер",
140: u"Словацкий чувач",
141: u"Английский спрингер спаниель",
142: u"Среднеазиатская овчарка (алабай)",
143: u"Стаффордширский бультерьер",
144: u"Тайский риджбек",
145: u"Такса гладкошерстная",
146: u"Такса жесткошерстная",
147: u"Такса карликовая",
148: u"Такса кроличья",
149: u"Такса стандартная",
150: u"Тибетский мастиф",
151: u"Тибетский спаниель",
152: u"Тибетский терьер",
153: u"Английский той терьер",
154: u"Тувинская овчарка",
155: u"Уиппет",
156: u"Фараонова собака",
157: u"Финская гончая",
158: u"Фландрский бувье",
159: u"Фокстерьер гладкошерстный",
160: u"Фокстерьер жесткошерстный",
161: u"Французский бульдог",
162: u"Хаски (сибирский)",
163: u"Ховаварт",
164: u"Хортая борзая",
165: u"Цвергшнауцер",
166: u"Чау-чау",
167: u"Русский черный терьер",
168: u"Чехословацкая волчья собака",
169: u"Чихуахуа",
170: u"Шарпей",
171: u"Шелти",
172: u"Ши тцу",
174: u"Шипперке",
175: u"Энтлебухер зенненхунд",
176: u"Эрдельтерьер",
177: u"Эстонская гончая",
178: u"Южноафриканский бурбуль",
179: u"Южнорусская овчарка",
180: u"Ягдтерьер",
181: u"Японский хин",
182: u"Японский шпиц",
183: u"Русская салонная собака (русалка)",
184: u"Норфолк терьер",
185: u"Немецкий шпиц (Большой)",
}


cats = {
    1002:u"Абиссинская",
    1003:u"Американская короткошёрстная",
    1004:u"Американский бобтейл",
    1005:u"Американский кёрл",
    1007:u"Балинезийская",
    1008:u"Бенгальская",
    1009:u"Бомбейская",
    1010:u"Британская короткошёрстная",
    1011:u"Бурманская",
    1054:u"Бурмилла",
    1012:u"Гавана",
    1014:u"Девон-рекс",
    1015:u"Донской сфинкс",
    1018:u"Египетская мау",
    1019:u"Канадский сфинкс",
    1020:u"Корат",
    1021:u"Корниш-рекс",
    1060:u"Курильский бобтейл",
    1101:u"Манчкин",
    1023:u"Мейн-кун",
    1022:u"Меконгский бобтейл",
    1024:u"Мэнкс",
    1025:u"Невская маскарадная",
    1061:u"Немецкий рекс",
    1026:u"Нибелунг",
    1027:u"Норвежская лесная",
    1028:u"Ориентальная короткошёрстная",
    1062:u"Ориентальная полудлинношёрстная",
    1029:u"Оцикэт",
    1030:u"Персидская",
    1063:u"Петерболд",
    1064:u"Петербургский сфинкс",
    1065:u"Пиксибоб",
    1102:u"Рагамаффин",
    1033:u"Русская голубая",
    1032:u"Рэгдолл",
    1034:u"Священная бирма",
    1066:u"Селкирк рекс",
    1035:u"Сиамская",
    1036:u"Сибирская",
    1037:u"Сингапурская",
    1038:u"Скоттиш фолд",
    1039:u"Сомали",
    1067:u"Тайская",
    1068:u"Тойгер",
    1041:u"Тонкинская",
    1006:u"Турецкая ангора",
    1042:u"Турецкий ван",
    1043:u"Украинский левкой",
    1044:u"Шартрез",
    1071:u"Экзотическая короткошёрстная",
    1048:u"Японский бобтейл"
}

from dic.pets import (pets, DOG_ID, CAT_ID)
from helpers import (num)
from pymongo import (MongoClient)

breeds = dict([(dog, {'name':dog_name, 'pet':DOG_ID}) for (dog, dog_name) in dogs.items()] + \
	[(cat, {'name': cat_name, 'pet': CAT_ID}) for (cat, cat_name) in cats.items()])


def get_breed_by_name(name):
    if name:
        name = name.lower()
        _dogs = [dog_id for (dog_id, dog_name) in dogs.items() if dog_name.lower() in name]
        if _dogs:
            return (_dogs[0], DOG_ID)
        _cats = [cat_id for (cat_id, cat_name) in cats.items() if cat_name.lower() in name]
        if _cats:
            return (_cats[0], CAT_ID)

    return (None, None)

def get_breed_by_id(breed_id):
	if breed_id:
	 	breed_id = num(breed_id)
	 	if breed_id in breeds:
	 		return (breed_id, breeds[breed_id]['pet'])
	return (None, None)

def get_breed_name(breed_id, pet_id):
    breed_id = num(breed_id or 0)
    breed = breeds.get(breed_id)
    return breed.get("name") if breed else u""

def get_breed_dog_name(breed_id):
    breed_id = num(breed_id or 0)
    return dogs.get(breed_id) or u""

def get_breed_cat_name(breed_id):
    breed_id = num(breed_id or 0)
    return cats.get(breed_id) or u""

import random
from bson.objectid import ObjectId
from pets import pets

def shuffle_breeds_in_advs():
    c = MongoClient()
    db = c['povodochek']
    for adv in db.sales.find():
        pet_id = random.choice(pets.keys())
        breed_id = random.choice((dogs if pet_id == 1 else cats).keys())
        db.sales.update(adv, \
            {'$set': {'breed_id': breed_id, 'pet_id' : pet_id}}, upsert = False)

if __name__ == '__main__':
    #shuffle_breeds_in_advs()
    pass
