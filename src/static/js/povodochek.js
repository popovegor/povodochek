jQuery.validator.addMethod("_login", function(value, element) {
  return this.optional(element) || /^[.a-zA-Z0-9_-]+$/.test(value);
}, "Неправильный формат: только латинские буквы, цифры, дефисы, подчеркивания и точки.");

jQuery.validator.addMethod("_phone", function(value, element) {
  return this.optional(element) || /^(\+7\([0-9]{3}\)[0-9]{3}-[0-9]{4})|(\+7\(___\)___-____)$/.test(value);
}, "Неправильный номер телефона.");


var povodochek = {};

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

povodochek.validate = function (form, rules, submit){
  form.validate({
     rules : rules,
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
     },
     submitHandler: function(form) {
        var btn = $(":submit").button("loading");
        if(submit) submit();
        form.submit();
       }
    });
};
