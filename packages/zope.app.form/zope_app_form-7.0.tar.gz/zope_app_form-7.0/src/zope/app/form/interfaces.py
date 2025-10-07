##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
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
"""Validation Exceptions

This has been moved to zope.formlib.interfaces.
"""


# this moved to zope.formlib.interfaces
from zope.formlib.interfaces import ConversionError
from zope.formlib.interfaces import ErrorContainer
from zope.formlib.interfaces import IDisplayWidget
from zope.formlib.interfaces import IInputWidget
from zope.formlib.interfaces import InputErrors
from zope.formlib.interfaces import IWidget
from zope.formlib.interfaces import IWidgetFactory
from zope.formlib.interfaces import IWidgetInputError
from zope.formlib.interfaces import MissingInputError
from zope.formlib.interfaces import WidgetInputError
from zope.formlib.interfaces import WidgetsError


__all__ = [
    'ConversionError',
    'ErrorContainer',
    'IDisplayWidget',
    'IInputWidget',
    'IWidget',
    'IWidgetFactory',
    'IWidgetInputError',
    'InputErrors',
    'MissingInputError',
    'WidgetInputError',
    'WidgetsError',
]
