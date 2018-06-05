# - coding: utf-8 -
from flask import abort, g
from google.appengine.ext import ndb
from google.appengine.ext import deferred

from languages import lang_title
from atuincms.router import load_page_by_key, weak_load_page_by_key

MAIN_MENU = 'MAIN_MENU'


class Menu(ndb.Model):
    p_parent_menu = ndb.KeyProperty('pm', kind='Menu')
    p_linked_page = ndb.KeyProperty('p')

    p_descriptions = ndb.PickleProperty('d', default={})
    # p_descriptions = {
    # 	'en' : {
    # 		'name': 'How it works?',
    # 		'url': 'section1/section2/how-it-works',
    # 		'description': 'How does the project work?'
    # 	},
    # 	'it' : {
    # 		'name': 'Come funziona?',
    # 		'url': 'sezione1/sezione2/come-funziona',
    # 		'description': 'Come funziona il progetto?'
    # 	}
    # }
    # WARNING: The url must be inherited by the linked page
    order = ndb.IntegerProperty('o', default=0)

    # TODO icon ?
    ins_timestamp = ndb.DateTimeProperty('i_ts', auto_now_add=True, indexed=False)
    upd_timestamp = ndb.DateTimeProperty('u_ts', auto_now=True, indexed=False)
    p_must_update_menu_tree = False

    def __repr__(self):
        return "<Menu %s>" % (self.key)

    def to_dict(self):
        d = super(Menu, self).to_dict(
            exclude=['p_parent_menu', 'p_linked_page', 'p_descriptions', 'p_must_update_menu_tree'])
        d['key_us'] = self.key.urlsafe()
        d['url'] = self.url
        d['languages'] = self.get_languages()
        d['descriptions'] = self.descriptions
        d['parent_menu'] = '/'
        d['linked_page'] = ''

        if self.parent_menu:
            d['parent_menu'] = self.parent_menu.urlsafe()

        if self.linked_page:
            page = weak_load_page_by_key(self.linked_page.urlsafe())
            if page:
                d['linked_page'] = self.linked_page.urlsafe()
                d['linked_page_name'] = page.name
                d['linked_page_url'] = page.url
        return d

    def get_id(self):
        return self.key.id()

    @classmethod
    def get_by_key(cls, k):
        return ndb.Key(urlsafe=k).get()

    @property
    def descriptions(self):
        return self.p_descriptions

    def get_languages(self):
        return self.descriptions.keys()

    def get_submenus(self):
        return self.query(self.__class__.p_parent_menu == self.key).fetch()

    #  Parent menu
    ########################
    @property
    def parent_menu(self):
        return self.p_parent_menu

    @parent_menu.setter
    def parent_menu(self, parent_menu_key):
        if self.p_parent_menu == parent_menu_key:
            # print 'menu - parent_menu.setter execution truncated, SAME parent_menu AS BEFORE'
            return
        self.p_parent_menu = parent_menu_key
        # print '----------- menu parent_menu p_must_update_menu_tree = True'
        self.p_must_update_menu_tree = True

    #  Linked page
    ########################
    @property
    def linked_page(self):
        return self.p_linked_page

    def set_linked_page(self, page):
        if page is None:
            self.p_linked_page = page
        else:
            self.p_linked_page = page.key
        self._update_lurls(page)

    # Name
    ########################
    def get_name(self, lang):
        if lang in self.descriptions:
            return self.descriptions[lang]['name']
        return 'N/D'

    @property
    def name(self):
        return self.get_name(g.language)

    def set_name(self, name, lang):
        if lang not in self.descriptions:
            self.descriptions[lang] = {
                'name': '',
                'url': '',
                'description': ''
            }

        # Verify that is not a silly parameter update
        if self.get_name(lang) == name:
            # print 'menu - set_name(%s, %s) execution truncated, SAME NAME AS BEFORE' % (name, lang)
            return
        self.descriptions[lang]['name'] = name
        # print '----------- menu set_name p_must_update_menu_tree = True'
        self.p_must_update_menu_tree = True

    # Description
    ########################
    def get_description(self, lang):
        if self.descriptions.get(lang):
            return self.descriptions[lang]['description']
        return 'N/D'

    def set_description(self, description, lang):
        # Set the description in descriptions dict
        if not self.descriptions.get(lang):
            self.descriptions[lang] = {}
        self.descriptions[lang]['description'] = description

    @property
    def description(self):
        return self.get_description(g.language)

    # Url
    ########################
    def get_url(self, lang):
        if lang not in self.descriptions:
            return self.descriptions.iteritems().next()[1]['url']
        if 'url' not in self.descriptions[lang]:
            return ''
        return self.descriptions[lang]['url']

    def set_url(self, url, lang):
        if not self.descriptions.get(lang):
            self.descriptions[lang] = {}
        self.descriptions[lang]['url'] = url
        self.p_must_update_menu_tree = True

    @property
    def url(self):
        return self.get_url(g.language)

    def _update_lurls(self, page):
        # print "\nMenu _update_lurls"
        # When should it be called?
        # - linked page change
        # - linked page's name change
        #
        # What does do:
        # - update the saved localized urls
        if page is None:
            for lang in self.get_languages():
                self.set_url('', lang)
        else:
            for lang in self.get_languages():
                self.set_url(page.get_url(lang), lang)

    def refresh_derived_parameters(self, page):
        """
        To be called each time linked page undergoes an update.
        """
        self.set_linked_page(page)

    def _post_put_hook(self, future):
        if self.p_must_update_menu_tree:
            deferred.defer(_menu_generate_tree, _countdown=3)


