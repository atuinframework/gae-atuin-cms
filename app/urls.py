# -*- coding: utf-8 -*-
# WEBSITE
import js_translations.views
import home.admin

# ATUIN
import atuin.js_translations.views
import atuin.auth.views
import atuin.auth.admin

# ATUIN CMS
import atuincms.js_translations.views
import atuincms.auth.views
import atuincms.home.admin
import atuincms.media.admin
import atuincms.menus.admin
import atuincms.sections.admin
import atuincms.pages.admin
import atuincms.sitemap_robots.views
import atuincms.router.handler

mounts = [
    # WEBSITE
    ('/', js_translations.views),
    ('/', home.admin),

    # ATUIN
    ('/', atuin.js_translations.views),
    ('/', atuin.auth.views),
    ('/', atuin.auth.admin),

    # ATUIN CMS
    ('/', atuincms.js_translations.views),
    ('/', atuincms.auth.views),
    ('/', atuincms.home.admin),
    ('/', atuincms.media.admin),
    ('/', atuincms.menus.admin),
    ('/', atuincms.sections.admin),
    ('/', atuincms.pages.admin),
    ('/', atuincms.sitemap_robots.views),

    ('/', atuincms.router.handler),
]
