var povodochek = {};

povodochek.extract_youtube_videoid = function(url) {
  if(url) {
    var re = /https?:\/\/(?:[0-9A-Z-]+\.)?(?:youtu\.be\/|youtube(?:-nocookie)?\.com\S*[^\w\s-])([\w-]{11})(?=[^\w-]|$)(?![?=&+%\w.-]*(?:['"][^<>]*>|<\/a>))[?=&+%\w.-]*/ig;
    var match = re.exec(url);
    return match ? match[1] : undefined;
  } 
  return undefined;

}

jQuery.validator.addMethod("_login", function(value, element) {
  return this.optional(element) || /^[.a-zA-Z0-9_-]+$/.test(value);
}, "Неправильный формат: только латинские буквы, цифры, дефисы, подчеркивания и точки.");

jQuery.validator.addMethod("_phone", function(value, element) {
  return this.optional(element) || /^(\+7\([0-9]{3}\)[0-9]{3}-[0-9]{4})|(\+7\(___\)___-____)$/.test(value);
}, "Неправильный номер телефона.");


jQuery.validator.addMethod("youtube", function(value, element) {
  if (value) {
    return povodochek.extract_youtube_videoid(value);
  }
  return true;
}, "Введите корректную ссылку. Например, http://www.youtube.com/watch?v=keflmwIRq6w");



povodochek.sort_alphabetical = function(x,y) {
  if(x,y) {
    return x.text.toLowerCase() > y.text.toLowerCase() ? 1: -1;
  } else {
    return 0;
  }
};

povodochek.select2_breed_sort = function(results, container, query) {
  if(query.term) {
    var results_top = [];
    var results_bottom = [];
    $.each(results, function(key, value) {
      var breed_name = value.text;
      if (breed_name.toLowerCase().indexOf(query.term.toLowerCase()) === 0){
        results_top.push(value);
      } else {
        results_bottom.push(value);
      }
    });
    results = $.merge(results_top.sort(povodochek.sort_alphabetical), 
      results_bottom.sort(povodochek.sort_alphabetical));
  }
  return results;
};

povodochek.select2_breed_format = function(object, container, query) {
    breed_name = "";
    if(object.id) {
      breed_name = object.id.split("_")[0] == "1" ? "собаки" : "кошки";
    }
    var regex = new RegExp(query.term, "i");
    var match = object.text.match(regex);
    var text  = object.text.replace(match, "<span style='text-decoration:underline'>" + match + "</span>");
    return $("<div>" + text + "<small class='muted pull-right'>" + breed_name + "</small></div>");
};

povodochek.validate = function (form, options, submit){
  var rules = options.rules ? options.rules : options;
  var messages= options.messages ? options.messages : undefined;
  form.validate({
     rules : rules,
     messages : messages, 
     errorElement : "li", 
      errorPlacement: function(error, element) {
       error.addClass("form-field-error");
       $("#" + element.attr("id") + "_field .form-field-errors").append(error);
     },
     highlight: function(element, errorClass) {
        $("#" + element.id + "_field").addClass("has-error").removeClass('has-success');
     },
     unhighlight: function(element, errorClass) {
        $("#" + element.id + "_field").removeClass("has-error").addClass("has-success");
        $("#" + element.id + "_field .form-field-errors .form-field-error").remove();
     },
     submitHandler: function(form) {
        var btn = $(":submit").button("loading");
        if(submit) submit();
        form.submit();
       }
    });
};


povodochek.typeahead = function(ajax_url, input_id, updater){
  var m = {
    minLength: 0,
    items: 12,
    autoSelect : true,
    source: function (query, process) {
      return $.getJSON(ajax_url,
        {limit: 12, query: query },
        function (data) { 
          var input = $("#" + input_id);
          if(data.items.length === 0) {
              input.tooltip("destroy").tooltip(
                {title:"Совпадений не найдено. Выберите из выпадающего списка, введя часть названия.", 
                trigger: "click"}).tooltip("show").
              attr("show-tooltip", "true");
          } else if (input.attr("show-tooltip") === "true"){
            input.tooltip("destroy").attr("show-tooltip", "false");
          }
          return process(data.items);
      }); //getJSON
    } //source
  }
  if (updater) {
    m["updater"] = updater;
  }
  return m;
};


(function($) {

    var oldHide = $.fn.popover.Constructor.prototype.hide;

    $.fn.popover.Constructor.prototype.hide = function() {
        if (this.options.trigger === "hover" && this.tip().is(":hover")) {
            var that = this;
            // try again after what would have been the delay
            setTimeout(function() {
                return that.hide.call(that, arguments);
            }, that.options.delay.hide);
            return;
        }
        oldHide.call(this, arguments);
    };

})(jQuery);