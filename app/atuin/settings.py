# -*- coding: utf-8 -*-
"""
Settings file
Why this file works like this?
When updating the application, it should ensure the application will run without updating config.py
each new features should have a default here
"""
import sys

# basic configuration - these MUST BE present
try:
	import config
except ImportError:
	err_msg = [	"*" * 80,
				"\nATUIN ERROR\n\nConfiguration files are missing. Please copy config.py out of atuin/ directory.",
				"\nMore info in the README file and documentation",
				"\n",
				"*" * 80
	]
	print "\n".join(err_msg)
	sys.exit(255)


DEBUG = config.DEBUG
SECRET_KEY = config.SECRET_KEY
SITE_TITLE = config.SITE_TITLE

try:
	MULTILANGUAGE = config.MULTILANGUAGE
	MULTILANGUAGE_LANGS = config.MULTILANGUAGE_LANGS
except AttributeError:
	MULTILANGUAGE = False
	MULTILANGUAGE_LANGS = ['en']

try:
	CACHE_CONFIG = config.CACHE_CONFIG
except AttributeError:
	CACHE_CONFIG = {'CACHE_TYPE': 'simple'}

try:
	CACHE_DEFAULT_TIME = config.CACHE_DEFAULT_TIME
except AttributeError:
	CACHE_DEFAULT_TIME = 60

try:
	FORCE_HTTPS = config.FORCE_HTTPS
except AttributeError:
	FORCE_HTTPS = False

# apps mounts MUST BE present
from urls import mounts
