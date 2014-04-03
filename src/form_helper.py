from wtforms import (fields, widgets, TextField, \
    SelectField, HiddenField, BooleanField, TextAreaField, \
    IntegerField)

class Select2Widget(widgets.Select):
    """
        `Select2 <https://github.com/ivaynberg/select2>`_ styled select widget.

        You must include select2.js, form.js and select2 stylesheet for it to
        work.
    """
    def __call__(self, field, **kwargs):
        allow_blank = getattr(field, 'allow_blank', False)

        if allow_blank and not self.multiple:
            kwargs['data-role'] = u'select2blank'
        else:
            kwargs['data-role'] = u'select2'

        return super(Select2Widget, self).__call__(field, **kwargs)



def get_fields(form):
    return dict([(f.id, {"name": f.name, \
        "attrs": f.attrs}) for f in form])

class PField():
    def __init__(self, field, attraction = False, \
        attraction_depends = None, \
        depends = None, db_name = None, 
        db_in = None, db_out = None):
        self.attrs = {}
        self.attrs["attraction"] = attraction
        self.attrs["attraction_depends"] = attraction_depends
        self.attrs["depends"] = depends
        self.db_name = db_name
        self.db_in = db_in
        self.db_out = db_out
        self.field = field

    def get_db_name(self):
        return self.db_name if self.db_name else self.name

    def get_db_val(self, form):
        f = self.field
        if is_active_field(form, f):
            return self.db_in(f) if self.db_in else f.data
        return None

    def set_db_val(self, val):
        self.field.data = self.db_out(val) if self.db_out else val


    # def get_val(self):
    #     return get_field_val

    # def set_db_val(self, val):
    #     return self.db_out()


class PTextField(TextField, PField):
     def __init__(self, label = '', validators = None, \
        attraction = False, attraction_depends = None, \
        depends = None, db_name = None, \
        db_in = None, db_out = None, **kwargs):
        filters = kwargs.get("filters") or []
        kwargs["filters"] = [lambda x : (x or '').strip()] + filters
        TextField.__init__(self, label = label, \
            validators = validators, **kwargs)
        PField.__init__(self, field = self, attraction = attraction, \
            attraction_depends = attraction_depends, \
            depends = depends, db_name = db_name, \
            db_in = db_in, db_out = db_out)

class PSelectField(SelectField, PField):
    def __init__(self, label = '', validators = None, \
        attraction = False, attraction_depends = None, \
        depends = None, db_name = None, \
        db_in = None, db_out = None, **kwargs):
        SelectField.__init__(self, label = label, \
            validators = validators, **kwargs)
        PField.__init__(self, field = self, attraction = attraction, \
            attraction_depends = attraction_depends, \
            depends = depends, db_name = db_name, \
            db_in = db_in, db_out = db_out)

class PHiddenField(HiddenField, PField):
    def __init__(self, label = '', validators = None, \
        attraction = False, attraction_depends = None, \
        depends = None, db_name = None, \
        db_in = None, db_out = None, **kwargs):
        HiddenField.__init__(self, label = label, \
            validators = validators, **kwargs)
        PField.__init__(self, field = self, attraction = attraction, \
            attraction_depends = attraction_depends, \
            depends = depends, db_name = db_name, \
            db_in = db_in, db_out = db_out)


class PBooleanField(BooleanField, PField):
    def __init__(self, label = '', validators = None, \
        attraction = False, attraction_depends = None, \
        depends = None, db_name = None, \
        db_in = None, db_out = None, **kwargs):
        BooleanField.__init__(self, label = label, \
            validators = validators, **kwargs)
        PField.__init__(self, field = self, attraction = attraction, \
            attraction_depends = attraction_depends, \
            depends = depends, db_name = db_name, \
            db_in = db_in, db_out = db_out)  

class PTextAreaField(TextAreaField, PField):
    def __init__(self, label = '', validators = None, \
        attraction = False, attraction_depends = None, \
        depends = None, db_name = None, \
        db_in = None, db_out = None, **kwargs):
        TextAreaField.__init__(self, label = label, \
            validators = validators, **kwargs)
        PField.__init__(self, field = self, attraction = attraction, \
            attraction_depends = attraction_depends, \
            depends = depends, db_name = db_name, \
            db_in = db_in, db_out = db_out)

class PIntegerField(IntegerField, PField):
    def __init__(self, label = '', validators = None, \
        attraction = False, attraction_depends = None, \
        depends = None, db_name = None, \
        db_in = None, db_out = None, **kwargs):
        IntegerField.__init__(self, label = label, \
            validators = validators, **kwargs)
        PField.__init__(self, field = self, attraction = attraction, \
            attraction_depends = attraction_depends, \
            depends = depends, db_name = db_name, \
            db_in = db_in, db_out = db_out)


def is_active_attraction_field(form, field):
    if field.attrs and field.attrs.get("attraction_depends"):
        depends = field.attrs.get("attraction_depends");
        active = is_active_attraction_field(form, \
            form[depends["id"]]);
        if not active:
            return False;
        elif depends.get("values"):
            depends_val = get_field_val(form, form[depends["id"]])
            depends_values = depends["values"]
            return depends_val in depends_values
    
    return True;

def get_attraction_field_val(form, field):
    if field.attrs and field.attrs.get("attraction_depends"):
        depends = field.attrs.get("attraction_depends");
        if not get_attraction_field_val(form, form[depends["id"]]):
            return None

    return get_field_val(form, field)

def is_active_field(form, field):
    if field.attrs and field.attrs.get("depends"):
        depends = field.attrs.get("depends");
        active = is_active_field(form, \
            form[depends["id"]]);
        if not active:
            return False;
        elif depends.get("values"):
            depends_val = get_field_val(form, form[depends["id"]])
            depends_values = depends["values"]
            return depends_val in depends_values

    if type(field) is PSelectField:
        if field.data <= 0:
            return False
    return True   
        
def get_field_val(form, field):
    if is_active_field(form, field):
        data = field.data
        if type(field) is PTextField:
            data = (data or '').strip()
        return data
    else:
        return None


def calc_attraction(form):
    count = 0;
    complete = 0;
    for f in filter(lambda f: f.attrs.get("attraction"), form):
        if is_active_attraction_field(form, f):
            count += 1; 
            # print('count', count, f.name)
    
            if get_attraction_field_val(form, f):
                complete += 1;  
                # print('complete', complete, f.name)


    percent = (round(complete / float(count) * 10000) / 100) if count > 0 else 0;
    return percent