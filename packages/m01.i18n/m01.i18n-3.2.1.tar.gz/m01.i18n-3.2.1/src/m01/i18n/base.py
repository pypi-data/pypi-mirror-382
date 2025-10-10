###############################################################################
#
# Copyright (c) 2018 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""
$Id: base.py 5675 2025-10-09 15:55:37Z roger.ineichen $
"""
from __future__ import absolute_import
from builtins import str
from zope.interface import implementer
from builtins import object
__docformat__ = "reStructuredText"

import datetime

import bson.objectid

import zope.interface
import zope.component
import zope.location.interfaces
import zope.security.management
import zope.i18n.interfaces

import m01.mongo.interfaces
import m01.mongo.base
from m01.mongo import UTC
from m01.mongo.fieldproperty import MongoFieldProperty

from m01.i18n import interfaces

_marker = object()


def getRequest():
    try:
        interaction = zope.security.management.getInteraction()
        request = interaction.participations[0]
    except zope.security.interfaces.NoInteraction:
        request = None
    except IndexError:
        request = None
    return request


###############################################################################
#
# item storing content for one language

class I18nMongoSubItemBase(m01.mongo.base.SetupConvertDump):
    """I18n sub item

    This class stores the content for a single language. Use I18nMongoSubItem
    which inherits from from this class for implement your content schema.
    """

    __name__ = None
    _type = None
    _m_changed_value = None

    # built in skip and dump names
    _skipNames = []
    _dumpNames = ['__name__', '_type', 'created', 'modified']

    # customize this in your implementation
    skipNames = []
    dumpNames = []

    created = MongoFieldProperty(interfaces.II18nMongoSubItem['created'])
    modified = MongoFieldProperty(interfaces.II18nMongoSubItem['modified'])

    def __init__(self, data):
        """Initialize a I18nMongoSubItem with given data."""
        # set given language as __name__
        __name__ = data.pop('__name__', _marker)
        if __name__ is not _marker:
            self.__dict__['__name__'] = __name__

        # set given or None __parent__
        __parent__ = data.pop('__parent__', None)
        if __parent__ is not None:
            self.__parent__ = __parent__

        # set given or new _type
        _type = data.pop('_type', self.__class__.__name__)
        if _type != self.__class__.__name__:
            raise TypeError("Wrong mongo item _type used")
        self.__dict__['_type'] = str(_type)

        # set given or new created datetime
        created = data.pop('created', _marker)
        if created is _marker:
            created = datetime.datetime.now(UTC)
        self.__dict__['created'] = created

        # update object with given key/value data
        self.setup(data)

        # it is very important to set _m_changed_value to None, otherwise each
        # read access will end in a write access.
        self._m_changed_value = None

    def _m_changed():
        def fget(self):
            return self._m_changed_value
        def fset(self, value):
            if value == True:
                self._m_changed_value = value
                if self.__parent__ is not None:
                    self.__parent__._m_changed = value
            elif value != True:
                raise ValueError("Can only dispatch True to __parent__")
        return property(fget, fset)

    _m_changed = _m_changed()

    def dump(self, dumpNames=None, dictify=False):
        if self._m_changed and (dumpNames is None or 'modified' in dumpNames):
            self.modified = datetime.datetime.now(UTC)
        return super(I18nMongoSubItemBase, self).dump(dumpNames)


###############################################################################
#
# contains items for each language

class I18nMongoItemCore(object):
    """II18n mongo item core class

    This class provides the i18n related attributes and methods for
    store your content per language locale and can get used for any
    i18n implementation.
    """

    # default language
    _lang = MongoFieldProperty(interfaces.II18nItem['lang'])
    i18n = MongoFieldProperty(interfaces.II18nItem['i18n'])

    # built in skip and dump names
    _dumpNames = ['_id', '_pid', '_type', '_version', '__name__',
                  'created', 'modified',
                  'i18n', 'lang']

    # Subclass MUST implement own converter and use the relevant class for i18n
    # converters = {'i18n': I18nMongoSubItem}
    @property
    def converters(self):
        raise NotImplementedError(
            "Subclass must implement converters property providing own item "
            "converters")

    # II18nRead
    def lang():
        def fget(self):
            return self._lang
        def fset(self, lang):
            if not lang:
                raise ValueError("Can't set an empty value as language", lang)
            if self._m_initialized and lang not in self.i18n:
                raise ValueError(
                    'cannot set non existent lang (%s) as default' % lang)
            self._lang = str(lang)
        return property(fget, fset)

    lang = lang()

    def getAvailableLanguages(self):
        keys = list(self.i18n.keys())
        keys.sort()
        return keys

    def getPreferedLanguage(self):
        # evaluate the negotiator
        lang = None
        request = getRequest()
        negotiator = None
        try:
            negotiator = zope.component.queryUtility(
                zope.i18n.interfaces.INegotiator, name='', context=self)
        except zope.component.ComponentLookupError:
            # can happens during tests without a site and sitemanager
            pass
        if request is not None and negotiator is not None:
            lang = negotiator.getLanguage(self.getAvailableLanguages(), request)
        if lang is None:
            lang = self.lang
        if lang is None:
            # fallback lang for functional tests, there we have a cookie request
            lang = 'en'
        return lang

    def getAttribute(self, name, lang=None):
        # preconditions
        if lang is None:
            lang = self.lang

        if not lang in self.getAvailableLanguages():
            raise KeyError(lang)

        # essentials
        data = self.i18n[lang]
        return getattr(data, name)

    def queryAttribute(self, name, lang=None, default=None):
        try:
            return self.getAttribute(name, lang)
        except (KeyError, AttributeError):
            return default

    # II18nRead
    def addLanguage(self, lang, obj):
        if not (obj.__name__ is None or obj.__name__ == lang):
            raise TypeError("Obj must provide the lang as __name__ or None")
        obj.__name__ = lang
        self.i18n.append(obj)

    def removeLanguage(self, lang):
        if lang == self.lang:
            raise ValueError('cannot remove default lang (%s)' % lang)
        elif lang not in self.i18n:
            raise ValueError('cannot remove non existent lang (%s)'
                % lang)
        else:
            del self.i18n[lang]
            self._m_changed = True

    def setAttributes(self, lang, **kws):
        # preconditions
        if not lang in self.getAvailableLanguages():
            raise KeyError(lang)

        obj = self.i18n[lang]

        for key in kws:
            if not hasattr(obj, key):
                raise KeyError(key)

        # essentials
        for key in kws:
            setattr(obj, key, kws[key])
        else:
            self._m_changed = True


@implementer(interfaces.II18nItem)
class I18nMongoItemBase(I18nMongoItemCore, m01.mongo.base.MongoItemBase):
    """II18n mongo item base class

    This class is inherited from I18nMongoItemCore and also provides the i18n
    related attributes and methods for store your content per language locale.

    The class can get used as base for all container or storage items but not
    for MongoObject items. The I18nMongoObject items uses I18nMongoItemCore
    as base and prevents to inherit from MongoItemBase because of import order.
    """

