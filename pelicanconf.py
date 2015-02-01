#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals
import os

AUTHOR = 'Sam Stoelinga'
SITENAME = 'Sam Stoelinga (Samos IT) - Blog'
SITEURL = 'http://localhost:8000'
#DISQUS_SITENAME = 'samosit'

OUTPUT_PATH = os.path.abspath(__file__)
PATH = "content"

ARTICLE_URL = 'posts/{slug}.html'
ARTICLE_SAVE_AS = 'posts/{slug}.html'

THEME = "themes/pelican-bootstrap3"

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

## pelican-bootcamp3 settings
GITHUB_URL = 'http://github.com/samos123/'
GITHUB_USER = "samos123"
SOCIAL = (('linkedin', 'http://www.linkedin.com/in/sam.stoelinga'),
          ('github', 'http://github.com/samos123/'),)
DISPLAY_TAGS_ON_SIDEBAR=False





DEFAULT_PAGINATION = 10


# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
