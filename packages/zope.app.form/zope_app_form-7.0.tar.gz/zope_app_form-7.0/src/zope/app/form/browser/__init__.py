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
"""Browser widgets"""
__docformat__ = 'restructuredtext'

# the implementation of widgets has moved to zope.formlib.widgets
# import directly from there instead.

from zope.formlib.widget import BrowserWidget
from zope.formlib.widget import DisplayWidget
from zope.formlib.widget import UnicodeDisplayWidget
from zope.formlib.widgets import ASCIIAreaWidget
from zope.formlib.widgets import ASCIIDisplayWidget
from zope.formlib.widgets import ASCIIWidget
from zope.formlib.widgets import BooleanDropdownWidget
from zope.formlib.widgets import BooleanRadioWidget
from zope.formlib.widgets import BooleanSelectWidget
from zope.formlib.widgets import BytesAreaWidget
from zope.formlib.widgets import BytesDisplayWidget
from zope.formlib.widgets import BytesWidget
from zope.formlib.widgets import CheckBoxWidget
from zope.formlib.widgets import ChoiceCollectionDisplayWidget
from zope.formlib.widgets import ChoiceCollectionInputWidget
from zope.formlib.widgets import ChoiceDisplayWidget
from zope.formlib.widgets import ChoiceInputWidget
from zope.formlib.widgets import CollectionDisplayWidget
from zope.formlib.widgets import CollectionInputWidget
from zope.formlib.widgets import DateDisplayWidget
from zope.formlib.widgets import DateI18nWidget
from zope.formlib.widgets import DatetimeDisplayWidget
from zope.formlib.widgets import DatetimeI18nWidget
from zope.formlib.widgets import DatetimeWidget
from zope.formlib.widgets import DateWidget
from zope.formlib.widgets import DecimalWidget
from zope.formlib.widgets import DropdownWidget
from zope.formlib.widgets import FileWidget
from zope.formlib.widgets import FloatWidget
from zope.formlib.widgets import IntWidget
from zope.formlib.widgets import ItemDisplayWidget
from zope.formlib.widgets import ItemsMultiDisplayWidget
from zope.formlib.widgets import ListDisplayWidget
from zope.formlib.widgets import ListSequenceWidget
from zope.formlib.widgets import MultiCheckBoxWidget
from zope.formlib.widgets import MultiSelectFrozenSetWidget
from zope.formlib.widgets import MultiSelectSetWidget
from zope.formlib.widgets import MultiSelectWidget
from zope.formlib.widgets import ObjectWidget
from zope.formlib.widgets import OrderedMultiSelectWidget
from zope.formlib.widgets import PasswordWidget
from zope.formlib.widgets import RadioWidget
from zope.formlib.widgets import SelectWidget
from zope.formlib.widgets import SequenceDisplayWidget
from zope.formlib.widgets import SequenceWidget
from zope.formlib.widgets import SetDisplayWidget
from zope.formlib.widgets import TextAreaWidget
from zope.formlib.widgets import TextWidget
from zope.formlib.widgets import TupleSequenceWidget
from zope.formlib.widgets import URIDisplayWidget


__all__ = [
    'BrowserWidget',
    'DisplayWidget',
    'UnicodeDisplayWidget',
    'TextWidget',
    'BytesWidget',
    'TextAreaWidget',
    'BytesAreaWidget',
    'PasswordWidget',
    'FileWidget',
    'ASCIIWidget',
    'ASCIIAreaWidget',
    'IntWidget',
    'FloatWidget',
    'DecimalWidget',
    'DatetimeWidget',
    'DateWidget',
    'DatetimeI18nWidget',
    'DateI18nWidget',
    'DatetimeDisplayWidget',
    'DateDisplayWidget',
    'BytesDisplayWidget',
    'ASCIIDisplayWidget',
    'URIDisplayWidget',
    'CheckBoxWidget',
    'BooleanRadioWidget',
    'BooleanSelectWidget',
    'BooleanDropdownWidget',
    'ItemDisplayWidget',
    'ItemsMultiDisplayWidget',
    'SetDisplayWidget',
    'ListDisplayWidget',
    'ChoiceDisplayWidget',
    'ChoiceInputWidget',
    'CollectionDisplayWidget',
    'CollectionInputWidget',
    'ChoiceCollectionDisplayWidget',
    'ChoiceCollectionInputWidget',
    'SelectWidget',
    'DropdownWidget',
    'RadioWidget',
    'MultiSelectWidget',
    'MultiSelectSetWidget',
    'MultiSelectFrozenSetWidget',
    'MultiCheckBoxWidget',
    'OrderedMultiSelectWidget',
    'SequenceWidget',
    'TupleSequenceWidget',
    'ListSequenceWidget',
    'SequenceDisplayWidget',
    'ObjectWidget',
]
