# -*- coding: utf-8 -*-
import copy
import datetime
from pprint import pprint

from atuincms.media import sanitize_input_text
from atuincms.router import Template
from atuincms.sections.models import get_section_pages
from flask import g, request, abort
from flask_babel import _
import markdown
from google.appengine.ext import ndb, blobstore
from google.appengine.api import images as gapi_images

from atuin.utils import slugify
import atuincms.router
from atuincms.menus.models import Menu, get_menu
from atuincms.sections.models import Section
from collections import OrderedDict

from atuincms.utils import pkg_to_cc

import views, admin


class Page(ndb.Model):
    tpl_name = _('Page template sample')
    tpl_preview_img_path = 'https://via.placeholder.com/1200x3500?text=Template+preview'

    p_template_id = ndb.StringProperty('t', indexed=False)
    p_parent_section = ndb.KeyProperty('s', kind='Section')

    ins_timestamp = ndb.DateTimeProperty('i_ts', auto_now_add=True, indexed=False, default=datetime.datetime.now())
    upd_timestamp = ndb.DateTimeProperty('u_ts', auto_now=True, indexed=False, default=datetime.datetime.now())

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

    # TEXTS
    ###########
    # p_page_texts: actual texts contents saved
    p_page_texts = ndb.PickleProperty('txts', default={})
    # p_page_texts = {
    # 	'text_id_A': {
    #       'en': 'Text',
    #       'it': 'Testo'
    #   },
    #   'text_id_B': {
    #       'en': 'Text',
    #       'it': 'Testo'
    #   },
    #   [...]
    # }

    # IMAGES
    ###########
    # p_page_images: images entities saved
    p_page_images = ndb.PickleProperty('imgs', default={})
    # p_page_images = {
    # 	'image_id_A': (<blob_key>, <img_serving_url>),
    # 	'image_id_B': (<blob_key>, <img_serving_url>),
    #   [...]
    # }

    # LINKED PAGES
    ###########
    # p_page_linked_pages: linked pages to the page
    p_page_linked_pages = ndb.PickleProperty('lnk_pgs', default={})
    # p_page_linked_pages = {
    # 	'linked_page_id_A': '<page_key_us>',
    # 	'linked_page_id_B': '<page_key_us>',
    #   [...]
    # }

    # LINKED SECTIONS
    ###########
    # p_page_linked_sections: linked sections to the page
    p_page_linked_sections = ndb.PickleProperty('lnk_sct', default={})

    # p_page_linked_sections = {
    # 	'linked_section_id': '<section_key_us>',
    #   [...]
    # }

    def __repr__(self):
        return "<Page %s>" % (self.key)

    def __init__(self):
        super(Page, self).__init__()

        # WARNING: The url must be generated by the section the page belongs to
        # On the _post_put_hook, is it necessary to update the page route?
        self.p_lurls_changed = False

        # p_menus_to_inject: menus that will be injected in the template
        self.p_menus_to_inject = {}
        # p_menus_to_inject = {
        # 	'menu_variable_name': 'Name of the template to search for',
        #   [...]
        # }

        # p_texts: texts defined for the page
        self.p_texts = {}
        # p_texts = {
        # 	'textA': 'Default already translated text',
        #   'textB': 'Default already translated text',
        #   [...]
        # }

        # p_images: images defined for the page
        self.p_images = {}
        # p_images = {
        # 	'image_id_A': '<img_serving_url>',
        # 	'image_id_B': '<img_serving_url>',
        #   [...]
        # }

        # p_linked_pages: linked pages defined for the page
        self.p_linked_pages = {}
        # p_images = {
        # 	'linked_page_id_A': 'Page name hint',
        # 	'linked_page_id_B': 'Page name hint',
        #   [...]
        # }

        # p_linked_sections: section for which inject pages lists in the page template
        self.p_linked_sections = {}
        # p_linked_sections = {
        # 	'section_id_A': 'Section name hint',
        #   [...]
        # }
        self.p_media_collections = {}

    def to_dict(self):
        exclude = [
            'p_template_id',
            'p_parent_section',
            'p_descriptions',
            'p_lurls_changed',
            'p_page_texts',
            'p_texts',
            'p_page_images',
            'p_images',
            'p_page_linked_pages',
            'p_linked_pages'
        ]
        d = super(Page, self).to_dict(exclude=exclude)
        d['key_us'] = self.key.urlsafe()
        d['url'] = self.url
        d['languages'] = self.get_languages()
        d['descriptions'] = self.descriptions
        if self.parent_section:
            d['parent_section'] = self.parent_section.urlsafe()
        else:
            d['parent_section'] = ''
        return d

    '''
        PAGE MANAGEMENT
    '''

    @property
    def descriptions(self):
        return self.p_descriptions

    def get_languages(self):
        return self.descriptions.keys()

    # Parent section
    ###########
    @property
    def parent_section(self):
        return self.p_parent_section

    @parent_section.setter
    def parent_section(self, parent_sect_key):
        # 0. Verify not a silly parameter update
        if self.parent_section == parent_sect_key:
            # print 'page - parent_section.setter execution truncated, SAME parent_section AS BEFORE'
            # print parent_sect_key
            return

        # 1. Remove page from previous_parent_section
        if self.parent_section is not None:
            prev_sect = self.parent_section.get()
            # Remove page from pages list in section
            if prev_sect:
                prev_sect.remove_page(self.key.urlsafe())
                prev_sect.put()

        self.p_parent_section = parent_sect_key

        # 2. Insert page in the new parent_section
        p_section = None
        if self.parent_section is not None:
            p_section = self.parent_section.get()
            p_section.add_page(page=self)
            p_section.put()

        # 3. Update the urls
        self._update_lurls(p_section)

        # 4. It will be necessary to update the page route
        # print 'MUST UPDATE ROUTE TO TRUE'
        self.p_lurls_changed = True

    # Name
    ###########
    def get_name(self, lang):
        if self.descriptions.get(lang):
            return self.descriptions[lang]['name']
        return 'N/D'

    @property
    def name(self):
        return self.get_name(g.language)

    def set_name(self, name, lang):
        # print 'SETTING NAME'
        if not self.descriptions.get(lang):
            self.descriptions[lang] = {}

        # 0. Verify not a silly parameter update
        if self.descriptions[lang].get('name'):
            if self.descriptions[lang]['name'] == name:
                # print 'page - set_name(%s, %s) execution truncated, SAME NAME AS BEFORE!!!' % (name, lang)
                return

        self.descriptions[lang]['name'] = name

        # 1. Update page name in parent_section
        p_section = None
        if self.parent_section is not None:
            p_section = self.parent_section.get()
            p_section.add_page(page=self)
            p_section.put()

        # 2. Update urls
        self._update_lurls(p_section)

        # 3. It will be necessary to update the page route
        # print 'MUST UPDATE ROUTE TO TRUE'
        self.p_lurls_changed = True

    def get_all_lnames(self):
        """
        Return a dict of all localized names.
        """
        names = {}
        for l, desc in self.descriptions.iteritems():
            names[l] = desc['name']
        return names

    # Description
    ###########
    def get_description(self, lang):
        if self.descriptions.get(lang):
            return self.descriptions[lang]['description']
        return 'N/D'

    def set_description(self, description, lang):
        if not self.descriptions.get(lang):
            self.descriptions[lang] = {}
        self.descriptions[lang]['description'] = description

    @property
    def description(self):
        return self.get_description(g.language)

    # Url
    ###########
    def get_url(self, lang):
        if self.descriptions.get(lang):
            return self.descriptions[lang]['url']
        return self.descriptions.iteritems().next()[1]['url']

    def set_url(self, url, lang):
        if not self.descriptions.get(lang):
            self.descriptions[lang] = {}

        l_home_page = '/' + lang + '/' + 'home-page'
        if url == l_home_page:
            url = '/'
        self.descriptions[lang]['url'] = url

    @property
    def url(self):
        return self.get_url(g.language)

    def _disambiguate_page_name(self):
        """
        Add a dash at the end of the page name (all languages) in order to make its url unique.
        """
        for lang, d in self.descriptions.iteritems():
            d['name'] += '-'

    def _generate_lurls(self, parent_section):
        if parent_section is not None:
            for lang, desc in parent_section.descriptions.iteritems():
                sec_path = desc['path']
                page_path = slugify(self.get_name(lang))
                self.set_url(sec_path + '/' + page_path, lang)
        else:
            for lang in self.get_languages():
                self.set_url('/' + lang + '/' + slugify(self.get_name(lang)), lang)

    # print '_generete_urls'
    # print self.descriptions

    def _update_lurls(self, parent_section=None):
        # print "\n_update_lurls"
        # When should it be called?
        # - page name change
        # - parent section change
        #
        # What does do:
        # - generate urls
        # - verify page is unique (if it is not, change the page name and generate urls again)
        exists = True
        while exists:
            self._generate_lurls(parent_section)
            # print "_generate_urls"
            # print self.descriptions
            # pick the first url, doesn't matter the language in which it is
            u = self.descriptions.itervalues().next()
            u = u['url']
            # print 'picked url:'
            # print u
            # print '\nexists before'
            # print exists
            exists = atuincms.router.route_exists(u)
            # print 'exists after'
            # print exists
            if exists:
                # print 'Already existing page!!'
                self._disambiguate_page_name()

    def get_all_lurls(self):
        """
        Return a list of all localized urls.
        """
        urls = {}
        for l, desc in self.descriptions.iteritems():
            urls[l] = desc['url']
        return urls

    def refresh_derived_parameters(self, parent_section):
        """
        To be called each time the parent section undergoes an update related to its: name, parent_section.
        """
        # Update the lurls
        self._update_lurls(parent_section)
        # It will be necessary to update the page route
        # print 'MUST UPDATE ROUTE TO TRUE'
        self.p_lurls_changed = True

    def _post_put_hook(self, future):
        # print "\nPAGE _post_put_hook"
        # if localized urls are changed:
        # - update the route for the page
        # - update all the menus that refer to the page
        print 'PAGE OBJ _post_put_hook '
        if self.p_lurls_changed:
            print 'PAGE OBJ _post_put_hook p_lurls_changed'
            key = future.get_result()
            page = key.get()

            print 'PAGE OBJ _post_put_hook atuincms.router.update_page_route'
            # Route update
            atuincms.router.update_page_route(page)

            # print 'Going to update menu'

            # Menus update
            menus = Menu.query(Menu.p_linked_page == page.key).fetch()
            for m in menus:
                m.refresh_derived_parameters(page)
                m.put()

    # print 'ROUTE UPDATED AND ALSO MENU!'
    # print 'key:'
    # print key
    # print page

    @classmethod
    def _pre_delete_hook(cls, key):
        # To do:
        # - delete corresponding route
        # - discard page information from parent section
        # - remove page from menus that have it as linked page
        # - remove page from sections that contain it
        # - delete images saved in it

        # print 'page - PRE DELETE HOOK'

        page = key.get()

        # delete the associated route
        atuincms.router.remove_page_route(key)

        # set parent section to None in order to discard page information in other sections
        page.parent_section = None

        # remove page from menus that have it as linked page
        menus = Menu.query(Menu.p_linked_page == key).fetch()
        for m in menus:
            m.set_linked_page(None)
            m.put()

        page._delete_all_images()

    '''
        MENUS
    '''

    def inject_menu(self, menu_var_name, menu_name):
        self.p_menus_to_inject[menu_var_name] = menu_name

    def _get_menus_dict(self):
        menus = {}
        for menu_var_name, menu_name in self.p_menus_to_inject.iteritems():
            menus[menu_var_name] = get_menu(menu_name)
        return menus

    '''
        TEXTS
    '''

    def text_init(self, text_id, default_text):
        """
        Initialize a new text_id and a default_text content (already localized) for the page.
        :param text_id: text id
        :param default_text: text content
        :return:
        """
        self.p_texts[text_id] = default_text

    def text_list_init(self, text_list_id, default_text, lst_range):
        """
        Initialize multiple text_id and default_text content (already localized) by the given range.
        :param text_list_id:
        :param default_text:
        :param lst_range:
        :return:
        """
        for idx in lst_range:
            text_id = '{}_{}'.format(text_list_id, idx)
            def_text = default_text.format(idx + 1)
            self.p_texts[text_id] = def_text

    def text_exists(self, text_id, idx=None, l=None):
        """
        Return whether a content for the text_id and language is present or not.
        :param text_id:
        :param l:
        :return bool:
        """
        if l is None:
            l = g.language

        if idx is not None:
            text_id = '{}_{}'.format(text_id, idx)

        if text_id not in self.p_page_texts:
            return False
        return l in self.p_page_texts[text_id]

    def text(self, text_id, idx=None, l=None):
        """
        Returns the text localized text else it returns the initialized text.
        :param text_id: text id
        :param idx:
        :param l: language
        :return:
        """
        if l is None:
            l = g.language

        if idx is not None:
            text_id = '{}_{}'.format(text_id, idx)

        if self.text_exists(text_id, idx=None, l=l):
            return self.p_page_texts[text_id][l]

        return self.p_texts[text_id]

    def text_html(self, text_id, idx=None, l=None):
        """
        Return the html version of the text. Sanitized.
        :param text_id:
        :param idx:
        :param l:
        :return:
        """
        if l is None:
            l = g.language

        if idx is not None:
            text_id = '{}_{}'.format(text_id, idx)

        if self.text_exists(text_id, l=l):
            txt = self.text(text_id, l=l)
        else:
            txt = self.p_texts[text_id]
        return markdown.markdown(txt)

    def text_save(self, text_id, txt, l=None):
        """
        Save a localized text by its id.
        :param text_id: text id
        :param txt: text content
        :param l:
        :return:
        """
        if l is None:
            l = g.language

        if text_id not in self.p_page_texts:
            self.p_page_texts[text_id] = {}

        # sanitize the user input
        txt = sanitize_input_text(txt)
        self.p_page_texts[text_id][l] = txt

    def text_delete(self, text_id):
        """
        Delete a localized text by its id.
        :param text_id: text id
        :return:
        """
        if text_id in self.p_page_texts:
            del (self.p_page_texts[text_id])

    '''
        IMAGES
    '''

    def image_init(self, image_id, default_url):
        """
        Initialize a new image_id and a default_url's image for the page.
        :param image_id:
        :param default_url:
        :return:
        """
        self.p_images[image_id] = default_url

    def image_list_init(self, image_list_id, default_url, lst_range):
        """
        Initialize multiple image_id and default_urls by the given range.
        :param image_list_id:
        :param default_url:
        :param lst_range:
        :return:
        """
        for idx in lst_range:
            image_id = '{}_{}'.format(image_list_id, idx)
            def_url = default_url.format(idx + 1)
            self.p_images[image_id] = def_url

    def image_exists(self, image_id, idx=None):
        """
        Return whether there exist an image saved for the image_id.
        :param idx:
        :param image_id:
        :return bool:
        """
        if idx is not None:
            image_id = '{}_{}'.format(image_id, idx)

        return image_id in self.p_page_images

    def image_url(self, image_id, idx=None, append='=s0'):
        """
        Return image url by image id.
        :param append:
        :param image_id:
        :param idx:
        :return:
        """
        if idx is not None:
            image_id = '{}_{}'.format(image_id, idx)

        if image_id in self.p_page_images:
            return self.p_page_images[image_id][1] + append

        return self.p_images[image_id]

    def image_save(self, image_id, blob):
        """
        Save an image to the page.
        :param image_id:
        :param blob:
        :return:
        """
        # delete previous image
        self.image_delete(image_id)

        blob_key = blob.key()
        url = gapi_images.get_serving_url(blob_key, secure_url=True)
        self.p_page_images[image_id] = (blob_key, url)

    def image_delete(self, image_id):
        """
        Delete an image from the page.
        :param image_id:
        :return:
        """
        if image_id in self.p_page_images:
            (blob_key, url) = self.p_page_images[image_id]
            blob = blobstore.get(blob_key)
            if blob:
                blob.delete()
            del (self.p_page_images[image_id])

    def _delete_all_images(self):
        """
        Delete all images of the page
        :return:
        """
        images = self.p_page_images.copy()
        for image_id in images.iterkeys():
            self.image_delete(image_id)

    '''
        LINKED PAGES
    '''

    def linked_page_init(self, linked_page_id, page_name_hint):
        """
        Initialize a new linked_page for the page.
        :param linked_page_id:
        :param page_name_hint:
        :return:
        """
        self.p_linked_pages[linked_page_id] = page_name_hint

    def linked_page_list_init(self, linked_page_list_id, page_name_hint, lst_range):
        # does it have any sense?
        pass

    def linked_page_exists(self, linked_page_id):
        # print 'LINKED PAGE EXISTS'
        """
        Return whether there exist the linked page.
        :param linked_page_id:
        :return bool:
        """
        if linked_page_id not in self.p_page_linked_pages:
            return False

        page_key_us = self.p_page_linked_pages[linked_page_id]
        page = atuincms.router.weak_load_page_by_key(page_key_us)
        if not page:
            return False

        return True

    def linked_page_key_us(self, linked_page_id):
        """
        Returns the linked page key_us.
        :param linked_page_id:
        :return:
        """
        if linked_page_id not in self.p_page_linked_pages:
            return None

        page_key_us = self.p_page_linked_pages[linked_page_id]
        return page_key_us

    def linked_page_url(self, linked_page_id, l=None):
        """
        Returns the localized linked page url else it returns the home.
        :param linked_page_id:
        :param l:
        :return:
        """
        if l is None:
            l = g.language

        if linked_page_id not in self.p_page_linked_pages:
            return '/'

        page_key_us = self.p_page_linked_pages[linked_page_id]
        page = atuincms.router.weak_load_page_by_key(page_key_us)
        if page is None:
            return '/'

        return page.get_url(l)

    def linked_page_name(self, linked_page_id, l=None):
        """
        Returns the localized linked page name else it returns the linked page hint.
        :param linked_page_id:
        :param l:
        :return:
        """
        if l is None:
            l = g.language

        if linked_page_id not in self.p_page_linked_pages:
            return self.p_linked_pages[linked_page_id]

        page_key_us = self.p_page_linked_pages[linked_page_id]
        page = atuincms.router.weak_load_page_by_key(page_key_us)
        if page is None:
            return self.p_linked_pages[linked_page_id]

        return page.get_name(l)

    def linked_page_save(self, linked_page_id, linked_page_key_us):
        """
        Save linked page by its key us.
        :param linked_page_id:
        :param linked_page_key_us:
        :return:
        """
        self.p_page_linked_pages[linked_page_id] = linked_page_key_us

    def linked_page_delete(self, linked_page_id):
        """
        Delete linked page by its key us.
        :param linked_page_id:
        :return:
        """
        if linked_page_id in self.p_page_linked_pages:
            del (self.p_page_linked_pages[linked_page_id])

    '''
        SECTIONS PAGES
    '''

    def linked_section_init(self, linked_section_id, section_name_hint):
        """
        Initialize a new linked section for the page.
        :param linked_section_id:
        :param section_name_hint:
        :return:
        """
        self.p_linked_sections[linked_section_id] = section_name_hint

    def linked_section_list_init(self, linked_section_list_id, section_name_hint, lst_range):
        # does it have any sense?
        pass

    def linked_section_exists(self, linked_section_id):
        """
        Return whether there exist the linked section.
        :param linked_section_id:
        :return bool:
        """
        if linked_section_id not in self.p_page_linked_sections:
            return False

        section_key_us = self.p_page_linked_sections[linked_section_id]
        section = ndb.Key(urlsafe=section_key_us).get()
        if not section:
            return False

        return True

    def linked_section_key_us(self, linked_section_id):
        """
        Returns the linked section key_us.
        :param linked_section_id:
        :return:
        """
        if linked_section_id not in self.p_page_linked_sections:
            return None

        section_key_us = self.p_page_linked_sections[linked_section_id]
        return section_key_us

    def linked_section_path(self, linked_section_id, l=None):
        """
        Returns the localized path of the section else it returns /.
        :param linked_section_id:
        :param l:
        :return:
        """
        if l is None:
            l = g.language

        if linked_section_id not in self.p_page_linked_sections:
            return '/'

        section_key_us = self.p_page_linked_sections[linked_section_id]
        section = ndb.Key(urlsafe=section_key_us).get()
        if not section:
            return '/'

        return section.get_path(l)

    def linked_section_name(self, linked_section_id, l=None):
        """
        Returns the localized linked section name else it returns the linked section hint.
        :param linked_section_id:
        :param l:
        :return:
        """
        if l is None:
            l = g.language

        if linked_section_id not in self.p_page_linked_sections:
            return self.p_linked_sections[linked_section_id]

        section_key_us = self.p_page_linked_sections[linked_section_id]
        section = ndb.Key(urlsafe=section_key_us).get()
        if section is None:
            return self.p_linked_sections[linked_section_id]

        return section.get_name(l)

    def linked_section_save(self, linked_section_id, linked_section_key_us):
        """
        Save linked section by its key us.
        :param linked_section_id:
        :param linked_section_key_us:
        :return:
        """
        self.p_page_linked_sections[linked_section_id] = linked_section_key_us

    def linked_section_delete(self, linked_section_id):
        """
        Delete linked page by its key us.
        :param linked_section_id:
        :return:
        """
        if linked_section_id in self.p_page_linked_sections:
            del (self.p_page_linked_sections[linked_section_id])

    def linked_section_pages(self, linked_section_id, only_template_id, **kwargs):
        if linked_section_id not in self.p_page_linked_sections:
            return []
        section_key_us = self.p_page_linked_sections[linked_section_id]
        return get_section_pages(
            section_key_us=section_key_us,
            only_template_id=only_template_id,
            **kwargs
        )

    '''
        MEDIA COLLECTIONS
    '''

    def media_collection_init(self, collection_id, texts=None, images=None, linked_pages=None, h_idx=''):
        """
        Initialize a new media collection.
        'media_coll_id': {
            'texts': OrderedDict([
                ('name', {
                    'panel_title': 'Nome cognome {}',
                    'default_text': 'Default name {}',
                }),
                ('desc', {
                    'panel_title': 'Descrizione {}',
                    'text': 'Default descripition {}',
                })
            ]),
            'images': OrderedDict([
                ('img_1', {
                    'panel_title': 'Image  {}',
                    'default_url': '<Default url {}>',
                })
            ]),
            'linked_pages': OrderedDict([
                ('linked_A', {
                    'panel_title': 'Linked page {}',
                    'page_name_hint': 'Hint to pick the page {}>',
                })
            ])
        ]),
        :param collection_id:
        :param texts: OrderedDict
        :param images: OrderedDict
        :param linked_pages: OrderedDict
        :param h_idx: humanized id
        :return:
        """
        # Initialize texts
        if texts is None:
            texts = {}
        for txt_id, txt in texts.iteritems():
            txt['panel_title'] = txt['panel_title'].format(h_idx)
            txt['default_text'] = txt['default_text'].format(h_idx)

            text_id = '{}_{}'.format(collection_id, txt_id)
            self.text_init(text_id, txt['default_text'])

        # Initialize images
        if images is None:
            images = {}
        for img_id, img in images.iteritems():
            img['panel_title'] = img['panel_title'].format(h_idx)
            img['default_url'] = img['default_url'].format(h_idx)

            image_id = '{}_{}'.format(collection_id, img_id)
            self.image_init(image_id, img['default_url'])

        # Initialize linked pages
        if linked_pages is None:
            linked_pages = {}
        for lnk_pg_id, lnk_pg in linked_pages.iteritems():
            lnk_pg['panel_title'] = lnk_pg['panel_title'].format(h_idx)
            lnk_pg['page_name_hint'] = lnk_pg['page_name_hint'].format(h_idx)

            lnk_pg_id = '{}_{}'.format(collection_id, lnk_pg_id)
            self.linked_page_init(lnk_pg_id, lnk_pg['page_name_hint'])

        collection = {
            'texts': texts,
            'images': images,
            'linked_pages': linked_pages
        }

        self.p_media_collections[collection_id] = collection

    # print 'pprint(self.p_texts)'
    # pprint(self.p_texts)
    # print '\n\n\n'
    # print 'pprint(self.p_images)'
    # pprint(self.p_images)
    # print '\n\n\n'
    # print 'pprint(self.p_linked_pages)'
    # pprint(self.p_linked_pages)
    # print '\n\n\n'
    # print 'pprint(self.p_media_collections)'
    # pprint(self.p_media_collections)

    def media_collection_list_init(self, collection_list_id, lst_range, texts=None, images=None, linked_pages=None):
        """
        :param collection_list_id:
        :param lst_range:
        :param texts:
        :param images:
        :param linked_pages:
        :return:
        """
        for idx in lst_range:
            collection_id = '{}_{}'.format(collection_list_id, idx)
            # deep copy of structures due to same pointer passing problem
            txts = copy.deepcopy(texts)
            imgs = copy.deepcopy(images)
            lnkpgs = copy.deepcopy(linked_pages)
            h_idx = str(idx + 1)
            self.media_collection_init(
                collection_id=collection_id,
                texts=txts,
                images=imgs,
                linked_pages=lnkpgs,
                h_idx=h_idx
            )

    # print 'pprint(self.p_texts)'
    # pprint(self.p_texts)
    # print '\n\n\n'
    # print 'pprint(self.p_images)'
    # pprint(self.p_images)
    # print '\n\n\n'
    # print 'pprint(self.p_media_collections)'
    # pprint(self.p_media_collections)

    # media collection lists
    def collection_texts(self, collection_id):
        if collection_id in self.p_media_collections:
            return self.p_media_collections[collection_id]['texts']

    def collection_images(self, collection_id):
        if collection_id in self.p_media_collections:
            return self.p_media_collections[collection_id]['images']

    def collection_linked_pages(self, collection_id):
        if collection_id in self.p_media_collections:
            return self.p_media_collections[collection_id]['linked_pages']

    # media collection text functions
    def collection_text_exists(self, collection_id, text_id, idx=None):
        if idx is None:
            text_id = '{}_{}'.format(collection_id, text_id)
        else:
            text_id = '{}_{}_{}'.format(collection_id, str(idx), text_id)
        return self.text_exists(text_id)

    def collection_text(self, collection_id, text_id, idx=None):
        if idx is None:
            text_id = '{}_{}'.format(collection_id, text_id)
        else:
            text_id = '{}_{}_{}'.format(collection_id, str(idx), text_id)
        return self.text(text_id)

    def collection_text_html(self, collection_id, text_id, idx=None):
        if idx is None:
            text_id = '{}_{}'.format(collection_id, text_id)
        else:
            text_id = '{}_{}_{}'.format(collection_id, str(idx), text_id)
        return self.text_html(text_id)

    # media collection image functions
    def collection_image_exists(self, collection_id, image_id, idx=None):
        if idx is None:
            image_id = '{}_{}'.format(collection_id, image_id)
        else:
            image_id = '{}_{}_{}'.format(collection_id, str(idx), image_id)
        return self.image_exists(image_id)

    def collection_image_url(self, collection_id, image_id, idx=None, append='=s0'):
        if idx is None:
            image_id = '{}_{}'.format(collection_id, image_id)
        else:
            image_id = '{}_{}_{}'.format(collection_id, str(idx), image_id)
        return self.image_url(image_id, append=append)

    # media collection linked_page functions
    def collection_linked_page_exists(self, collection_id, linked_page_id, idx=None):
        if idx is None:
            image_id = '{}_{}'.format(collection_id, linked_page_id)
        else:
            image_id = '{}_{}_{}'.format(collection_id, str(idx), linked_page_id)
        return self.linked_page_exists(image_id)

    def collection_linked_page_url(self, collection_id, linked_page_id, idx=None):
        if idx is None:
            image_id = '{}_{}'.format(collection_id, linked_page_id)
        else:
            image_id = '{}_{}_{}'.format(collection_id, str(idx), linked_page_id)
        return self.linked_page_url(image_id)

    '''
        REQUESTS HANDLERS AND PAGE RENDER FUNCTIONS
    '''

    def handle_admin_request(self, **kwargs):
        """
        Called each time the page admin url is called.
        :return:
        """
        # print '-------------------handle_admin_request'
        r_handler = Template(self.p_template_id).admin_request_handler
        method = request.method
        if r_handler:
            target = request.args.get('target', '')
            return r_handler(page=self, method=method, target=target, **kwargs)

        if method == 'GET':
            return self.render_admin_page(**kwargs)

        return abort(405)

    def render_admin_page(self, **kwargs):
        """
        Called to render the admin template of the page: pages.<template_id>.admin.index
        :param kwargs:
        :return:
        """
        # print '-------------------render_admin_page'
        return Template(self.p_template_id).render_admin_index(page=self, **kwargs)

    def handle_request(self, **kwargs):
        """
        Called each time the page url is called.
        :return:
        """
        # inject menus into the page
        kwargs.update(self._get_menus_dict())

        # print '-------------------handle_request'
        r_handler = Template(self.p_template_id).request_handler
        method = request.method

        if r_handler:
            target = request.args.get('target', '')
            return r_handler(page=self, method=method, target=target, **kwargs)

        if method == 'GET':
            return self.render_page(**kwargs)

        return abort(405)

    def render_page(self, **kwargs):
        """
        Called to render the template of the page: pages.<template_id>.views.index
        :param kwargs:
        :return:
        """
        # print '-------------------render_page'
        return Template(self.p_template_id).render_index(page=self, **kwargs)

    @property
    def cacheable(self):
        views_rh = Template(self.p_template_id).request_handler
        if views_rh:
            return False
        return True
