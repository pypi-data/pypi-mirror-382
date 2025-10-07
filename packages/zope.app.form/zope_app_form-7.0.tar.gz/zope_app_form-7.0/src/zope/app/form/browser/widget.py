##############################################################################
#
# Copyright (c) 2001-2004 Zope Foundation and Contributors.
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
"""Browser Widget Definitions"""
__docformat__ = 'restructuredtext'

# BBB
from zope.formlib.widget import BrowserWidget
from zope.formlib.widget import DisplayWidget
from zope.formlib.widget import SimpleInputWidget
from zope.formlib.widget import UnicodeDisplayWidget
from zope.formlib.widget import escape
from zope.formlib.widget import quoteattr
from zope.formlib.widget import renderElement
from zope.formlib.widget import renderTag
from zope.formlib.widget import setUp
from zope.formlib.widget import tearDown


__all__ = [
    'quoteattr',
    'BrowserWidget',
    'SimpleInputWidget',
    'DisplayWidget',
    'UnicodeDisplayWidget',
    'renderTag',
    'renderElement',
    'escape',
    'setUp',
    'tearDown',
]
