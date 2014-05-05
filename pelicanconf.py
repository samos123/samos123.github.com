#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals
import os

AUTHOR = 'Sam Stoelinga'
SITENAME = 'Sam Stoelinga (Samos IT) - Blog'
SITEURL = 'http://localhost:8000'
#DISQUS_SITENAME = 'samosit'
GITHUB_URL = 'http://github.com/samos123/'

OUTPUT_PATH = os.path.abspath(__file__)
PATH = "content"

ARTICLE_URL = 'posts/{slug}.html'
ARTICLE_SAVE_AS = 'posts/{slug}.html'

TIMEZONE = 'Europe/Paris'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

# Blogroll
LINKS = (('Pelican', 'http://getpelican.com/'),
         ('Python.org', 'http://python.org/'),
         ('Jinja2', 'http://jinja.pocoo.org/'),
         ('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (('You can add links in your config file', '#'),
          ('Another social link', '#'),)

DEFAULT_PAGINATION = 10


# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