class MenuTree(ndb.Model):
    tree = ndb.PickleProperty('t')

    ins_timestamp = ndb.DateTimeProperty('i_ts', auto_now_add=True, indexed=False)
    upd_timestamp = ndb.DateTimeProperty('u_ts', auto_now=True, indexed=False)

    def __repr__(self):
        return "<MenuTree %s>" % self.key

    def get_id(self):
        return self.key.id()

    @classmethod
    def get_by_key(cls, k):
        return ndb.Key(urlsafe=k).get()


def generate_full_menu_tree(menu=None):
    if menu:
        submenus = menu.get_submenus()
    else:
        # root menus
        submenus = Menu.query(Menu.p_parent_menu == None).fetch()

    tree_d = {x: [] for x in lang_title}

    for subm in submenus:
        subs = generate_full_menu_tree(subm)
        for lang in subm.get_languages():
            tree_d[lang].append({
                'key_us': subm.key.urlsafe(),
                'order': subm.order,
                # 'menu_icon': subm.icon,
                'name': subm.get_name(lang),
                'url': subm.get_url(lang),
                'description': subm.get_description(lang),
                'subs': subs[lang]
            })

    for menus in tree_d.itervalues():
        menus.sort(key=lambda v: (v['order'], v['name']))

    return tree_d


def _menu_generate_tree(lang=None):
    trees = generate_full_menu_tree()
    # print 'generated trees'
    # print trees

    for lang_t, tree in trees.iteritems():
        if (lang is None) or (lang_t == lang):
            k = ndb.Key('MenuTree', lang_t)
            m = MenuTree(key=k)
            m.tree = tree
            m.put()


def get_menus_by_parent(parent_key_us=None):
    if parent_key_us:
        parent_menu = ndb.Key(urlsafe=parent_key_us).get() or abort(404)
        menus = Menu.query(Menu.p_parent_menu == parent_menu.key).order(Menu.order).fetch()
    else:
        menus = Menu.query(Menu.p_parent_menu == None).order(Menu.order).fetch()

    menus_list = [m for m in menus]

    return menus_list


def get_menu(menu_name):
    tree_entity = ndb.Key(MenuTree, g.language).get()
    if tree_entity is None:
        tree = []
    else:
        tree = tree_entity.tree

    found_menu = _search_menu_by_name(tree, menu_name)
    return found_menu


def _search_menu_by_name(menus, menu_name):
    for m in menus:
        if m['name'] == menu_name:
            return m

        found_nested = _search_menu_by_name(m['subs'], menu_name)
        if found_nested:
            return found_nested

    return {}
