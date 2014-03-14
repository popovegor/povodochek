from wtforms import (fields, widgets, TextField)

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




class PTextField(TextField):
     def __init__(self, label='', validators=None, \
        credibility = False, **kwargs):
        super(PTextField, self).__init__(label = label, \
            validators = validators, **kwargs)
        self.credibility = credibility


