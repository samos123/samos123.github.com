#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals
import os

AUTHOR = 'Sam Stoelinga'
SITENAME = 'Sam Stoelinga'
SITEURL = 'http://localhost:8001'
#DISQUS_SITENAME = 'samosit'

OUTPUT_PATH = os.path.abspath(__file__)
PATH = "content"

PLUGINS=[]

ARTICLE_URL = 'posts/{slug}.html'
ARTICLE_SAVE_AS = 'posts/{slug}.html'

THEME = "themes/pelican-hyde"

TIMEZONE = 'Europe/Paris'

DEFAULT_LANG = 'en'

# Blogroll
LINKS = (('Websu (Web Speed Analysis)', 'https://websu.io'),
         ('bgdestroyer.com (Remove background from image with AI)', 'https://www.bgdestroyer.com'),
         ('github.com/websu-io/websu', 'https://github.com/websu-io/websu'),)

## pelican-bootcamp3 settings
SOCIAL = (('linkedin', 'https://www.linkedin.com/in/samstoelinga/'),
          ('github', 'http://github.com/samos123/'),)
DISPLAY_TAGS_ON_SIDEBAR=False
DISPLAY_CATEGORIES_ON_MENU=False
DISPLAY_PAGES_ON_MENU=True

BIO="Open source contributor and Cloud Architect. Creator of websu.io and bgdestroyer.com"
PROFILE_IMAGE="sam-profile-pic.jpg"




DEFAULT_PAGINATION = 10
DEFAULT_DATE = "fs"


# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
PLUGINS = ['sitemap']

SITEMAP = {
    "format": "xml",
    "priorities": {
        "articles": 0.5,
        "indexes": 0.5,
        "pages": 0.5
    },
    "changefreqs": {
        "articles": "monthly",
        "indexes": "daily",
        "pages": "monthly"
    }
}
