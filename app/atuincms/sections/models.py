# - coding: utf-8 -
from collections import OrderedDict
from flask import abort, g
from google.appengine.ext import ndb
from google.appengine.ext import deferred

from languages import lang_title
from atuin.utils import slugify, update_searchable_set
from atuincms.pages.admin import load_page_by_key


class Section(ndb.Model):
    # TODO https://cloud.google.com/appengine/docs/standard/python/datastore/entities#Python_Ancestor_paths
    p_parent_section = ndb.KeyProperty('p', kind='Section')
    lname_searchable = ndb.StringProperty('lns', repeated=True, indexed=True)
    all_lpaths_l = ndb.StringProperty('alp', repeated=True, indexed=True)

    p_descriptions = ndb.PickleProperty('d', default={})
    # {
    # 	'en': {
    # 		'name': 'What we do',
    # 		'path': 'en/company/what-we-do'
    # 	},
    # 	'it': {
    # 		'name': 'Cosa facciamo',
    # 		'path': 'it/azienda/cosa-facciamo'
    # 	}
    # }

    p_pages_names = ndb.PickleProperty('pgs', default=OrderedDict())
    # p_pages_names = OrderedDict({
    # 	'page_key_us_1': {
    # 		'en' : 'How it works?',
    # 		'it' : 'Come funziona?'
    # 	},
    # 	'page_key_us_2': {
    # 		'en': 'How it works2?',
    # 		'it': 'Come funziona2?'
    # 	},
    # })

    # On the _post_put_hook, is it necessary to update descendants pages and sections?
    p_must_update_descendants = False
    p_post_put_generate_tree = False

    def __repr__(self):
        return "<Section %s>" % self.key

    def to_dict(self):
        d = super(Section, self).to_dict(exclude=['p_parent_section', 'p_descriptions'])
        d['key_us'] = self.key.urlsafe()
        d['languages'] = self.get_languages()
        d['descriptions'] = self.descriptions
        if self.parent_section:
            d['parent_section'] = self.parent_section.urlsafe()
        else:
            d['parent_section'] = '/'
        return d

    @property
    def descriptions(self):
        return self.p_descriptions

    def get_languages(self):
        return self.descriptions.keys()

    def get_subsections(self):
        return self.query(self.__class__.p_parent_section == self.key).fetch()

    # ### Parent section ###
    @property
    def parent_section(self):
        return self.p_parent_section

    @parent_section.setter
    def parent_section(self, parent_sect_key):
        self.p_parent_section = parent_sect_key
        # Update the paths
        self._update_lpaths()
        # Then lnames (maybe a disambiguate section name invocation has changed the section name)
        self._update_lnames()

    # ### Name ###
    def get_name(self, lang):
        if self.descriptions.get(lang):
            return self.descriptions[lang]['name']
        return 'N/D'

    @property
    def name(self):
        return self.get_name(g.language)

    def set_name(self, name, lang):
        if not self.descriptions.get(lang):
            self.descriptions[lang] = {}

        # 0. Verify it is not a silly parameter update
        if self.descriptions[lang].get('name'):
            if self.descriptions[lang]['name'] == name:
                # print 'section - set_name(%s, %s) execution truncated, SAME NAME AS BEFORE' % (name, lang)
                return

        self.descriptions[lang]['name'] = name

        # Update the paths
        self._update_lpaths()
        # Then lnames (maybe a disambiguate section name invocation has changed the section name)
        self._update_lnames()

    def get_all_lnames(self):
        """
        Return a dict of all localized names.
        """
        names = {}
        for l, desc in self.descriptions.iteritems():
            names[l] = desc['name']
        return names

    # ### Contained pages ###
    @property
    def pages_names(self):
        return self.p_pages_names

    def add_page(self, page):
        page_key_us = page.key.urlsafe()
        self.p_pages_names[page_key_us] = page.get_all_lnames()
        self.p_post_put_generate_tree = True

    def remove_page(self, page_key_urlsafe):
        if page_key_urlsafe in self.pages_names:
            del (self.pages_names[page_key_urlsafe])
            self.p_post_put_generate_tree = True

    # ### Path ###
    def get_path(self, lang):
        if self.descriptions.get(lang):
            return self.descriptions[lang]['path']
        return 'N/D'

    @property
    def path(self):
        return self.get_path(g.language)

    def _disambiguate_section_name(self):
        """
        Add a dash at the end of the section name (all languages) in order to make its path unique.
        """
        for lang, d in self.descriptions.iteritems():
            d['name'] += '-'

    def _generate_lpaths(self, parent_section):
        if parent_section is not None:
            for lang, desc in parent_section.descriptions.iteritems():
                parent_sec_path = desc['path']
                sec_path = slugify(self.get_name(lang))
                self.descriptions[lang]['path'] = parent_sec_path + '/' + sec_path
        else:
            for lang, desc in self.descriptions.iteritems():
                desc['path'] = '/' + lang + '/' + slugify(self.get_name(lang))

        self.all_lpaths_l = self.get_all_lpaths().values()

        # print 'MUST UPDATE DESCENDANTS'
        self.p_must_update_descendants = True

    def _update_lpaths(self, parent_section='TO_BE_LOADED'):
        if parent_section == 'TO_BE_LOADED':
            parent_section = self.parent_section.get() if self.parent_section else None

        # print "\n_update_lurls"
        # When should it be called?
        # - section name change
        # - parent section change
        #
        # What does do:
        # - generate paths
        # - verify section path is unique (if it is not, change the section name and generate paths again)

        # If still it doesn't have one name: no aims to generate an url
        if not bool(self.descriptions):
            return

        exists = True
        while exists:
            # print "_generate_lpaths"
            self._generate_lpaths(parent_section)
            # print self.descriptions
            # pick the first path, doesn't matter the language in which it is
            p = self.descriptions.itervalues().next()['path']
            # print 'picked path:'
            # print p
            # print '\nexists before'
            # print exists
            exists = self.query(self.__class__.all_lpaths_l == p).get() is not None
            # print 'exists after'
            # print exists
            if exists:
                # print 'Already existing section!!'
                self._disambiguate_section_name()

    def _update_lnames(self):
        n_set = set()
        for n in self.get_all_lnames().values():
            n_set = update_searchable_set(n_set, n)
        self.lname_searchable = [nl.lower() for nl in n_set]

    def get_all_lpaths(self):
        """
        Return a list of all localized paths.
        """
        paths = {}
        for l, desc in self.descriptions.iteritems():
            paths[l] = desc['path']
        return paths

    def refresh_derived_parameters(self, parent_section):
        """
        To be called each time the parent section undergoes an update related to its: name, parent_section.
        """
        # Update the lpaths
        self._update_lpaths(parent_section)
        # Then lnames (maybe a disambiguate section name invocation has changed the section name)
        self._update_lnames()

    def _post_put_hook(self, future):
        # if necessary update the descendants
        if self.p_must_update_descendants:
            # print 'UPDATING THE DESCENDANTS!'
            section = future.get_result().get()
            deferred.defer(_update_descendants, section, _countdown=1)

        # if necessary update the three
        if self.p_post_put_generate_tree:
            _section_generate_tree()

    @classmethod
    def _pre_delete_hook(cls, key):
        # To do:
        # - turn pages belonging to the section to root pages
        # - delete sub sections
        section = key.get()
        deferred.defer(_delete_descendants, section, _countdown=1)


