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
$Id: tests.py 5184 2025-03-24 12:27:39Z felipe.souza $
"""
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import doctest
import unittest

import m01.i18n.testing
from m01.i18n import interfaces


class I18nMongoSubItemTest(m01.i18n.testing.BaseTestI18nMongoSubItem):

    def getTestInterface(self):
        return interfaces.II18nMongoSubItem

    def getTestClass(self):
        return m01.i18n.item.I18nMongoSubItem


class I18nMongoContainerItemTest(m01.i18n.testing.I18nMongoContainerItemBaseTest):

    def makeI18nTestSubObject(self):
        return m01.i18n.item.I18nMongoSubItem({})

    def getTestInterface(self):
        return interfaces.II18nMongoContainerItem

    def getTestClass(self):
        return m01.i18n.item.I18nMongoContainerItem


class I18nMongoStorageItemTest(m01.i18n.testing.I18nMongoStorageItemBaseTest):

    def makeI18nTestSubObject(self):
        return m01.i18n.item.I18nMongoSubItem({})

    def getTestInterface(self):
        return interfaces.II18nMongoStorageItem

    def getTestClass(self):
        return m01.i18n.item.I18nMongoStorageItem


def test_suite():
    suites = [
        unittest.makeSuite(I18nMongoSubItemTest),
        unittest.makeSuite(I18nMongoContainerItemTest),
        unittest.makeSuite(I18nMongoStorageItemTest),
        doctest.DocFileSuite('README.txt',
                              globs={'print_function': print_function,
                                     'absolute_import': absolute_import,
                                     'unicode_literals': unicode_literals,},
                             setUp=m01.i18n.testing.setUpFakeMongo,
            tearDown=m01.i18n.testing.tearDownFakeMongo,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ]
    # level 2 test using a mongo stub
    suite = unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
                             globs={'print_function': print_function,
                                    'absolute_import': absolute_import,
                                    'unicode_literals': unicode_literals, },
                             setUp=m01.i18n.testing.setUpStubMongo,
        tearDown=m01.i18n.testing.tearDownStubMongo,
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ))
    suite.level = 2
    suites.append(suite)

    # return test suite
    return unittest.TestSuite(suites)

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
