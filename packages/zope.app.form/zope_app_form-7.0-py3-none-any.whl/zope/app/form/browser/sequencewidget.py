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
"""Browser widgets for sequences"""
# BBB implementation moved to zope.formlib.sequencewidget
from zope.formlib.sequencewidget import ListSequenceWidget
from zope.formlib.sequencewidget import SequenceDisplayWidget
from zope.formlib.sequencewidget import SequenceWidget
from zope.formlib.sequencewidget import TupleSequenceWidget


__all__ = [
    'ListSequenceWidget',
    'SequenceDisplayWidget',
    'SequenceWidget',
    'TupleSequenceWidget',
]
