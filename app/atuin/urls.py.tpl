# -*- coding: utf-8 -*-
# public site imports
import home.views

import js_translations.views

# admin site imports
import auth.views, auth.admin
import admin.admin

mounts = [
	('/', home.views),

	# ATUIN
	('/', atuin.auth.views),
	('/admin/auth', atuin.auth.admin),
	('/', atuin.js_translations.views),
]
