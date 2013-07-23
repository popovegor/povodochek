jQuery.validator.addMethod("_login", function(value, element) {
  return this.optional(element) || /^[a-zA-Z0-9_-]+$/.test(value);
}, "Неправильный формат: только латинские буквы, цифры, дефисы и подчеркивания.");

var povodochek = {};

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

