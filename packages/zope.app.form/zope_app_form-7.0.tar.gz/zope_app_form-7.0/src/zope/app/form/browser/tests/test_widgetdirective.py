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
"""Tests for the <widget> subdirective for the generated form pages."""
import doctest
import unittest

import zope.component
import zope.component.testing
import zope.configuration.xmlconfig
import zope.formlib.interfaces
import zope.interface
import zope.publisher.browser
import zope.schema
from zope.browser.interfaces import IAdding

import zope.app.form.browser.interfaces
from zope.app.form.tests import utils


__docformat__ = "reStructuredText"


class IContent(zope.interface.Interface):

    field = zope.schema.TextLine(
        title="Field",
        description="Sample input field",
        required=False,
    )


@zope.interface.implementer(IContent)
class Content:

    __Security_checker__ = utils.SchemaChecker(IContent)

    __parent__ = None
    __name__ = "sample-content"

    field = None


@zope.interface.implementer(IAdding)
class Adding:

    def add(self, content):
        raise NotImplementedError("Don't actually get here")


class WidgetDirectiveTestCase(zope.component.testing.PlacelessSetup,
                              unittest.TestCase):

    def setUp(self):
        super().setUp()
        zope.configuration.xmlconfig.file("widgetDirectives.zcml",
                                          zope.app.form.browser.tests)

    def get_widget(self, name, context):
        request = zope.publisher.browser.TestRequest()
        view = zope.component.getMultiAdapter((context, request), name=name)
        return view.field_widget

    def test_addform_widget_without_class(self):
        w = self.get_widget("add.html", Adding())
        self.assertTrue(zope.formlib.interfaces.IInputWidget.providedBy(w))
        self.assertEqual(w.extraAttr, "42")

    def test_editform_widget_without_class(self):
        w = self.get_widget("edit.html", Content())
        self.assertTrue(zope.formlib.interfaces.IInputWidget.providedBy(w))
        self.assertEqual(w.extraAttr, "84")

    def test_subeditform_widget_without_class(self):
        w = self.get_widget("subedit.html", Content())
        self.assertTrue(zope.formlib.interfaces.IInputWidget.providedBy(w))
        self.assertEqual(w.extraAttr, "168")


def test_suite():
    return unittest.TestSuite((
        unittest.defaultTestLoader.loadTestsFromName(__name__),
        doctest.DocFileSuite("../widgets.rst")))