def _update_descendants(section):
    # print '\n\nupdate_descendants task'
    # print section.descriptions

    child_sections = Section.query(Section.p_parent_section == section.key).fetch()

    # print child_sections

    # UPDATE CHILD SECTIONS
    for cs in child_sections:
        cs.refresh_derived_parameters(section)
        cs.put()

    # UPDATE CHILD PAGES
    for page_key_us in section.pages_names.iterkeys():
        p = load_page_by_key(page_key_us)
        p.refresh_derived_parameters(section)
        p.put()

    # TREE GENERATION
    if not child_sections:
        _section_generate_tree()


def _delete_descendants(section):
    child_sections = Section.query(Section.p_parent_section == section.key).fetch()

    # DELETE CHILD SECTIONS
    for cs in child_sections:
        cs.key.delete()

    # MOVE CHILD PAGES
    for page_key_us in section.pages_names.iterkeys():
        p = load_page_by_key(page_key_us)
        p.parent_section = None
        p.put()

    # TREE GENERATION
    if not child_sections:
        _section_generate_tree()


def get_sections_by_parent(parent_key=None):
    if parent_key:
        parent_key = ndb.Key(urlsafe=parent_key) or abort(404)
    sections = Section.query(Section.p_parent_section == parent_key).fetch()

    sections_list = [s for s in sections]

    return sections_list


