#!/usr/bin/python
# -*- coding: utf-8 -*-

city_metro = {}

city_metro[1] = {
	#1. Кировско-Выборгская линия: 
	1000: u"Девяткино",
	1001: u"Гражданский проспект",
	1002: u"Академическая",
	1003: u"Политехническая",
	1004: u"Площадь Мужества",
	1005: u"Лесная",
	1006: u"Выборгская",
	1007: u"Площадь Ленина",
	1008: u"Чернышевская",
	1009: u"Площадь Восстания",
	1010: u"Владимирская",
	1011: u"Пушкинская",
	1012: u"Технологический институт",
	1013: u"Балтийская",
	1014: u"Нарвская",
	1015: u"Кировский завод",
	1016: u"Автово",
	1017: u"Ленинский проспект",
	1018: u"Проспект Ветеранов",

	#2. Московско-Петроградская линия: 
	1019: u"Парнас",
	1020: u"Проспект Просвещения",
	1021: u"Озерки",
	1022: u"Удельная",
	1023: u"Пионерская",
	1024: u"Чёрная речка",
	1025: u"Петроградская",
	1026: u"Горьковская",
	1027: u"Невский проспект",
	1028: u"Сенная площадь",
	#1029: u"Технологический институт",
	1030: u"Фрунзенская",
	1031: u"Московские ворота",
	1032: u"Электросила",
	1033: u"Парк Победы",
	1034: u"Московская",
	1035: u"Звёздная",
	1036: u"Купчино",

	#3. Невско-Василеостровская линия: 
	1037: u"Приморская",
	1038: u"Василеостровская",
	1039: u"Гостиный двор",
	1040: u"Маяковская",
	1041: u"Площадь Александра Невского-1",
	1042: u"Елизаровская",
	1043: u"Ломоносовская",
	1044: u"Пролетарская",
	1045: u"Обухово",
	1046: u"Рыбацкое",

	#4. Правобережная линия: 
	1047: u"Спасская",
	1048: u"Достоевская",
	1049: u"Лиговский проспект",
	1050: u"Площадь Александра Невского-2",
	1051: u"Новочеркасская",
	1052: u"Ладожская",
	1053: u"Проспект Большевиков",
	1054: u"Улица Дыбенко",

	#5. Фрунзенско-Приморская линия: 
	1055: u"Комендантский проспект",
	1056: u"Старая Деревня",
	1057: u"Крестовский остров",
	1058: u"Чкаловская",
	1059: u"Спортивная",
	1060: u"Садовая",
	1061: u"Звенигородская",
	1062: u"Волковская"
}

