#!/usr/bin/python
# -*- coding: utf-8 -*-

breeds = {
1387:u"Австралийская короткохвостая пастушья собака", 
12:u"Австралийская овчарка", 
234:u"Австралийская пастушья собака", 
13:u"Австралийский келпи", 
14:u"Австралийский кеттл", 
15:u"Австралийский терьер", 
235:u"Австралийский шелковистый терьер", 
398:u"Австрийский гладкошерстный бракк", 
399:u"Австрийский короткошерстный пинчер", 
400:u"Азавак", 
401:u"Аиди", 
236:u"Айну", 
402:u"Акбаш", 
16:u"Акита-ину", 
403:u"Алано", 
17:u"Алапахский бульдог", 
404:u"Алопекис", 
405:u"Альпийская овчарка", 
406:u"Альпийский таксообразный бракк", 
407:u"Аляскинский кли кэй", 
18:u"Аляскинский маламут", 
19:u"Американская акита", 
408:u"Американская индейская собака", 
409:u"Американская оленья собака", 
410:u"Американская тундровая овчарка", 
845:u"Американская эскимосская собака", 
411:u"Американский булли", 
21:u"Американский бульдог", 
412:u"Американский бульнез", 
413:u"Американский водный спаниель", 
23:u"Американский голый терьер", 
22:u"Американский кокер-спаниель", 
414:u"Американский низкорослый мопс", 
24:u"Американский питбультерьер", 
25:u"Американский стаффордширский терьер", 
26:u"Американский той-фокстерьер", 
415:u"Американский фоксхаунд", 
20:u"Американский эскимосский шпиц", 
27:u"Анатолийский карабаш", 
416:u"Английская овчарка", 
118:u"Английский бульдог", 
117:u"Английский кокер-спаниель", 
418:u"Английский красно-крапчатый кунхаунд", 
119:u"Английский мастиф", 
120:u"Английский пойнтер", 
121:u"Английский сеттер", 
420:u"Английский фоксхаунд", 
421:u"Англо-французская малая гончая", 
422:u"Андалузский ратонеро", 
124:u"Аппенцеллер зенненхунд", 
125:u"Аргентинский дог", 
397:u"Арденнский бувье", 
1390:u"Армант (египетская овчарка)", 
423:u"Артезиано-нормандский бассет", 
424:u"Артуазская гончая", 
425:u"Арубская деревенская собака", 
426:u"Арьежская гончая", 
427:u"Арьежский бракк", 
395:u"Афганская борзая", 
428:u"Африканская дикая собака", 
396:u"Аффен-пинчер", 
130:u"Баварская горная гончая", 
1391:u"Баварская следовая собака", 
134:u"Балканская гончая", 
1392:u"Барбет (барбе)", 
136:u"Басенджи", 
137:u"Бассет-хаунд", 
139:u"Бедлингтон-терьер", 
145:u"Белая швейцарская овчарка", 
156:u"Бельгийская овчарка грюнендаль", 
149:u"Бельгийская овчарка лакенуа", 
150:u"Бельгийская овчарка малинуа", 
152:u"Бельгийская овчарка тервюрен", 
154:u"Бельгийский гриффон", 
1394:u"Бергамская овчарка (бергамаско)", 
155:u"Бернский зенненхунд", 
159:u"Бивер йорк", 
160:u"Бигль", 
316:u"Бигль-харрьер", 
167:u"Бийи", 
161:u"Бишон-фриз", 
162:u"Бладхаунд", 
598:u"Бобтейл (староанглийская овчарка)", 
168:u"Бойкин-спаниель", 
490:u"Боксер (немецкий)", 
170:u"Болоньез", 
171:u"Большая гасконско-сентонжская гончая", 
172:u"Большая древесная гончая", 
173:u"Большая испанская гончая", 
318:u"Большая пиренейская собака", 
1393:u"Большая швейцарская овчарка", 
175:u"Большой португальский поденгу", 
176:u"Большой французский бракк", 
178:u"Бордер-колли", 
179:u"Бордер-терьер", 
180:u"Бордоский дог", 
319:u"Бородатая колли", 
182:u"Босерон", 
183:u"Боснийская грубошерстная гончая", 
184:u"Бостон-терьер", 
846:u"Бретонский эпаньоль", 
188:u"Бриар (Французская овчарка)", 
189:u"Брюссельский гриффон", 
190:u"Бульмастиф", 
191:u"Бультерьер", 
195:u"Бурбонский бракк", 
321:u"Бургосская легавая", 
194:u"Бурят-монгольская собака (волкодав)", 
1067:u"Валлер", 
907:u"Вандейский бассет-гриффон (большой)", 
196:u"Вандейский бассет-гриффон (малый)", 
199:u"Веймаранер (Веймарская легавая)", 
202:u"Вельш-корги-кардиган", 
547:u"Вельш-корги-пемброк", 
200 : u"Вельш-спрингер-спаниель", 
203:u"Вельш-терьер", 
206:u"Венгерская борзая", 
1068:u"Венгерская выжла (жесткошерстная)", 
201:u"Венгерская короткошерстная легавая (выжла)", 
208:u"Венгерский кувас", 
638:u"Вест-хайленд-уайт-терьер", 
322:u"Вестфальский таксообразный бракк", 
1069:u"Вестфальский терьер", 
323:u"Веттерхун", 
844:u"Восточно-европейская овчарка", 
212:u"Восточносибирская лайка", 
213:u"Гаванский бишон", 
215:u"Ганноверская гончая", 
217:u"Герта-пойнтер", 
218:u"Гималайская овчарка", 
219:u"Гладкошёрстный фокстерьер", 
220:u"Глен-ов-имаал-терьер", 
221:u"Голая собака инков", 
222:u"Голландская овчарка", 
223:u"Голландский смаусхонд", 
224:u"Голландский тульпхонд", 
225:u"Голубая гасконская гончая", 
226:u"Голубой гасконский бассет", 
314:u"Голубой гасконский гриффон", 
228:u"Голубой овернский бракк", 
229:u"Голубой пикардийский эпаньоль", 
230:u"Гончая гамильтона", 
233:u"Гончая шиллера", 
325:u"Грейхаунд", 
231:u"Гренландская собака", 
232:u"Гриффон кортальса", 
238:u"Далматин", 
244:u"Датская таксообразная гончая", 
239:u"Денди-динмонт-терьер", 
240:u"Джек-рассел-терьер", 
242:u"Доберман", 
243:u"Дратхаар", 
245:u"Древер", 
246:u"Древесная енотовая гончая (Кунхаунд Уолкера)", 
247:u"Дрентская куропаточная собака", 
248:u"Дункер (норвежская гончая)", 
331:u"Евразиер (Ойразир)", 
332:u"Еврохаунд", 
333:u"Емтхунд", 
250:u"Западносибирская лайка", 
251:u"Золотистый ретривер", 
258:u"Ивисская собака (Поденко Ибиценко)", 
259:u"Ирландский водяной спаниель", 
254:u"Ирландский волкодав", 
260:u"Ирландский глен оф имаал терьер", 
255:u"Ирландский мягкошерстный пшеничный терьер", 
256:u"Ирландский сеттер", 
257:u"Ирландский терьер", 
263:u"Исландская сторожевая", 
261:u"Испанская водная собака", 
262:u"Испанский мастиф", 
328:u"Итальянская короткошерстная гончая", 
265:u"Итальянский бракк", 
324:u"Итальянский шпиц (Вольпино итальяно)", 
266:u"Йоркширский Терьер", 
351:u"Ка де бестиар", 
267:u"Кавалер-кинг-чарльз-спаниель", 
268:u"Кавказская овчарка", 
269:u"Кадебо (Ка Де Бо)", 
330:u"Кай", 
271:u"Кай лео", 
352:u"Кан гуичо", 
353:u"Кан де паллейро", 
272:u"Кан ди кастру лаборейру", 
273:u"Канарская собака", 
274:u"Кангал", 
275:u"Кане-корсо Итальяно", 
355:u"Караванная борзая", 
356:u"Каракачанская собака", 
357:u"Карело-финская лайка", 
329:u"Карельская медвежья собака", 
675:u"Карликовый пинчер", 
279:u"Каролинская собака", 
280:u"Карстская овчарка", 
281:u"Каталонская овчарка", 
1401:u"Катахула", 
334:u"Кеесхонд", 
341:u"Келпи", 
891:u"Керн-терьер", 
343:u"Керри-бигль", 
336:u"Керри-блю-терьер", 
337:u"Кинг чарльз спаниель", 
359:u"Кису", 
873:u"Китайская хохлатая собака", 
339:u"Кламбер-спаниель", 
1431:u"Коикерхондье", 
326:u"Колли длинношерстная (шотландская овчарка)", 
360:u"Колли короткошерстная", 
345:u"Комондор", 
368:u"Корейский джиндо", 
369:u"Королевская овчарка", 
363:u"Короткохвостый кеттл-дог", 
346:u"Котон де тулеар", 
347:u"Крапчато-голубой кунхаунд", 
364:u"Красный кунхаунд", 
365:u"Крашская овчарка", 
366:u"Критикос ихнилатис", 
348:u"Кромфорлендер", 
371:u"Куньминская овчарка", 
350:u"Курчавошерстный ретривер", 
372:u"Лабрадор ретривер", 
1402:u"Лабрадудль", 
379:u"Лаготто романьоло", 
380:u"Ландсир", 
381:u"Ланкашир хилер", 
1403:u"Лапландская пастушья собака", 
391:u"Лапхунд", 
382:u"Латвийская гончая", 
392:u"Левеск", 
373:u"Левретка (итальянский грейхаунд)", 
374:u"Лейкленд-терьер", 
375:u"Леонбергер", 
383:u"Леонская кареа", 
376:u"Леопардовая собака", 
384:u"Лесная такса", 
385:u"Лёрчер", 
377:u"Лион бишон", 
386:u"Ллавелн сеттер", 
387:u"Лонгдог", 
388:u"Лопарская оленегонная собака", 
389:u"Лукас терьер", 
378:u"Лхаский апсо", 
394:u"Люцернская гончая", 
438:u"Мажореро Канарио", 
439:u"Малая аппенинская гончая", 
440:u"Малая гасконско-сэнтонжская гончая", 
441:u"Малая голубая гасконская гончая", 
444:u"Малая львиная собачка", 
445:u"Малая швейцарская гончая - Бернская гончая", 
446:u"Малая швейцарская гончая - Люцернская гончая", 
447:u"Малая швейцарская гончая - Швицкая гончая", 
448:u"Малая швейцарская гончая - Юрская гончая", 
450:u"Малый мюнстерлендер", 
430:u"Мальтезе (Мальтийская болонка)", 
451:u"Манчестер терьер", 
452:u"Мареммано-абруццкая овчарка", 
453:u"Маркизье", 
367:u"Мексиканская голая собака (Ксолоитцкуинтли)", 
442:u"Мелитео Кинидио", 
885:u"Метис", 
455:u"Ми-ки", 
456:u"Миниатюрная австралийская овчарка", 
457:u"Миниатюрный бульдог", 
433:u"Миниатюрный бультерьер", 
304:u"Миттельшнауцер", 
458:u"Монгольская овчарка", 
436:u"Мопс", 
437:u"Московская сторожевая", 
459:u"Московский дракон", 
460:u"Муди", 
1404:u"Мягкошерстный пшеничный терьер", 
491:u"Наваррская легавая", 
462:u"Неаполитанский мастиф", 
492:u"Немецкая гончая", 
463:u"Немецкая овчарка", 
464:u"Немецкая овчарка длинношерстная", 
465:u"Немецкий бракк", 
466:u"Немецкий вахтельхунд (спаниель)", 
467:u"Немецкий дог", 
469:u"Немецкий курцхаар", 
470:u"Немецкий лангхаар", 
471:u"Немецкий шпиц большой", 
472:u"Немецкий шпиц малый", 
473:u"Немецкий шпиц средний", 
474:u"Немецкий штихельхаар", 
475:u"Немецкий ягдтерьер", 
476:u"Нивернейский гриффон", 
477:u"Новогвинейская поющая собака", 
493:u"Новозеландская овчарка", 
478:u"Новошотландский ретривер", 
479:u"Норботтен шпиц", 
480:u"Норвежский бухунд", 
481:u"Норвежский лундехунд", 
482:u"Норвежский эльгхунд серый", 
483:u"Норвежский эльгхунд черный", 
484:u"Норвич терьер", 
485:u"Норфолк терьер", 
486:u"Ньюфаундленд", 
494:u"Облавная бразильская гончая", 
495:u"Овернский бракк", 
496:u"Овчарка Гаучо", 
497:u"Овчарка панда", 
498:u"Одис", 
500:u"Ойразир", 
499:u"Оттерхаунд", 
546:u"Папильон (Папийон, Континентальный той спаниель)", 
501:u"Парсон Рассел терьер", 
502:u"Пастушья собака Трансмонтано", 
655:u"Паттердейл терьер", 
504:u"Пекинес", 
505:u"Перро ратеро Мальоркин", 
506:u"Перуанская голая собака", 
507:u"Петербургская орхидея", 
549:u"Пикарди", 
508:u"Пикардийская овчарка", 
509:u"Пикардийский эпаньоль", 
487:u"Пинчер немецкий", 
512:u"Пиренейская овчарка гладкомордая", 
513:u"Пиренейская овчарка длинношерстная", 
514:u"Пиренейский мастиф", 
516:u"Планинская гончая", 
517:u"Плотт-хаунд", 
519:u"Поденгу португезе малый", 
520:u"Поденгу португезе средний", 
521:u"Поденко Андалуз", 
522:u"Поденко Гальго", 
524:u"Поденко Кампанеро", 
525:u"Поденко Канарио", 
550:u"Пойнтер", 
526:u"Полигарская борзая", 
527:u"Польская борзая", 
528:u"Польская гончая", 
529:u"Польская низинная овчарка", 
530:u"Польская подгалянская овчарка", 
548:u"Померанский шпиц (карликовый)", 
640:u"Порселен (фарфоровая гончая )", 
531:u"Португальская водная собака", 
665:u"Португальская овчарка", 
553:u"Португальская сторожевая", 
533:u"Португальский бракк (пойнтер)", 
534:u"Посавская гончая", 
535:u"Пражский крысарик", 
890:u"Прямошерстный ретривер", 
185:u"Пти брабансон", 
538:u"Пуатвинская гончая", 
539:u"Пудель большой (стандартный, королевский пудель)", 
843:u"Пудель карликовый (миниатюрный)", 
540:u"Пудель малый", 
542:u"Пудель той", 
543:u"Пудельпойнтер", 
544:u"Пули", 
545:u"Пуми", 
554:u"Рампурская борзая", 
555:u"Рафейру ду Алентежу", 
556:u"Ризеншнауцер", 
557:u"Родезийский риджбек", 
558:u"Ротвейлер", 
559:u"Румынская карпатская овчарка", 
560:u"Румынская овчарка миоритик", 
561:u"Русская гончая", 
562:u"Русская каштанка", 
563:u"Русская пегая гончая", 
564:u"Русская псовая борзая", 
565:u"Русская цветная болонка", 
566:u"Русский охотничий спаниель", 
567:u"Русский той-терьер", 
569:u"Русско-европейская лайка", 
570:u"Рыжий бретонский бассет", 
571:u"Рыжий бретонский гриффон", 
572:u"Рэт-терьер", 
573:u"Саге Коче", 
574:u"Салюки (арабская борзая)", 
575:u"Самоед (самоедская лайка)", 
576:u"Сапсари", 
607:u"Сарлосская волчья собака", 
577:u"Сассекс спаниель", 
578:u"Сахалинский хаски", 
580:u"Сен-Жерменский бракк", 
579:u"Сенбернар", 
581:u"Сербская гончая", 
216:u"Сеттер гордон (шотландский)", 
608:u"Сиба-ину", 
585:u"Сибирская ездовая собака", 
586:u"Сикоку", 
587:u"Силихем терьер", 
609:u"Сицилийская борзая", 
588:u"Скай терьер", 
589:u"Скотч-терьер", 
590:u"Словацкая гончая", 
591:u"Словацкая жесткошерстная легавая", 
592:u"Словацкий чувач", 
593:u"Слюги", 
594:u"Смоландская гончая", 
595:u"Спиноне", 
611:u"Спрингер-спаниель (английский)", 
596:u"Среднеазиатская овчарка", 
597:u"Стабихон", 
599:u"Староанглийский бульдог", 
600:u"Стародатская легавая", 
601:u"Староиспанский пойнтер", 
604:u"Старонемецкая пастушья собака (овечий пудель)", 
605:u"Старонемецкая пастушья собака (черная)", 
602:u"Старонемецкая пастушья собака - Желтощек", 
603:u"Старонемецкая пастушья собака - Лис", 
606:u"Стаффордширский бультерьер", 
612:u"Тази", 
613:u"Тайган", 
614:u"Тайский риджбек", 
680:u"Такса гладкошерстная", 
629:u"Такса жесткошерстная", 
615:u"Такса карликовая", 
616:u"Такса кроличья", 
617:u"Такса стандартная", 
618:u"Тедди Рузвельт терьер", 
619:u"Теломиан", 
620:u"Тентерфилд терьер", 
621:u"Тибетский мастиф", 
622:u"Тибетский спаниель", 
623:u"Тибетский терьер", 
624:u"Тирольский бракк", 
625:u"Той фокстерьер", 
123:u"Той-терьер (Английский)", 
626:u"Тоса Ину", 
632:u"Трансильванская гончая", 
694:u"Тувинская овчарка", 
633:u"Уиппет", 
637:u"Упряжная собака", 
634:u"Уругвайская дикая собака", 
635:u"Утонаган", 
636:u"Уэльская овчарка", 
362:u"Фален", 
639:u"Фараонова собака", 
641:u"Фел-хаунд", 
642:u"Фила Бразилейро", 
644:u"Фила Сен Мигель", 
643:u"Фила Тершейра", 
645:u"Филд спаниель", 
646:u"Финская гончая", 
647:u"Финская лопарская собака", 
648:u"Финский шпиц", 
649:u"Фландрский бувье", 
650:u"Фокстерьер гладкошерстный", 
651:u"Фокстерьер жесткошерстный", 
652:u"Французская бело-оранжевая гончая", 
653:u"Французская бело-черная гончая", 
654:u"Французская трехцветная гончая", 
657:u"Французский бракк пиренейский тип", 
658:u"Французский бульдог", 
659:u"Французский эпаньоль", 
661:u"Хальденстёваре", 
662:u"Ханаанская собака", 
663:u"Харьер", 
674:u"Хаски (сибирский)", 
664:u"Хахо-аву", 
666:u"Хеллефорсхунд", 
667:u"Хигенхунд", 
668:u"Ховаварт", 
669:u"Ходская собака", 
670:u"Хоккайдо", 
671:u"Хорватская овчарка", 
672:u"Хорватская планинская собака", 
673:u"Хортая борзая", 
676:u"Цвергшнауцер", 
677:u"Чау-чау", 
681:u"Черно-подпалый кунхаунд", 
692:u"Черный терьер", 
682:u"Чесапик бей ретривер", 
683:u"Чехословацкая волчья собака (чешский волфхунд)", 
684:u"Чешская горская собака", 
686:u"Чешская пестрая собака", 
687:u"Чешский терьер", 
685:u"Чешский фоусек (жесткошерстная легавая)", 
903:u"Чинук", 
689:u"Чиппипарай", 
690:u"Чирнеко делль Этна", 
691:u"Чихуахуа", 
285:u"Шапендус (шапендоес, голландская овчарка)", 
135:u"Шарпей", 
296:u"Шарпланинац", 
902:u"Шведский лаппхунд", 
298:u"Шведский эльгхунд белый", 
299:u"Швейцарская гончая", 
300:u"Шелковистая борзая", 
144:u"Шелти", 
153:u"Ши-тцу", 
146:u"Шиба-ину", 
302:u"Шиллерстеваре", 
151:u"Шипперке", 
1405:u"Шнуровой пудель", 
306:u"Шотландская борзая (Дирхаунд)", 
307:u"Штирский брудастый бракк", 
292:u"Эло", 
140:u"Энтлебухер зенненхунд", 
293:u"Эпаньоль де Сент Юсюж", 
294:u"Эпаньоль Понт Одемер", 
141:u"Эрдельтерьер", 
1406:u"Эскимосская лайка", 
142:u"Эстонская гончая", 
295:u"Эштрельская овчарка", 
290:u"Югославская трехцветная гончая", 
874:u"Южноафриканский бурбуль", 
291:u"Южнорусская борзая", 
138:u"Южнорусская овчарка", 
131:u"Ягдтерьер", 
289:u"Якутская лайка", 
288:u"Японский терьер", 
132:u"Японский хин", 
133:u"Японский шпиц"}

import urllib2
from bs4 import BeautifulSoup
import codecs 


def check_breed_alive(breed_id = 182):
	try:
		post_data = "region_id=0&city_id=0&breed_id={0}&dog_size_id=0&x=38&y=12&page=1".format(breed_id)
		response = None
		alive = False
		advs_num = 0
		r = urllib2.Request("http://poisk-druga.ru/sell/search/", post_data)
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
	with codecs.open("breeds_alive.txt", "w", "utf-8") as f:
		for breed_id, breed_name in breeds.items()[:]:
			( alive, advs_num ) = check_breed_alive(breed_id)
			if alive:
				f.write("%s, %s, %s\n" % (breed_id, breed_name, advs_num))
				print ("%s %s %s " % (breed_id , alive, advs_num))
		
