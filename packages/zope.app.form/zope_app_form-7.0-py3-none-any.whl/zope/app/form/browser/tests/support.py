##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""General test support."""
from zope.configuration import xmlconfig
# This import is used in tests.
from zope.formlib.tests.support import patternExists  # noqa: F401


def registerEditForm(schema, widgets=()):
    """Registers an edit form for the specified schema.

    widgets is a mapping of field name to dict. The dict for each field must
    contain a 'class' item, which is the widget class, and any additional
    widget attributes (e.g. text field size, rows, cols, etc.)
    """
    widgetsXml = []
    for field in widgets:  # pragma: no cover
        widgetsXml.append('<widget field="%s"' % field)
        for attr in widgets[field]:
            widgetsXml.append(f' {attr}="{widgets[field][attr]}"')
        widgetsXml.append(' />')
    xmlconfig.string("""
        <configure xmlns="http://namespaces.zope.org/browser">
          <include package="zope.app.form.browser" file="meta.zcml" />
          <editform
            name="edit.html"
            schema="{}"
            permission="zope.View">
            {}
          </editform>
        </configure>
        """.format(schema.__identifier__, ''.join(widgetsXml)))


def defineSecurity(class_, schema):
    class_ = f'{class_.__module__}.{class_.__name__}'
    schema = schema.__identifier__
    xmlconfig.string("""
        <configure xmlns="http://namespaces.zope.org/zope">
          <include package="zope.security" file="meta.zcml" />
          <class class="{}">
            <require
              permission="zope.Public"
              interface="{}"
              set_schema="{}" />
          </class>
        </configure>
        """.format(class_, schema, schema))
