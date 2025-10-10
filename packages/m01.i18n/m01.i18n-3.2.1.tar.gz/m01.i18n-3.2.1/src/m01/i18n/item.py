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
$Id: item.py 5184 2025-03-24 12:27:39Z felipe.souza $
"""
from __future__ import absolute_import
from builtins import str
from zope.interface import implementer

import datetime

import bson.objectid

import zope.interface
import zope.component
import zope.location.interfaces
import zope.security.management
import zope.i18n.interfaces

import m01.mongo.interfaces
import m01.mongo.base
import m01.mongo.item
from m01.mongo import UTC
from m01.mongo.fieldproperty import MongoFieldProperty

import m01.i18n.base
from m01.i18n import interfaces

_marker = object()


@implementer(interfaces.II18nMongoSubItem)
class I18nMongoSubItem(m01.i18n.base.I18nMongoSubItemBase):
    """I18n sub item
    This class stores the content for a single language. Inherit from this
    class and implement your content schema.
    """


@implementer(interfaces.II18nMongoContainerItem,
             m01.mongo.interfaces.IMongoParentAware,
             zope.location.interfaces.ILocation)
class I18nMongoContainerItem(m01.i18n.base.I18nMongoItemBase):
    """Simple mongo container item.

    Implement your own II18nMongoContainerItem with the attributes you need.
    """

    # validate __name__ and observe to set _m_changed
    __name__ = MongoFieldProperty(zope.location.interfaces.ILocation['__name__'])


@implementer(interfaces.II18nMongoStorageItem,
             m01.mongo.interfaces.IMongoParentAware,
             zope.location.interfaces.ILocation)
class I18nMongoStorageItem(m01.i18n.base.I18nMongoItemBase):
    """Simple mongo storage item.

    This MongoItem will use the mongo ObjectId as the __name__. This means
    you can't set an own __name__ value for this object.

    Implement your own II18nMongoStorageItem with the attributes you need.
    """

    _skipNames = ['__name__']

    @property
    def __name__(self):
        return str(self._id)


@implementer(interfaces.II18nMongoObject)
class I18nMongoObject(m01.i18n.base.I18nMongoItemCore,
                      m01.mongo.item.MongoObject):
    """MongoObject based item providing _oid as object reference"""

    _skipNames = ['_oid']
    _dumpNames = ['_id', '_oid', '__name__', '_type', '_version',
                  '_field',
                  'created', 'modified', 'removed',
                  'i18n', 'lang']
