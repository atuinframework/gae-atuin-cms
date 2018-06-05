# - coding: utf-8 -
import datetime, json
from flask.blueprints import Blueprint
from flask import render_template, jsonify, request, abort, g, flash
from flask_babel import _

from google.appengine.ext import deferred

from atuin.auth import login_role_required, current_user
from atuincms.pages.admin import load_page_by_key

from models import ndb, Menu, _menu_generate_tree, get_menus_by_parent
from forms import MenuFormAdmin, MenuLangFormAdmin

bp = Blueprint('atuincms.menus.admin', __name__)


@bp.route("admin/atuincms/menus")
@bp.route("en/admin/atuincms/menus", endpoint='index_en')
@login_role_required("ADMIN")
def index():
    menus = get_menus_by_parent(None)
    menu_lang_form = MenuLangFormAdmin()

    menu_form = MenuFormAdmin()
    return render_template('atuincms/menus/admin/index.html',
                           menuid='menus', menus=menus,
                           menu_form=menu_form,
                           menu_lang_form=menu_lang_form)


@bp.route('admin/atuincms/menus/<menu_key_us>')
@login_role_required("ADMIN")
def menu_get(menu_key_us):
    m = ndb.Key(urlsafe=menu_key_us).get() or abort(404)
    return jsonify(m.to_dict())


@bp.route('admin/atuincms/menus/<menu_key_us>/submenus')
@login_role_required("ADMIN")
def get_submenus(menu_key_us=None):
    submenus = get_menus_by_parent(menu_key_us)

    return render_template('atuincms/menus/admin/submenus.html', submenus=submenus)


@bp.route("admin/atuincms/menus", methods=['POST'])
@bp.route("admin/atuincms/menus/<menu_key_us>", methods=['POST'])
@login_role_required("ADMIN")
def menu_save(menu_key_us=None):
    form = MenuFormAdmin()

    # form validation
    if not form.validate_on_submit():
        return "VALIDATION_ERROR", 400

    # get and validate parent menu
    if form.parent_menu.data == '/':
        parent_menu_key = None
    else:
        parent_menu = ndb.Key(urlsafe=form.parent_menu.data).get() or abort(404)
        parent_menu_key = parent_menu.key

    # get and validate linked page
    if form.linked_page.data == '':
        # print 'LINKED NONE!'
        linked_page = None
    else:
        # pass
        linked_page = load_page_by_key(form.linked_page.data)

    # menu instance
    if menu_key_us:
        # edit
        menu = ndb.Key(urlsafe=menu_key_us).get() or abort(404)
    else:
        # new
        menu = Menu()

    # update data
    g.cache.clear()
    menu.parent_menu = parent_menu_key
    menu.set_linked_page(linked_page)
    menu.set_name(form.name.data, form.lang.data)
    menu.set_description(form.description.data, form.lang.data)
    menu.put()

    flash(_('Menu salvato con successo'))
    return 'ok'


@bp.route("admin/atuincms/menus/tree")
@login_role_required("ADMIN")
def tree():
    lang = request.args.get('lang', g.language)

    menu_tree = ndb.Key('MenuTree', lang).get()
    if menu_tree is None:
        menu_tree = {}
    else:
        menu_tree = menu_tree.tree
    return jsonify(results=menu_tree)


@bp.route('admin/atuincms/menus/<menu_key_us>/languages', methods=['POST'])
@login_role_required("ADMIN")
def menu_language_save(menu_key_us=None):
    form = MenuLangFormAdmin()

    if not form.validate_on_submit():
        return "VALIDATION_ERROR", 400

    menu = ndb.Key(urlsafe=menu_key_us).get() or abort(404)
    # update data
    g.cache.clear()
    menu.set_name(form.name.data, form.language.data)
    menu.set_description(form.description.data, form.language.data)
    menu.put()

    return 'ok'


@bp.route('admin/atuincms/menus/switch/<menu_key_us>/<menu_key_us_target>', methods=['POST'])
@login_role_required("ADMIN")
def menu_switch(menu_key_us, menu_key_us_target):
    # target is 0, source is + 1

    menu = ndb.Key(urlsafe=menu_key_us).get() or abort(404)
    menu_target = ndb.Key(urlsafe=menu_key_us_target).get() or abort(404)

    g.cache.clear()
    if menu.order == menu_target.order:
        menu_target.order += 1
        menu_target.put()
    else:
        t = menu_target.order
        menu_target.order = menu.order
        menu.order = t

        menu.put()
        menu_target.put()

    deferred.defer(_menu_generate_tree, _countdown=3)
    return 'OK'


@bp.route('admin/atuincms/menus/reindex-all')
def reindex_all_menus():
    g.cache.clear()
    menus = Menu.query().fetch()
    for m in menus:
        m.put()

    return "done"
