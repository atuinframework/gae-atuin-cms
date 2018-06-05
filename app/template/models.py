# -*- coding: utf-8 -*-
from collections import OrderedDict
from atuincms.pages.models import ndb, blobstore, Page
from google.appengine.api import images as gapi_images

from flask_babel import _


class MyCustomBasePage(Page):
    tpl_name = _('My Custom Base Page')

    def __repr__(self):
        return "<MyCustomBasePage %s>" % (self.key)

    def __init__(self):
        super(MyCustomBasePage, self).__init__()

        # initialize page elements
        self.mcb_menus()
        self.mcb_texts()
        self.mcb_images()
        self.mcb_media_collections()

    def mcb_menus(self):
        self.inject_menu('main_menu', _('Main menu'))

    def mcb_texts(self):
        pass

    def mcb_images(self):
        pass

    def mcb_media_collections(self):
        pass
