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
$Id: vocabulary.py 5184 2025-03-24 12:27:39Z felipe.souza $
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from past.builtins import cmp
from zope.interface import provider
from zope.interface import implementer

import zope.interface
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from m01.i18n import interfaces


@implementer(interfaces.IAvailableLanguagesVocabulary)
@provider(IVocabularyFactory)
class AvailableLanguagesVocabulary(SimpleVocabulary):
    """A vocabular of available languages from the context object."""



    def __init__(self, context):
        terms = []
        
        # returns available languages form the object itself
        # but just after creation of the object
        try:
            languages = context.getAvailableLanguages()
        except AttributeError:
            languages = []

        for lang in languages:
            terms.append(SimpleTerm(lang, lang, lang))

        terms.sort(key=lambda term: term.title)
        super(AvailableLanguagesVocabulary, self).__init__(terms)