class SectionTree(ndb.Model):
    tree = ndb.PickleProperty('t')
    # tree = [
    # 		{
    # 			'key_us' : 'urlsafe_key',
    # 			'name' : 'What we do',
    # 			'pages_names': OrderedDict({
    # 				'page_key_us_1': {
    # 					'en' : 'How it works?',
    # 					'it' : 'Come funziona?'
    # 				},
    # 				'page_key_us_2': {
    # 					'en': 'How it works2?',
    # 					'it': 'Come funziona2?'
    # 				},
    # 			}),
    # 			'subs': [
    #                       {
    # 							'key_us' : 'urlsafe_key',
    # 							'name' : 'Specialized in',
    # 							'pages_names': OrderedDict({}),
    # 							'subs': {...}
    # 			             },
    #                        {...}
    #       },
    # 		{ ... }
    # ]

    ins_timestamp = ndb.DateTimeProperty('i_ts', auto_now_add=True, indexed=False)
    upd_timestamp = ndb.DateTimeProperty('u_ts', auto_now=True, indexed=False)

    def __repr__(self):
        return "<SectionTree %s>" % self.key

    def get_id(self):
        return self.key.id()

    @classmethod
    def get_by_key(cls, k):
        return ndb.Key(urlsafe=k).get()


def _generate_full_section_trees(section=None):
    if section:
        subsections = section.get_subsections()
    else:
        # root sections
        subsections = Section.query(Section.p_parent_section == None).fetch()

    tree_d = {x: [] for x in lang_title}

    for sub in subsections:
        subs = _generate_full_section_trees(sub)
        for lang in sub.descriptions.iterkeys():
            tree_d[lang].append({
                'key_us': sub.key.urlsafe(),
                'name': sub.get_name(lang),
                'pages_names': sub.pages_names,
                'subs': subs[lang]
            })

    for sections in tree_d.itervalues():
        sections.sort(key=lambda v: v['name'])

    return tree_d


def _section_generate_tree(lang=None):
    trees = _generate_full_section_trees()
    # print 'generated trees'
    # print trees

    for lang_t, tree in trees.iteritems():
        if (lang is None) or (lang_t == lang):
            k = ndb.Key('SectionTree', lang_t)
            m = SectionTree(key=k)
            m.tree = tree
            m.put()


def get_section_pages(section_name='', section_key_us='', only_template_id=None, order_by=None, text_id='',
                      text_idx=None, text_l=None, attr_name=''):
    section = None
    pages = []

    if not section_name == '':
        section = Section.query(Section.lname_searchable == section_name.lower()).get()

    if not section_key_us == '':
        section = ndb.Key(urlsafe=section_key_us).get()

    if section is None:
        return pages

    for page_key_us in section.pages_names.iterkeys():
        page = load_page_by_key(page_key_us)

        if only_template_id is None:
            pages.append(page)
            continue

        # filter by template_id
        if page.p_template_id == only_template_id:
            pages.append(page)

    if order_by == 'page_name':
        pages = sorted(pages, key=lambda page: page.name)
        return pages

    if order_by == 'page_text':
        pages = sorted(pages, key=lambda page: page.text(text_id, text_idx, text_l))
        return pages

    if order_by == 'page_attribute':
        pages = sorted(pages, key=lambda page: getattr(page, attr_name))
        return pages

    return pages
