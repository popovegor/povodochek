#!/usr/bin/python
# -*- coding: utf-8 -*-


cats = {
u'abissinskaja_koshka':u"Абиссинская кошка",
u'australian_mist':u"Австралийский мист",
u'asian_tabby':u"Азиатская табби",
u'amerikanskaja_zhestkosherstnaja_koshka':u"Американская жесткошерстная кошка",
u'amerikanskaja_korotkosherstnaja_koshka':u"Американская короткошерстная кошка",
u'american_bobtail':u"Американский бобтейл",
u'amerikanskij_kerl':u"Американский керл",
u'anatolian':u"Анатолийская кошка",
u'arabian_mau':u"Аравийский мау",
u'balinezijskaja_koshka':u"Балинезийская кошка",
u'bengalskaja_koshka':u"Бенгальская кошка",
u'birmanskaja_koshka':u"Бирманская кошка",
u'bombejskaja_koshka':u"Бомбейская кошка",
u'brazilian_shorthair':u"Бразильская короткошерстная кошка",
u'britanskaja_dlinnosherstnaja':u"Британская длинношерстная",
u'britanskaja_korotkosherstnaja_koshka':u"Британская короткошерстная кошка",
u'burma':u"Бурма",
u'burmilla':u"Бурмилла",
u'havana_brown_cat':u"Гавана браун",
u'gimalaiskaja_koshka':u"Гималайская кошка",
u'devon-reks':u"Девон-рекс",
u'donskoj_sfinks':u"Донской сфинкс",
u'evropejskaja_korotkosherstnaja_koshka':u"Европейская короткошерстная кошка",
u'egipetskij_mau':u"Египетский мау",
u'York_сhocolate':u"Йоркская шоколадная кошка",
u'california_spangled':u"Калифорнийская сияющая кошка",
u'canaani':u"Канаани",
u'karelskij_bobtejl':u"Карельский бобтейл",
u'kimrik':u"Кимрик",
u'kolcehvostaja_koshka':u"Кольцехвостая кошка",
u'korat':u"Корат",
u'kornish-reks':u"Корниш-рекс",
u'kurilskij_bobtejl':u"Курильский бобтейл",
u'la-perm':u"Ла-Перм",
u'manks':u"Манкс",
u'manchkin':u"Манчкин",
u'mejn-kun':u"Мейн-кун",
u'mekonskiy_bobteyl':u"Меконгский бобтейл",
u'minskin':u"Минскин",
u'nevskaja_maskaradnaja':u"Невская маскарадная кошка",
u'nemeckij_reks':u"Немецкий рекс",
u'norvezhskaja_lesnaja_koshka':u"Норвежская лесная кошка",
u'orientalnaja_koshka':u"Ориентальная кошка",
u'ocikat':u"Оцикат",
u'persidskaja_koshka':u"Персидская кошка",
u'piterbold':u"Петерболд",
u'pixiebob':u"Пиксибоб",
u'ragamuffin':u"Рагамаффин",
u'reksy':u"Рексы",
u'russkaja_golubaja_dlinnosherstnaja':u"Русская голубая длинношерстная (Нибелунг)",
u'russkaja_golubaja_koshka':u"Русская голубая кошка",
u'rjegdoll':u"Рэгдолл",
u'savannah_cat':u"Саванна",
u'sacred_birma':u"Священная бирманская кошка (священная бирма)",
u'seychellois_cat':u"Сейшельская кошка",
u'selkirk-reks':u"Селкирк-рекс",
u'serengeti_cat':u"Серенгети",
u'siamskaja_koshka':u"Сиамская кошка",
u'sibirskaja_koshka':u"Сибирская кошка",
u'singapurskaja_koshka':u"Сингапурская кошка",
u'snou-shu':u"Сноу-шу",
u'sokoke':u"Сококе",
u'somalijskaja_koshka':u"Сомалийская кошка",
u'sfinks_kanadskij_sfinks':u"Сфинкс (Канадский сфинкс)",
u'tajskaja_koshka':u"Тайская кошка",
u'toj-bobtejl':u"Той-бобтейл",
u'toiger':u"Тойгер",
u'tonkinskaja_koshka':u"Тонкинская кошка",
u'tureckaja_angora':u"Турецкая ангора (Ангорская кошка)",
u'tureckij_van':u"Турецкий ван",
u'ukrainskij_levkoj':u"Украинский Левкой",
u'uralskij_reks':u"Уральский рекс",
u'foreign_white':u"Форинвайт",
u'ceylon_cat':u"Цейлонская кошка",
u'felis_chaus':u"Чаузи",
u'tiffani':u"Шантильи-Тиффани",
u'kartezianskaja_koshka':u"Шартрез (Картезианская кошка)",
u'chinchilla_longhair':u"Шиншилла ДШ",
u'shotlandskaja_vislouhaja_koshka':u"Шотландская вислоухая кошка (Скотиш фолд)",
u'hajlend-srajt':u"Шотландская длинношерстная (Хайленд-страйт)",
u'haylend-fold':u"Шотландская длинношерстная кошка (Хайленд-фолд)",
u'skotish_strayt':u"Шотландская короткошерстная (Cкоттиш-страйт)",
u'aegean_cat':u"Эгейская кошка",
u'jekzoticheskaja_korotkosherstnaja_koshka':u"Экзотическая короткошерстная кошка",
u'javanese':u"Яванез (Яванская кошка)",
u'japonskij_bobtejl':u"Японский бобтейл"}


import urllib2
from bs4 import BeautifulSoup
import codecs 


def check_breed_alive(breed_id = ''):
	try:
		post_data = "sex=0&category=2&page=0&section=0&type={0}&country=0&city=0&metro=0&_=".format(breed_id)
		response = None
		alive = False
		advs_num = 0
		r = urllib2.Request("http://www.pitomec.ru/board/main/2", post_data)
		r.add_data(post_data)
		response = urllib2.urlopen(r)
		if response.code == 200:
			soup = BeautifulSoup(response.read())
			advs_num = int(soup.strong.getText())
			if advs_num > 0:
				alive = True
	except Exception, e:
		print(e)
		raise e
	finally:
		if response: 
			response.close()
			response = None
	return (alive, advs_num)


if __name__ == "__main__":
	with codecs.open("cats_alive.txt", "w", "utf-8") as f:
		for breed_id, breed_name in cats.items()[:1]:
			( alive, advs_num ) = check_breed_alive(breed_id)
			if alive:
				# f.write("%s, %s, %s\n" % (breed_id, breed_name, advs_num))
				print ("%s %s %s " % (breed_id , alive, advs_num))
