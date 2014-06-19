#!/usr/bin/python
# -*- coding: utf-8 -*-


from jinja2 import Markup
from uuid import (uuid4, uuid1)

class MomentJS:
    def __init__(self, timestamp):
        self.timestamp = timestamp

    def __call__(self, *args):
        return self.format(*args)

    def render(self, format):
        uid = str(uuid4())
        return Markup(u"<script id='momentjs_{0}'>\n$('#momentjs_{0}').after(moment(\"{1}\").{2});\n</script>".format(uid, self.timestamp.strftime("%Y-%m-%dT%H:%M:%S Z"), format))

    def format(self, fmt):
        return self.render("format(\"%s\")" % fmt)

    def calendar(self):
        return self.render("calendar()")

    def fromNow(self, non_suffix = False):
        return self.render("fromNow("+ str(non_suffix).lower() +")")