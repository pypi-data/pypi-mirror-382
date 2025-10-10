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
$Id: __init__.py 5184 2025-03-24 12:27:39Z felipe.souza $
"""
from __future__ import absolute_import
__docformat__ = 'restructuredtext'
from zope.interface import implementer
from zope.interface import implementer_only

import os

import pymongo

import zope.interface
import zope.component.testing
from zope.schema.fieldproperty import FieldProperty
from zope.interface.verify import verifyClass

import m01.mongo
import m01.mongo.testing
import m01.fake.client
import m01.stub.testing

import m01.i18n.item
import m01.i18n.switch
from m01.i18n import interfaces
from m01.i18n.fieldproperty import I18nFieldProperty
from m01.i18n.fieldproperty import I18nSwitchProperty


def sorted(list):
    list.sort()
    return list


################################################################################
#
# test setup
#
################################################################################

# fake client
from m01.fake import FakeMongoClient

# fake mongodb setup
def setUpFakeMongo(test=None):
    """Setup fake (singleton) mongo client"""
    global _testClient
    host = 'localhost'
    port = 45017
    tz_aware = True
    storage = m01.fake.client.DatabaseStorage
    _testClient = FakeMongoClient(host, port, tz_aware=tz_aware,
        storage=storage)


def tearDownFakeMongo(test=None):
    """Tear down fake mongo client"""
    # reset test client
    global _testClient
    _testClient = None
    # clear thread local transaction cache
    m01.mongo.clearThreadLocalCache()


# stub mongodb server
def setUpStubMongo(test=None):
    """Setup pymongo client as test client and setup a real empty mongodb"""
    host = 'localhost'
    port = 45017
    tz_aware = True
    sandBoxDir = os.path.join(os.path.dirname(__file__), 'sandbox')
    import m01.stub.testing
    m01.stub.testing.startMongoServer(host, port, sandBoxDir=sandBoxDir)
    # setup pymongo.MongoClient as test client
    global _testClient
    _testClient = pymongo.MongoClient(host, port, tz_aware=tz_aware)


def tearDownStubMongo(test=None):
    """Tear down real mongodb"""
    # stop mongodb server
    sleep = 0.5
    import m01.stub.testing
    m01.stub.testing.stopMongoServer(sleep)
    # reset test client
    global _testClient
    _testClient = None
    # clear thread local transaction cache
    m01.mongo.clearThreadLocalCache()


################################################################################
#
# Public Base Tests
#
################################################################################

class BaseTestI18nMongoSubItem(m01.mongo.testing.MongoSubItemBaseTest):
    """I18nMongoSubItem base test"""

    def test_mongo_id(self):
        pass

    def test_name(self):
        obj = self.makeTestObject()
        self.assertEqual(obj.__name__, None)


class BaseTestI18nAware(m01.mongo.testing.MongoItemBaseTest):
    """I18nAware base test"""

    def getTestInterface(self):
        raise NotImplementedError('Subclasses has to implement getTestInterface()')

    def makeI18nTestSubObject(self, data=None):
        raise NotImplementedError('Subclasses has to implement makeI18nTestSubObject()')

    def makeI18nTestObject(self, data=None):
        return self.makeTestObject(data)

    # II18nRead tests
    def test_getAvailableLanguages(self):
        i18n = self.makeI18nTestObject()
        self.assertEqual(sorted(i18n.getAvailableLanguages()), [])

    def test_get_lang(self):
        i18n = self.makeI18nTestObject()
        self.assertEqual(i18n.lang, u'de')

    # II18nWrite tests
    def test_set_lang(self):
        i18n = self.makeI18nTestObject()
        self.assertEqual(i18n.lang, u'de')
        obj = self.makeI18nTestSubObject()
        i18n.addLanguage('en', obj)
        i18n.lang = u'en'
        self.assertEqual(i18n.lang, u'en')

    def test_addLanguage(self):
        i18n = self.makeI18nTestObject()
        obj = self.makeI18nTestSubObject()
        i18n.addLanguage('at', obj)
        obj = self.makeI18nTestSubObject()
        i18n.addLanguage('de', obj)
        res = [u'at', u'de']
        self.assertEqual(sorted(i18n.getAvailableLanguages()), res)

    def test_removeLanguage(self):
        i18n = self.makeI18nTestObject()
        obj = self.makeI18nTestSubObject()
        i18n.addLanguage('de', obj)
        obj = self.makeI18nTestSubObject()
        i18n.addLanguage('fr', obj)
        res = [u'de',u'fr']
        self.assertEqual(sorted(i18n.getAvailableLanguages()), res)
        i18n.removeLanguage('fr')
        res = ['de']
        self.assertEqual(sorted(i18n.getAvailableLanguages()), res)
        self.assertRaises(ValueError, i18n.removeLanguage, u'de')
        self.assertRaises(ValueError, i18n.removeLanguage, 'undefined')

    def test_II18nAware_Interface(self):
        i18n = self.makeI18nTestObject()
        class_ = self.getTestClass()
        self.failUnless(interfaces.II18nRead.implementedBy(class_))
        self.failUnless(interfaces.II18nWrite.implementedBy(class_))
        self.failUnless(interfaces.II18nAware.implementedBy(class_))
        self.failUnless(verifyClass(interfaces.II18nRead, class_))
        self.failUnless(verifyClass(interfaces.II18nWrite, class_))
        self.failUnless(verifyClass(interfaces.II18nAware, class_))


class I18nMongoContainerItemBaseTest(BaseTestI18nAware):
    """I18n mongo container item base test"""

    def test_name(self):
        obj = self.makeTestObject()
        self.assertEqual(obj.__name__, None)


class I18nMongoStorageItemBaseTest(BaseTestI18nAware):
    """I18n mongo storage item base test"""


class BaseTestI18nSwitch(m01.mongo.testing.MongoItemBaseTest):
    """I18nSwitch base test"""

    def getTestClass(self):
        raise NotImplementedError('Subclasses has to implement getTestClass()')

    def getTestInterface(self):
        raise NotImplementedError('Subclasses has to implement getTestInterface()')

    def getAdaptedClass(self):
        raise NotImplementedError('Subclasses has to implement getAdaptedClass()')

    def setUp(self):
        zope.component.testing.setUp()
        factory = self.getTestClass()
        iface = self.getTestInterface()
        required = self.getAdaptedClass()
        # register language switch for test interface adapter
        zope.component.provideAdapter(factory, (required,), iface)

    def tearDown(self):
        zope.component.testing.tearDown()

    def test_get_lang(self):
        obj = self.makeTestObject()
        self.assertEqual(obj.lang, u'de')

    def test_set_lang(self):
        obj = self.makeTestObject()
        obj.lang = u'fr'
        self.assertEqual(obj.lang, u'fr')

    def test_i18n_II18nSwitch_Interface(self):
        class_ = self.getTestClass()
        obj = self.makeTestObject()
        iface = self.getTestInterface()
        adapter = iface(obj)
        self.failUnless(interfaces.II18nSwitch.implementedBy(class_))
        self.failUnless(verifyClass(interfaces.II18nSwitch, class_))
        self.failUnless(iface.providedBy(adapter))


################################################################################
#
# Test implementation
#
################################################################################

class IContent(zope.interface.Interface):
    """IContent interface."""

    title = zope.schema.TextLine(
        title=u'Title',
        description=u'Title',
        required=True
        )

    description = zope.schema.Text(
        title=u'Description',
        description=u'Description',
        required=True
        )

class II18nContent(IContent):
    """II18nContent interface."""


class II18nContentSwitch(II18nContent, interfaces.II18nSwitch):
    """I18n language switch for ILetterTemplate."""


@implementer(IContent)
class Content(m01.i18n.item.I18nMongoSubItem):
    """Content type."""


    title = FieldProperty(IContent['title'])
    description = FieldProperty(IContent['description'])

    dumpNames = ['title', 'description']


@implementer(II18nContent, interfaces.II18nRead,
        interfaces.II18nWrite)
class I18nContent(m01.i18n.item.I18nMongoContainerItem):
    """i18n content type."""

    title = I18nFieldProperty(II18nContent['title'])
    description = I18nFieldProperty(II18nContent['description'])

    # title and decsription do not get dumped. We only dump them in IContent
    dumpNames = []

    converters = {'i18n': Content}


@implementer_only(II18nContentSwitch)
class I18nContentSwitch(m01.i18n.switch.I18nSwitch, m01.i18n.switch.I18nAdapter):
    """Language switch for I18nContent."""

    zope.component.adapts(IContent)

    title = I18nSwitchProperty(IContent['title'])
    description = I18nSwitchProperty(IContent['description'])
