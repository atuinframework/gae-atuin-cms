# -*- coding: utf-8 -*-
from collections import OrderedDict
from template.models import MyCustomBasePage

from flask_babel import _


class HomePage(MyCustomBasePage):
    tpl_name = _('Home page')
    tpl_preview_img_path = '/static/min/img/pages/home/admin/home-tpl-preview.png'

    def __repr__(self):
        return "<HomePage %s>" % (self.key)

    def __init__(self):
        super(HomePage, self).__init__()
        # initialize page elements
        self.home_texts()
        self.home_images()
        self.home_linked_pages()
        self.home_media_collections()

    def home_texts(self):
        # features
        self.text_init(
            text_id='main_description',
            default_text='# GAE Atuin CMS\n\nGAE Atuin CMS is a Content Management System to build cloud-based websites ' +
                         'that rely on top of the [GAE Atuin Web Framework](https://github.com/atuinframework/gae-atuin).' +
                         'This CMS is designed to be deployed on [Google App Engine](https://cloud.google.com/appengine/) ' +
                         'and to use the [Google Datastore](https://cloud.google.com/datastore/).\n\n'+
                         'GAE Atuin CMS dynamically creates RESTful URLs thanks to a powerful routing engine system.\n\n' +
                         'Finally, its template engine system gives you the freedom to define your own templates to be applied to each page.'
        )

    def home_images(self):
        # main_slider
        self.image_init(
            image_id='main_pic',
            default_url='/static/min/img/pages/home/atuin_logo.jpg'
            # default_url='https://via.placeholder.com/200x150/ffff66/000?text=200x150%20-%20image%20{}'
        )

    def home_linked_pages(self):
        pass

    def home_media_collections(self):
        pass
