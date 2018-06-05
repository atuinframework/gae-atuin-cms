# -*- coding: utf-8 -*-
import os
from importlib import import_module
from atuin.utils import update_searchable_set
from atuincms.utils import pkg_to_cc
from google.appengine.ext import ndb


class Route(ndb.Model):
    page_key = ndb.KeyProperty('p')
    # All localized urls. Used for searches and to ensure uniqueness of the route and page.
    all_lurls = ndb.StringProperty('alu', repeated=True, indexed=True)
    template_id = ndb.StringProperty('t_id')
    # True when the page does not belong to any section
    root_page = ndb.BooleanProperty('rp', default=True)
    p_page_names = ndb.PickleProperty('pn', default={})
    # {
    # 	'en' : {
    # 		'name': 'How it works?',
    # 		'url': 'en/how-it-works'
    # 	},
    # 	'it' : {
    # 		'name': 'Come funziona?',
    # 		'url': 'it/come-funziona'
    # 	}
    # }
    searchable_page_names = ndb.StringProperty('spn', repeated=True, indexed=True)

    def __repr__(self):
        return '<Route %s>' % (self.key)

    @property
    def page_names(self):
        return self.p_page_names

    # ### Page name ###
    def get_page_name(self, lang):
        if self.page_names.get(lang):
            return self.page_names[lang]['name']
        return 'N/D'

    def set_page_name(self, name, lang):
        if lang not in self.page_names:
            self.page_names[lang] = {}
        self.page_names[lang]['name'] = name
        ns = set(self.searchable_page_names)
        ns = update_searchable_set(ns, name)
        self.searchable_page_names = list(ns)

    # ### Page url ###
    def get_page_url(self, lang):
        if self.page_names.get(lang):
            return self.page_names[lang]['url']
        return 'N/D'

    def set_page_url(self, url, lang):
        if lang not in self.page_names:
            self.page_names[lang] = {}
        self.page_names[lang]['url'] = url


class Template:
    def __init__(self, template_id):
        self.template_id = template_id
        self.page_class = None

        # check whether the template_id path exists
        dir_path = 'pages/' + self.template_id
        if not os.path.isdir(dir_path):
            raise ValueError('No page directory with the name ' + self.template_id)

        # import class
        models_path = 'pages.{}.models'.format(self.template_id)
        models_module = import_module(models_path)
        # build class name by template id
        class_name = '{}{}'.format(pkg_to_cc(self.template_id), 'Page')
        # save the class and set its template_id
        self.page_class = getattr(models_module, class_name)
        self.page_class.p_template_id = self.template_id

    @classmethod
    def available_templates(cls):
        path = 'pages'
        templates_ids = os.walk(path).next()[1]
        return [(tid, cls(tid)) for tid in templates_ids]

    @property
    def name(self):
        return self.page_class.tpl_name

    @property
    def preview_img_path(self):
        return self.page_class.tpl_preview_img_path

    def new_page(self):
        return self.page_class()

    def load_page(self, key):
        return key.get()

    @property
    def render_index(self):
        # import views
        views_path = 'pages.{}.views'.format(self.template_id)
        views_module = import_module(views_path)
        return getattr(views_module, 'index')

    @property
    def request_handler(self):
        # import views
        views_path = 'pages.{}.views'.format(self.template_id)
        views_module = import_module(views_path)
        return getattr(views_module, 'request_handler', None)

    @property
    def render_admin_index(self):
        # import admin
        admin_path = 'pages.{}.admin'.format(self.template_id)
        admin_module = import_module(admin_path)
        return getattr(admin_module, 'index')

    @property
    def admin_request_handler(self):
        # import admin
        admin_path = 'pages.{}.admin'.format(self.template_id)
        admin_module = import_module(admin_path)
        return getattr(admin_module, 'request_handler', None)
