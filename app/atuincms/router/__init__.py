# -*- coding: utf-8 -*-
from flask import abort

from models import ndb, Route, Template


def weak_load_page_by_url(url):
    """
    Load a page object starting from an url string.
    """
    # print 'load page by url'
    r = Route.query(Route.all_lurls == url).get()
    # print r.key.urlsafe()
    if r is None:
        return r
    p = Template(r.template_id).load_page(r.page_key)
    return p


def load_page_by_key(key_us):
    """
    Load a page object starting from a key urlsafe string.
    """
    # print 'load page by key'
    key = ndb.Key(urlsafe=key_us)
    r = Route.query(Route.page_key == key).get() or abort(404)
    p = Template(r.template_id).load_page(r.page_key)
    return p


def weak_load_page_by_key(key_us):
    """
    Load a page object starting from a key urlsafe string.
    Return None if page not found.
    """
    # print 'weak load page by key'
    key = ndb.Key(urlsafe=key_us)
    r = Route.query(Route.page_key == key).get()
    if r is None:
        return r
    return Template(r.template_id).load_page(r.page_key)


def update_page_route(page):
    """
    Add or update the page to the routing system.
    """
    print '[ROUTER] update_page_route'
    r = Route.query(Route.page_key == page.key).get() or Route()
    r.searchable_page_names = []
    r.all_lurls = page.get_all_lurls().values()
    r.page_key = page.key
    r.template_id = page.p_template_id
    r.root_page = page.parent_section is None
    for lang in page.get_languages():
        r.set_page_name(page.get_name(lang), lang)
        r.set_page_url(page.get_url(lang), lang)
    r.put()


def remove_page_route(page_key):
    """
    Remove a page from the routing system.
    """
    # print 'router (remove_page_route) - DELETING ROUTE'
    r = Route.query(Route.page_key == page_key).get()
    r.key.delete()


def route_exists(url):
    """
    Return whether a route exists or not.
    """
    # print 'check route existence'
    a = Route.query(Route.all_lurls == url).get()
    # print 'route:'
    # print a
    return a is not None


def get_root_routes():
    """
    All root pages: pages that do not belong to any section.
    """
    return Route.query(Route.root_page == True).fetch()
