=================
Langauge Switcher
=================

Let's show how this i18n aware object implementation works:

Imports and placeless setup:

  >>> from __future__ import unicode_literals
  >>> from pprint import pprint
  >>> import zope.component
  >>> from m01.i18n.interfaces import II18nSwitch
  >>> from m01.i18n.testing import IContent
  >>> from m01.i18n.testing import II18nContent
  >>> from m01.i18n.testing import I18nContent
  >>> from m01.i18n.testing import I18nContentSwitch
  >>> from m01.i18n.testing import Content

Setup test object:

  >>> data = {'lang': 'en',
  ...         u'i18n': [{'__name__': 'en', 'title': 'en_title'}]}
  >>> obj = I18nContent(data)
  >>> obj.i18n
  [<Content ...'en'>]

  >>> print(obj.i18n['en'])
  <Content ...'en'>

  >>> print(obj.i18n['en'].title)
  en_title

  >>> print(obj.title)
  en_title

Add additional languages:

  >>> data = {'title': 'de_title'}
  >>> deObj = Content(data)
  >>> obj.addLanguage('de', deObj)

  >>> data = {'title': 'fr_title'}
  >>> frObj = Content(data)
  >>> obj.addLanguage('fr', frObj)

Switch default language:

  >>> print(obj.title)
  en_title

  >>> obj.lang = 'de'
  >>> print(obj.title)
  de_title

Remove the 'en' language object:

  >>> sorted(obj.i18n.keys())
  [...'de', ...'en', ...'fr']
  >>> obj.removeLanguage('en')
  >>> sorted(obj.i18n.keys())
  [...'de', ...'fr']

Remove default language object will end in a ``ValueError`` error:

  >>> obj.removeLanguage('de')
  Traceback (most recent call last):
  ...
  ValueError: cannot remove default lang (de)

Remove non existent language object will end in a ``ValueError`` error:

  >>> obj.removeLanguage('undefined')
  Traceback (most recent call last):
  ...
  ValueError: cannot remove non existent lang (undefined)

Set default language to a non existent lang will end in a ``ValueError``:

  >>> obj.lang = 'en'
  Traceback (most recent call last):
  ...
  ValueError: cannot set non existent lang (en) as default

Access the language directly via the ``II18nSwitch`` adapter. But first
register the adapter for the ``I18nContent``:

  >>> zope.component.provideAdapter(I18nContentSwitch,
  ...     (II18nContent,), provides=II18nSwitch)

The adapter is set to the default language in the init method:

  >>> adapted = II18nSwitch(obj)
  >>> print(adapted.title)
  de_title

Change the default language and access the title again, the title should not
switch to another language:

  >>> obj.lang = 'fr'
  >>> print(adapted.title)
  de_title

Switch the language to 'fr'  via the adapter:

  >>> adapted.lang = 'fr'
  >>> print(adapted.title)
  fr_title


Let's see what the mongodb data will look like:

  >>> pprint(obj.dump(dictify=True))
  {'__name__': None,
   '_id': ObjectId('...'),
   '_pid': None,
   '_type': 'I18nContent',
   '_version': 0,
   'created': datetime.datetime(..., tzinfo=UTC),
   'i18n': [{'__name__': ...'de',
             '_type': 'Content',
             'created': datetime.datetime(..., tzinfo=UTC),
             'description': None,
             'modified': None,
             'title': ...'de_title'},
            {'__name__': ...'fr',
             '_type': 'Content',
             'created': datetime.datetime(..., tzinfo=UTC),
             'description': None,
             'modified': None,
             'title': ...'fr_title'}],
   'lang': 'fr',
   'modified': None}


Now let's switch the language back to 'de'  via the adapter and check if the
default language doesn't get changed. This is important, otherwise we will
on any language switch force a write operation:

  >>> adapted.lang = 'de'
  >>> print(adapted.title)
  de_title

  >>> pprint(obj.dump(dictify=True))
  {'__name__': None,
   '_id': ObjectId('...'),
   '_pid': None,
   '_type': 'I18nContent',
   '_version': 0,
   'created': datetime.datetime(..., tzinfo=UTC),
   'i18n': [{'__name__': ...'de',
             '_type': 'Content',
             'created': datetime.datetime(..., tzinfo=UTC),
             'description': None,
             'modified': None,
             'title': ...'de_title'},
            {'__name__': ...'fr',
             '_type': 'Content',
             'created': datetime.datetime(..., tzinfo=UTC),
             'description': None,
             'modified': None,
             'title': ...'fr_title'}],
   'lang': 'fr',
   'modified': None}


AvailableLanguagesVocabulary
----------------------------

Use this vocabulary for get the available languages from the object
itself.

  >>> from m01.i18n import vocabulary
  >>> vocab = vocabulary.AvailableLanguagesVocabulary(obj)
  >>> len(vocab._terms)
  2

  >>> print(vocab._terms[0].value)
  de

  >>> print(vocab._terms[0].token)
  de

  >>> print(vocab._terms[0].title)
  de

  >>> print(vocab._terms[1].value)
  fr

  >>> print(vocab._terms[1].token)
  fr

  >>> print(vocab._terms[1].title)
  fr
