jQuery.validator.addMethod("_login", function(value, element) {
  return this.optional(element) || /^[a-zA-Z0-9_-]+$/.test(value);
}, "Неправильный формат: только латинские буквы, цифры, дефисы и подчеркивания.");

var povodochek = {};

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
    results = $.merge(results_top.sort(), results_bottom.sort());
  }
  return results;
}

povodochek.validate = function (form, rules, submit){
    form.validate({
       rules : rules,
       errorElement : "p", 
        errorPlacement: function(error, element) {
         error.addClass("label label-important");
         $("#" + element.attr("id") + "_field label").after(error);
       },
       highlight: function(element, errorClass) {
          $("#" + element.id + "_field").addClass("error").removeClass('success');
       },
       unhighlight: function(element, errorClass) {
          $("#" + element.id + "_field").removeClass("error").addClass("success");
       },
       submitHandler: function(form) {
          var btn = $(":submit").button("loading");
          if(submit) submit();
          form.submit();
         }
      });
  };