city_metro[3611] = {
	#1. Сокольническая линия: 
	1 : u"Улица Подбельского",
	2 : u"Черкизовская",
	3 : u"Преображенская Площадь",
	4 : u"Сокольники",
	5 : u"Красносельская",
	6 : u"Комсомольская",
	7 : u"Красные Ворота",
	8 : u"Чистые пруды",
	9 : u"Лубянка",
	10 : u"Охотный Ряд",
	11 : u"Библиотека имени Ленина",
	12 : u"Кропоткинская",
	13 : u"Парк культуры",
	14 : u"Фрунзенская",
	15 : u"Спортивная",
	16 : u"Воробьевы горы",
	17 : u"Университет",
	18 : u"Проспект Вернадского",
	19 : u"Юго-Западная",

	#2. Замоскворецкая линия: 
	20: u"Речной Вокзал",
	21: u"Водный Стадион",
	22: u"Войковская",
	23: u"Сокол",
	24: u"Аэропорт",
	25: u"Динамо",
	26: u"Белорусская",
	27: u"Маяковская",
	28: u"Тверская",
	29: u"Театральная",
	30: u"Новокузнецкая",
	31: u"Павелецкая",
	32: u"Автозаводская",
	33: u"Коломенская",
	34: u"Каширская",
	35: u"Кантемировская",
	36: u"Царицыно",
	37: u"Орехово",
	38: u"Домодедовская",
	39: u"Красногвардейская",

	#3. Арбатско-Покровская линия: 
	40: u"Строгино",
	41: u"Крылатское",
	42: u"Молодежная",
	43: u"Кунцевская",
	44: u"Славянский бульвар",
	45: u"Парк Победы",
	47: u"Смоленская",
	48: u"Арбатская",
	49: u"Площадь Революции",
	50: u"Курская",
	51: u"Бауманская",
	52: u"Электрозаводская",
	53: u"Семеновская",
	54: u"Партизанская",
	55: u"Измайловская",
	56: u"Первомайская",
	57: u"Щелковская",

	#4. Филевская линия: 
	58: u"Выставочная (стар. Международная)",
	59: u"Деловой центр",
	60: u"Кунцевская",
	61: u"Пионерская",
	62: u"Филевский Парк",
	63: u"Багратионовская",
	64: u"Фили",
	65: u"Кутузовская",
	66: u"Студенческая",
	68: u"Смоленская",
	69: u"Арбатская",
	70: u"Александровский Сад",

	#5. Кольцевая линия: 
	71: u"Белорусская",
	72: u"Новослободская",
	74: u"Комсомольская",
	75: u"Курская",
	77: u"Павелецкая",
	78: u"Добрынинская",
	79: u"Октябрьская",
	80: u"Парк Культуры",
	81: u"Киевская",
	82: u"Краснопресненская",

	#6. Калужско-Рижская линия: 
	83: u"Медведково",
	84: u"Бабушкинская",
	85: u"Свиблово",
	86: u"Ботанический Сад",
	87: u"ВДНХ",
	88: u"Алексеевская",
	89: u"Рижская",
	90: u"Проспект Мира",
	91: u"Сухаревская",
	92: u"Тургеневская",
	94: u"Третьяковская",
	95: u"Октябрьская",
	96: u"Шаболовская",
	97: u"Ленинский Проспект",
	98: u"Академическая",
	99: u"Профсоюзная",
	100: u"Новые Черёмушки",
	101: u"Калужская",
	102: u"Беляево",
	103: u"Коньково",
	104: u"Теплый Стан",
	105: u"Ясенево",
	106: u"Новоясеневская (стар. Битцевский Парк)",

	#7. Таганско-Краснопресенская линия: 
	107: u"Планерная",
	108: u"Сходненская",
	109: u"Тушинская",
	110: u"Щукинская",
	111: u"Октябрьское Поле",
	112: u"Полежаевская",
	113: u"Беговая",
	114: u"Улица 1905 года",
	115: u"Баррикадная",
	116: u"Пушкинская",
	117: u"Кузнецкий Мост",
	118: u"Китай-город",
	119: u"Таганская",
	120: u"Пролетарская",
	121: u"Волгоградский Проспект",
	122: u"Текстильщики",
	123: u"Кузьминки",
	124: u"Рязанский Проспект",
	125: u"Выхино",

	#8. Калининская линия: 
	126: u"Третьяковская",
	127: u"Марксистская",
	128: u"Площадь Ильича",
	129: u"Авиамоторная",
	130: u"Шоссе Энтузиастов",
	131: u"Перово",
	132: u"Новогиреево",

	#9. Серпуховско-Тимирязевская линия: 
	133: u"Алтуфьево",
	134: u"Бибирево",
	135: u"Отрадное",
	136: u"Владыкино",
	137: u"Петровско-Разумовская",
	138: u"Тимирязевская",
	139: u"Дмитровская",
	140: u"Савеловская",
	141: u"Менделеевская",
	142: u"Цветной Бульвар",
	143: u"Чеховская",
	144: u"Боровицкая",
	145: u"Полянка",
	146: u"Серпуховская",
	147: u"Тульская",
	148: u"Нагатинская",
	149: u"Нагорная",
	150: u"Нахимовский Проспект",
	151: u"Севастопольская",
	152: u"Чертановская",
	153: u"Южная",
	154: u"Пражская",
	155: u"Улица Академика Янгеля",
	156: u"Аннино",
	157: u"Бульвар Дмитрия Донского",

	#10. Люблинская линия: 
	158: u"Трубная",
	159: u"Сретенский бульвар",
	160: u"Чкаловская",
	161: u"Римская",
	162: u"Крестьянская застава",
	163: u"Дубровка",
	164: u"Кожуховская",
	165: u"Печатники",
	166: u"Волжская",
	167: u"Люблино",
	168: u"Братиславская",
	169: u"Марьино",

	#11. Каховская линия:
	171: u"Варшавская",
	172: u"Каховская",

	#12. Бутовская линия:
	173: u"Улица Старокачаловская",
	174: u"Улица Скобелевская",
	175: u"Бульвар адмирала Ушакова",
	176: u"Улица Горчакова",
	177: u"Бунинская аллея"
}

