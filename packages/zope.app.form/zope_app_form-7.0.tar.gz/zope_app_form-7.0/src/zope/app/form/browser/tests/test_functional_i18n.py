##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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
"""Test form i18n"""

import doctest
import re
import unittest

from persistent import Persistent
from zope.app.wsgi.testlayer import encodeMultipartFormdata
from zope.app.wsgi.testlayer import http
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope.interface import implementer
from zope.schema import Int
from zope.schema import List
from zope.schema import Text
from zope.schema import TextLine
from zope.testing import renormalizing

from zope.app.form.testing import AppFormLayer


_ = MessageFactory('formtest')

__docformat__ = "reStructuredText"


class IFieldContent(Interface):

    title = TextLine(
        title=_("Title"),
        description=_("A short description of the event."),
        default="",
        required=True
    )

    description = Text(
        title=_("Description"),
        description=_("A long description of the event."),
        default="",
        required=False
    )

    somenumber = Int(
        title=_("Some number"),
        default=0,
        required=False
    )

    somelist = List(
        title=_("Some List"),
        value_type=TextLine(title=_("Some item")),
        default=[],
        required=False
    )


@implementer(IFieldContent)
class FieldContent(Persistent):
    pass


checker = renormalizing.RENormalizing([
    (re.compile(r"HTTP/1\.0 200 .*"), "HTTP/1.1 200 OK"),
])


def test_suite():
    def setUp(test):
        wsgi_app = AppFormLayer.make_wsgi_app()

        def _http(query_str, *args, **kwargs):
            return http(wsgi_app, query_str, *args, **kwargs)

        test.globs['http'] = _http
        test.globs['encodeMultipartFormdata'] = encodeMultipartFormdata

    i18n = doctest.DocFileSuite('../i18n.rst',
                                setUp=setUp,
                                checker=checker,
                                optionflags=doctest.ELLIPSIS
                                | doctest.REPORT_NDIFF
                                | doctest.NORMALIZE_WHITESPACE)
    i18n.layer = AppFormLayer
    return unittest.TestSuite([
        i18n,
    ])
