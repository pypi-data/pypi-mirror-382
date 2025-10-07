##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Tests for the ZCML Documentation Module"""
import doctest
import re
import unittest

from zope.component import testing
from zope.formlib.interfaces import IInputWidget
from zope.schema.interfaces import ITextLine
from zope.testing import renormalizing

import zope.app.form.testing as ztapi
from zope.app.form.browser import TextWidget


checker = renormalizing.RENormalizing([
    (re.compile("u('.*?')"), r"\1"),
    (re.compile('u(".*?")'), r"\1"),
])


def setUp(test):
    testing.setUp()
    ztapi.browserViewProviding(ITextLine, TextWidget, IInputWidget)


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('../form.rst',
                             setUp=setUp, tearDown=testing.tearDown,
                             optionflags=doctest.NORMALIZE_WHITESPACE
                             | doctest.IGNORE_EXCEPTION_DETAIL),
    ))