city_metro[135] = {
	#Автозаводская линия: 
	4000: u"Московская",
	4001: u"Чкаловская",
	4002: u"Ленинская",
	4003: u"Заречная",
	4004: u"Двигатель Революции",
	4005: u"Пролетарская",
	4006: u"Автозаводская",
	4008: u"Кировская",
	4009: u"Парк Культуры",

	#2. Сормовская линия: 
	4010: u"Буревестник",
	4011: u"Бурнаковская",
	4012: u"Канавинская",
	4013: u"Московская"
}


city_metro[220] = {
	#1. Первая линия: 
	6000: u"Московская",
	6001: u"Гагаринская",
	6002: u"Спортивная",
	6003: u"Советская",
	6004: u"Победа",
	6005: u"Безымянка",
	6006: u"Кировская",
	6007: u"Юнгородок"
}

city_metro[60] = {
	#1. Уральская линия: 
	2000: u"Проспект Космонавтов",
	2001: u"Уралмаш",
	2002: u"Машиностроителей",
	2003: u"Уральская",
	2004: u"Динамо",
	2005: u"Площадь 1905 года", 
	2006: u"Геологическая"
}

city_metro[80] = {
	#Центральная линия: 
	3000: u"Кремлёвская",
	3001: u"Площадь Габдуллы",
	3002: u"Суконная слобода",
	3003: u"Аметьево",
	3004: u"Горки",
	3005: u"Проспект Победы"
}


city_metro[170] = {
	#1. Ленинская линия: 
	5000: u"Заельцовская",
	5001: u"Гагаринская",
	5002: u"Красный проспект",
	5003: u"Площадь Ленина",
	5004: u"Октябрьская",
	5005: u"Речной вокзал",
	5006: u"Студенческая",
	5007: u"Площадь Маркса",

	#2. Дзержинская линия: 
	5008: u"Площадь Гарина-Михайловского",
	5009: u"Сибирская",
	5010: u"Маршала Покрышкина",
	5011: u"Берёзовая роща"	
}

metro_stations = {}
for (city, metro) in city_metro.items():
	metro_stations.update(metro)


def get_stations_by_city(city_id):
	return city_metro.get(city_id)

def get_station_by_id(station_id):
	return metro_stations.get(station_id)


def is_station_in_city(station_id, city_id):
	check = False
	if station_id and city_id:
		stations = city_metro.get(city_id)
		if stations:
			check = stations.get(station_id)
	return check


def get_station_id_by_name_and_city(name, city_id):
	station_id = None
	if city_id and name:
		stations = city_metro.get(city_id)
		if stations:
			_name = name.strip().lower()
			station_id = next( (s_id for (s_id, s_name) in stations.items() if s_name.lower() == _name), None)
	return station_id

def get_station_id_by_name(name):
	station_id = None
	if name:
		_name = name.strip().lower()
		station_id = next( (s_id for (s_id, s_name) in metro_stations.items() if s_name.lower() == _name) , None)
	return station_id


def get_station_name_by_id(station_id):
	return metro_stations.get(station_id) or u""


if __name__ == '__main__':
	import dic.geo as geo
	#print(get_stations_by_city(170))
	#print(get_station_name_by_id(5002))
	#print(get_station_id_by_name_and_city(u"Красный проспект", 170))
	#print(get_station_id_by_name(u"Красный проспект"))
	#print(is_station_in_city(5002, 170))