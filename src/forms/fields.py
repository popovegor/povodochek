#!/usr/bin/python
# -*- coding: utf-8 -*-

from wtforms import (fields, widgets, TextField, \
    SelectField, HiddenField, BooleanField, TextAreaField, \
    IntegerField, Form, DateTimeField, PasswordField, RadioField)


import dic.metro as metro
import dic.geo as geo
import db

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

class PForm(Form):
    def load_from_db_entity(self, entity):
        for f in self:
            f.set_val(entity.get(f.get_db_name()))

    def set_field_val(self, field_name, val):
        for f in self:
            if f.name == field_name:
                f.set_val(val)

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

    def get_val(self, form):
        f = self.field
        if is_active_field(form, f):
            return self.db_in(f) if self.db_in else f.data
        return None

    def set_val(self, val):
        self.field.data = self.db_out(val) if self.db_out else val

class PRadioField(RadioField, PField):
    def __init__(self, label = '', validators = None, \
        attraction = False, attraction_depends = None, \
        depends = None, db_name = None, \
        db_in = None, db_out = None, **kwargs):
        RadioField.__init__(self, label = label, \
            validators = validators, **kwargs)
        PField.__init__(self, field = self, attraction = attraction, \
            attraction_depends = attraction_depends, \
            depends = depends, db_name = db_name, \
            db_in = db_in, db_out = db_out)

class PDateTimeField(DateTimeField, PField):
    def __init__(self, label = '', validators = None, \
        attraction = False, attraction_depends = None, \
        depends = None, db_name = None, \
        db_in = None, db_out = None, **kwargs):
        DateTimeField.__init__(self, label = label, \
            validators = validators, **kwargs)
        PField.__init__(self, field = self, attraction = attraction, \
            attraction_depends = attraction_depends, \
            depends = depends, db_name = db_name, \
            db_in = db_in, db_out = db_out)

class PPasswordField(PasswordField, PField):
     def __init__(self, label = '', validators = None, \
        attraction = False, attraction_depends = None, \
        depends = None, db_name = None, \
        db_in = None, db_out = None, **kwargs):
        filters = kwargs.get("filters") or []
        kwargs["filters"] = [lambda x : (x or '').strip()] + filters
        PasswordField.__init__(self, label = label, \
            validators = validators, **kwargs)
        PField.__init__(self, field = self, attraction = attraction, \
            attraction_depends = attraction_depends, \
            depends = depends, db_name = db_name, \
            db_in = db_in, db_out = db_out)

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
        filters = kwargs.get("filters") or []
        kwargs["filters"] = [lambda x : (x or '').strip()] + filters
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

class MetroField(PIntegerField):

    def _value(self):
        if self.data:
            return metro.get_station_name_by_id(self.data)
        elif self.raw_data:
            return self.raw_data[0]
        else:
            return u""

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = metro.get_station_id_by_name(valuelist[0])
        else:
            self.data = None


class CityField(PIntegerField):

    def _value(self):
        if self.data:
            return geo.get_city_region(self.data)
        elif self.raw_data:
            return self.raw_data[0]
        else:
            return u""

    def process_formdata(self, valuelist):
        self.data = None
        self.city_id = None
        self.region_id = None
        self.location = None
        if valuelist:
            city = db.get_city_by_id(valuelist[0])
            if not city:
                city = db.get_city_by_city_and_region(valuelist[0])
            if city:
                self.data = city.get('city_id')
                self.city_id = city.get('city_id')
                self.region_id = city.get("region_id")
                self.location = city.get("location")
                
            

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
            #print('count', count, f.name)
    
            if get_attraction_field_val(form, f):
                complete += 1;  
                #print('complete', complete, f.name)


    percent = (round(complete / float(count) * 10000) / 100) if count > 0 else 0;
    return percent