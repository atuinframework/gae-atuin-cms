# -*- coding: utf-8 -*-
# Configuration template file. Copy it to config.py

# True to print all queries and autoreload
DEBUG = True

# change for each installation
SECRET_KEY = 'somerandom-;:=()=yty'

# site title
SITE_TITLE = "GAE-ATUIN"

# multi language support
MULTILANGUAGE = False
# Languages supported by the website
# The first language is used for both multi language websites and
# single language websites as the default routing language.
MULTILANGUAGE_LANGS = ['en'] # , 'it', 'es']

# considered only in production (DEBUG False)
CACHE_CONFIG = {'CACHE_TYPE': 'gaememcached'}

# HTTPS
FORCE_HTTPS = True
