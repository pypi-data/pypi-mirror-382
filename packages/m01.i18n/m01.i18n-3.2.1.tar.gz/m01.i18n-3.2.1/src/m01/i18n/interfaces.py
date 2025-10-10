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
$Id: interfaces.py 5184 2025-03-24 12:27:39Z felipe.souza $
"""
from __future__ import absolute_import
__docformat__ = 'restructuredtext'

import zope.interface
import zope.schema.interfaces

import m01.mongo.interfaces


class II18nMongoSubItem(m01.mongo.interfaces.IMongoSubItem):
    """I18nSubItem"""


class II18nRead(zope.interface.Interface):
    """Let the language switch to the desired language.

    Support add and remove objects of a language.
    """
    def addLanguage(lang, obj):
        """Add item for given langauge"""

    def getPreferedLanguage():
        """Return the best matching language."""

    def getAvailableLanguages():
        """Find all the languages that are available."""

    def getAttribute(name, lang=None):
        """Get name attribute of the language specific translation.

        Parameter:

        name -- Attribute name.

        language -- Language code for example 'de'. If None the default language
        is returned.

        Return Value:

        object -- Evaluate of the language specific data object.

        Exceptions:

        KeyError -- If attribute or language code does not exists.

        """

    def queryAttribute(name, lang=None, default=None):
        """Get name attribute of the language specific translation or default.

        Parameter:

        name -- Attribute name.

        language -- Language code for example 'de'. If None the default language
        is returned.

        default -- Any object.

        Return Value:

        object -- Evaluate of the language specific data object or return default
        if not found.

        """


class II18nWrite(zope.interface.Interface):
    """Let the language switch to the desired language.

    Support add and remove objects of a language.
    """

    def removeLanguage(lang):
        """Remove the object under the given language."""

    def setAttributes(lang, **kws):
        """Set the language specific attribute of the translation defined by kw.

        Parameter:

        language -- Language code for example ``'de'``

        kws -- Attributes that have to be set as keyword value pairs.

        Exceptions:

        KeyError -- If attribute does not exists.

        """


class II18nAware(II18nRead, II18nWrite):
    """Read and write support for I18n objects."""


class II18nItem(II18nAware):
    """I18n aware item"""

    lang = zope.schema.TextLine(
        title=u'Default language',
        description=u'Default language',
        default=u'de',
        required=True)

    # i18n items
    i18n = m01.mongo.schema.MongoList(
        title=u'List of i18n sub items',
        description=u'List of i18n sub items',
        value_type=zope.schema.Object(
            title=u'i18n sub item',
            description=u'i18n sub item',
            schema=II18nMongoSubItem,
            required=True),
        default=[],
        required=False)


class II18nMongoContainerItem(II18nItem, m01.mongo.interfaces.IMongoContainerItem):
    """II18nAware mongo container item"""

class II18nMongoStorageItem(II18nItem, m01.mongo.interfaces.IMongoStorageItem):
    """II18nAware mongo container item"""

class II18nMongoObject(II18nItem, m01.mongo.interfaces.IMongoObject):
    """II18nAware mongo object"""


class II18nSwitch(zope.interface.Interface):
    """Let the language switch to the desired language."""

    lang = zope.schema.TextLine(
        title=u'Default language',
        description=u'Default language',
        default=u'de',
        required=True)


class IAvailableLanguages(zope.interface.Interface):

    def getAvailableLanguages():
        """Returns a list of available languages if we provide II18nRead"""

    def hasAvailableLanguages():
        """View for to check if we have i18n support on a context."""


class IAvailableLanguagesVocabulary(zope.schema.interfaces.IVocabularyTokenized):
    """Available languages."""

