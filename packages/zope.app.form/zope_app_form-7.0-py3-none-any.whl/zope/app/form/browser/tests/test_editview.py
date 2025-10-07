##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
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
"""Edit View Tests"""
import unittest

from zope.component.eventtesting import clearEvents
from zope.component.eventtesting import getEvents
from zope.component.testing import PlacelessSetup
from zope.formlib.interfaces import IInputWidget
from zope.interface import Interface
from zope.interface import implementer
from zope.location.interfaces import ILocation
from zope.publisher.browser import TestRequest
from zope.schema import TextLine
from zope.schema import accessors
from zope.schema.interfaces import ITextLine

import zope.app.form.testing as ztapi
from zope.app.form.browser import TextWidget
from zope.app.form.browser.editview import EditView
from zope.app.form.browser.submit import Update
from zope.app.form.tests import utils


class I(Interface):  # noqa: E742 ambiguous class definition 'I'
    foo = TextLine(title="Foo")
    bar = TextLine(title="Bar")
    a = TextLine(title="A")
    b = TextLine(title="B", min_length=0, required=False)
    getbaz, setbaz = accessors(TextLine(title="Baz"))


class EV(EditView):
    schema = I
    object_factories = []


@implementer(I)
class C:

    foo = "c foo"
    bar = "c bar"
    a = "c a"
    b = "c b"
    __Security_checker__ = utils.SchemaChecker(I)

    _baz = "c baz"
    def getbaz(self): return self._baz
    def setbaz(self, v): self._baz = v


class IFoo(Interface):
    foo = TextLine(title="Foo")


class IBar(Interface):
    bar = TextLine(title="Bar")


@implementer(IFoo)
class Foo:

    __Security_checker__ = utils.SchemaChecker(IFoo)

    foo = 'Foo foo'


@implementer(IFoo)
class ConformFoo:

    foo = 'Foo foo'

    def __conform__(self, interface):
        if interface is IBar:
            return OtherFooBarAdapter(self)


@implementer(IBar, ILocation)
class FooBarAdapter:

    __used_for__ = IFoo

    def __init__(self, context):
        self.context = context

    def getbar(self): return self.context.foo
    def setbar(self, v): self.context.foo = v

    bar = property(getbar, setbar)

    __Security_checker__ = utils.SchemaChecker(IBar)


class OtherFooBarAdapter(FooBarAdapter):
    pass


class BarV(EditView):
    schema = IBar
    object_factories = []


class Test(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super().setUp()
        ztapi.browserViewProviding(ITextLine, TextWidget, IInputWidget)
        ztapi.provideAdapter(IFoo, IBar, FooBarAdapter)
        clearEvents()

    def test_setPrefix_and_widgets(self):
        v = EV(C(), TestRequest())
        v.setPrefix("test")
        self.assertEqual(
            [w.name for w in v.widgets()],
            ['test.foo', 'test.bar', 'test.a', 'test.b', 'test.getbaz']
        )

    def test_empty_prefix(self):
        v = EV(C(), TestRequest())
        v.setPrefix("")
        self.assertEqual(
            [w.name for w in v.widgets()],
            ['foo', 'bar', 'a', 'b', 'getbaz']
        )

    def test_fail_wo_adapter(self):
        c = Foo()
        request = TestRequest()
        self.assertRaises(TypeError, EV, c, request)

    def test_update_no_update(self):
        c = C()
        request = TestRequest()
        v = EV(c, request)
        self.assertEqual(v.update(), '')
        self.assertEqual(c.foo, 'c foo')
        self.assertEqual(c.bar, 'c bar')
        self.assertEqual(c.a, 'c a')
        self.assertEqual(c.b, 'c b')
        self.assertEqual(c.getbaz(), 'c baz')
        request.form['field.foo'] = 'r foo'
        request.form['field.bar'] = 'r bar'
        request.form['field.a'] = 'r a'
        request.form['field.b'] = 'r b'
        request.form['field.getbaz'] = 'r baz'
        self.assertEqual(v.update(), '')
        self.assertEqual(c.foo, 'c foo')
        self.assertEqual(c.bar, 'c bar')
        self.assertEqual(c.a, 'c a')
        self.assertEqual(c.b, 'c b')
        self.assertEqual(c.getbaz(), 'c baz')
        self.assertFalse(getEvents())

    def test_update(self):
        c = C()
        request = TestRequest()
        v = EV(c, request)
        request.form[Update] = ''
        request.form['field.foo'] = 'r foo'
        request.form['field.bar'] = 'r bar'
        request.form['field.getbaz'] = 'r baz'
        request.form['field.a'] = 'c a'

        message = v.update()
        self.assertTrue(message.startswith('Updated '), message)
        self.assertEqual(c.foo, 'r foo')
        self.assertEqual(c.bar, 'r bar')
        self.assertEqual(c.a, 'c a')
        self.assertEqual(c.b, 'c b')  # missing from form - unchanged
        self.assertEqual(c.getbaz(), 'r baz')

        # Verify that calling update multiple times has no effect

        c.__dict__.clear()
        self.assertEqual(v.update(), message)
        self.assertEqual(c.foo, 'c foo')
        self.assertEqual(c.bar, 'c bar')
        self.assertEqual(c.a, 'c a')
        self.assertEqual(c.b, 'c b')
        self.assertEqual(c.getbaz(), 'c baz')

    def test_update_via_adapter(self):
        f = Foo()
        request = TestRequest()
        v = BarV(f, request)
        # check adapter
        self.assertEqual(f.foo, 'Foo foo')
        a = IBar(f)
        self.assertEqual(a.bar, 'Foo foo')
        # update
        request.form[Update] = ''
        request.form['field.bar'] = 'r bar'
        message = v.update()
        self.assertTrue(message.startswith('Updated '), message)
        self.assertEqual(a.bar, 'r bar')
        # wrong update
        self.assertFalse(getEvents())

    def test_setUpWidget_via_conform_adapter(self):

        f = ConformFoo()
        request = TestRequest()
        BarV(f, request)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
