/*
 * Translated default messages for the jQuery validation plugin.
 * Locale: RU (Russian; русский язык)
 */
(function ($) {
	$.extend($.validator.messages, {
		required: "Обязательное поле",
		remote: "Введите правильное значение",
		email: "Введите корректный адрес электронной почты",
		url: "Пожалуйста, введите корректный URL, например, http://ya.ru",
		date: "Введите корректную дату",
		dateISO: "Введите корректную дату в формате ISO",
		number: "Введите число",
		digits: "Пожалуйста, вводите только цифры",
		creditcard: "Введите правильный номер кредитной карты",
		equalTo: "Введите такое же значение ещё раз",
		accept: "Выберите файл с правильным расширением",
		maxlength: $.validator.format("Введите не больше {0} символов"),
		minlength: $.validator.format("Введите не меньше {0} символов"),
		rangelength: $.validator.format("Введите значение длиной от {0} до {1} символов"),
		range: $.validator.format("Введите число от {0} до {1}"),
		max: $.validator.format("Введите число, меньшее или равное {0}"),
		min: $.validator.format("Введите число, большее или равное {0}")
	});
}(jQuery));