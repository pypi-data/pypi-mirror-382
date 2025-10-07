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
"""Form and Widget specific 'browser' ZCML namespace interfaces"""
__docformat__ = 'restructuredtext'

from zope.browsermenu.field import MenuField
from zope.configuration.fields import GlobalInterface
from zope.configuration.fields import GlobalObject
from zope.configuration.fields import MessageID
from zope.configuration.fields import Path
from zope.configuration.fields import PythonIdentifier
from zope.configuration.fields import Tokens
from zope.interface import Interface
from zope.schema import Id
from zope.schema import TextLine
from zope.security.zcml import Permission


class ICommonInformation(Interface):
    """
    Common information for all successive directives
    """

    name = TextLine(
        title="Name",
        description="The name of the generated view.",
        required=True
    )

    schema = GlobalInterface(
        title="Schema",
        description="The schema from which the form is generated.",
        required=True
    )

    for_ = GlobalInterface(
        title="Interface",
        description="""
        The interface this page (view) applies to.

        The view will be for all objects that implement this
        interface. The schema is used if the for attribute is not
        specified.

        If the for attribute is specified, then the objects views must
        implement or be adaptable to the schema.""",
        required=False
    )

    permission = Permission(
        title="Permission",
        description="The permission needed to use the view.",
        required=True
    )

    layer = GlobalInterface(
        title="Layer",
        description="The later the view is in. Default: 'default'",
        required=False
    )

    template = Path(
        title="Template",
        description="An alternate template to use for the form.",
        required=False
    )

    class_ = GlobalObject(
        title="Class",
        description="""
        A class to provide custom widget definitions or methods to be
        used by a custom template.

        This class is used as a mix-in class. As a result, it needn't
        subclass any special classes, such as BrowserView.""",
        required=False
    )


class ICommonFormInformation(ICommonInformation):
    """
    Common information for browser forms
    """

    label = MessageID(
        title="Label",
        description="A label to be used as the heading for the form.",
        required=False
    )

    menu = MenuField(
        title="The browser menu to include the form in.",
        description="""
        Many views are included in menus. It's convenient to name the
        menu in the page directive, rather than having to give a
        separate menuItem directive.""",
        required=False
    )

    title = MessageID(
        title="Menu title",
        description="The browser menu label for the form.",
        required=False
    )

    fields = Tokens(
        title="Fields",
        description="""
        Here you can specify the names of the fields you wish to display.
        The order in this list is also the order the fields will
        be displayed in.  If this attribute is not specified, all schema fields
        will be displayed in the order specified in the schema itself.""",
        required=False,
        value_type=PythonIdentifier()
    )


class ICommonAddInformation(Interface):
    """
    Common information for add forms
    """

    content_factory = GlobalObject(
        title="Content factory",
        description="""
        An object to call to create new content objects.

        This attribute isn't used if a class is specified that
        implements createAndAdd.""",
        required=False
    )

    content_factory_id = Id(
        title="Content factory id",
        description="A factory id to create new content objects",
        required=False,
    )

    arguments = Tokens(
        title="Arguments",
        description="""
        A list of field names to supply as positional arguments to the
        factory.""",
        required=False,
        value_type=PythonIdentifier()
    )

    keyword_arguments = Tokens(
        title="Keyword arguments",
        description="""
        A list of field names to supply as keyword arguments to the
        factory.""",
        required=False,
        value_type=PythonIdentifier()
    )

    set_before_add = Tokens(
        title="Set before add",
        description="""
        A list of fields to be assigned to the newly created object
        before it is added.""",
        required=False,
        value_type=PythonIdentifier(),
    )

    set_after_add = Tokens(
        title="Set after add",
        description="""
        A list of fields to be assigned to the newly created object
        after it is added.""",
        required=False,
        value_type=PythonIdentifier()
    )


class IFormDirective(ICommonFormInformation):
    """
    Define an automatically generated form.

    The form directive does nto require the data to be stored in its context,
    but leaves the storing procedure to the to a method.
    """
    class_ = GlobalObject(
        title="Class",
        description="""
        A class to provide the `getData()` and `setData()` methods or
        completely custom methods to be used by a custom template.

        This class is used as a mix-in class. As a result, it needn't
        subclass any special classes, such as BrowserView.""",
        required=True
    )


class IEditFormDirective(ICommonFormInformation):
    """
    Define an automatically generated edit form

    The editform directive creates and registers a view for editing
    an object based on a schema.
    """


class ISubeditFormDirective(ICommonInformation):
    """
    Define a subedit form
    """

    label = TextLine(
        title="Label",
        description="A label to be used as the heading for the form.",
        required=False
    )

    fulledit_path = TextLine(
        title="Path (relative URL) to the full edit form",
        required=False
    )

    fulledit_label = MessageID(
        title="Label of the full edit form",
        required=False
    )


class IAddFormDirective(ICommonFormInformation, ICommonAddInformation):
    """
    Define an automatically generated add form

    The addform directive creates and registers a view for adding an
    object based on a schema.

    Adding an object is a bit trickier than editing an object, because
    the object the schema applies to isn't available when forms are
    being rendered.  The addform directive provides a customization
    interface to overcome this difficulty.

    See zope.app.form.browser.interfaces.IAddFormCustomization.
    """

    description = MessageID(
        title="A longer description of the add form.",
        description="""
        A UI may display this with the item or display it when the
        user requests more assistance.""",
        required=False
    )


class ISchemaDisplayDirective(ICommonFormInformation):
    """
    Define an automatically generated display form.

    The schemadisplay directive creates and registers a view for
    displaying an object based on a schema.
    """

    title = MessageID(
        title="The browser menu label for the edit form",
        description="This attribute defaults to 'Edit'.",
        required=False
    )


class IWidgetSubdirective(Interface):
    """Register custom widgets for a form.

    This directive allows you to quickly generate custom widget directives for
    a form.

    Besides the two required arguments, field and class, you can specify any
    amount of keyword arguments, e.g. style='background-color:#fefefe;'.
    The keywords will be stored as attributes on the widget instance. To see
    which keywords are sensible, you should look at the code of the specified
    widget class.
    """

    field = TextLine(
        title="Field Name",
        description="""
        The name of the field/attribute/property for which this widget will be
        used.""",
        required=True,
    )

    class_ = GlobalObject(
        title="Widget Class",
        description="""The class that will create the widget.""",
        required=False,
    )


# Arbitrary keys and values are allowed to be passed to the CustomWidget.
IWidgetSubdirective.setTaggedValue('keyword_arguments', True)
