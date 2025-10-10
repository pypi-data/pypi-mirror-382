##############################################################################
#
# Copyright (c) 2013 Zope Foundation and Contributors.
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
"""
$Id: fieldproperty.py 5184 2025-03-24 12:27:39Z felipe.souza $
"""
from __future__ import absolute_import
from builtins import object
__docformat__ = 'restructuredtext'

_marker = object()


class I18nFieldProperty(object):
    """Computed attributes based on schema fields and i18n implementation.

    Field properties provide default values, data validation and error messages
    based on data found in field meta-data.

    Note that I18nFieldProperties can only be used for attributes stored in
    a translation object. The class using this I18nFieldProperty must implement
    II18nAware.
    """

    def __init__(self, field, name=None):
        if name is None:
            name = field.__name__

        self.__field = field
        self.__name = name

    def __get__(self, inst, klass):
        if inst is None:
            return self

        value = inst.queryAttribute(self.__name, inst.getPreferedLanguage(), _marker)
        if value is _marker:
            field = self.__field.bind(inst)
            value = getattr(field, 'default', _marker)
            if value is _marker:
                raise AttributeError(self.__name)

        return value

    def __set__(self, inst, value):
        field = self.__field.bind(inst)
        field.validate(value)
        # make kws dict
        kws = {}
        kws[self.__name] = value
        inst.setAttributes(inst.getPreferedLanguage(), **kws)

    def __getattr__(self, name):
        return getattr(self.__field, name)


class I18nSwitchProperty(object):
    """Computed attributes based on schema fields and i18n language switch
    implementation.

    Field properties provide default values, data validation and error messages
    based on data found in field meta-data.

    Note that I18nSwitchProperty can only be used for attributes stored in
    self.i18n.
    
    If you use this field in simply object, there is a adapter called 
    'I18nSwitch' where the context attribute is setting to i18n. 
    """

    def __init__(self, field, name=None):
        if name is None:
            name = field.__name__

        self.__field = field
        self.__name = name

    def __get__(self, inst, klass):
        # essentails
        if inst is None:
            return self
        i18n = inst.i18n
        lang = inst.lang

        value = i18n.queryAttribute(self.__name, inst.lang, _marker)
        if value is _marker:
            field = self.__field.bind(inst)
            value = getattr(field, 'default', _marker)
            if value is _marker:
                raise AttributeError(self.__name)

        return value

    def __set__(self, inst, value):
        # essentails
        i18n = inst.i18n

        field = self.__field.bind(inst)
        field.validate(value)
        # make kws dict
        kws = {}
        kws[self.__name] = value
        i18n.setAttributes(inst.lang, **kws)

    def __getattr__(self, name):
        return getattr(self.__field, name)
