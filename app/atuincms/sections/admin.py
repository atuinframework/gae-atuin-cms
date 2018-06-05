# - coding: utf-8 -
import datetime, json
from flask.blueprints import Blueprint
from flask import render_template, jsonify, request, abort, g
from flask_babel import _
from google.appengine.ext import deferred

from atuin.auth import login_role_required, current_user

from models import ndb, Section, get_sections_by_parent
from forms import SectionFormAdmin
import atuincms.router

bp = Blueprint('atuincms.sections.admin', __name__)


@bp.route("admin/atuincms/sections")
@bp.route("en/admin/atuincms/sections", endpoint='index_en')
@login_role_required("ADMIN")
def index():
    # is a search?
    if 'q' in request.args:
        res = []
        q = request.args.get('q', '')
        q = q.lower()
        sections = Section.query(Section.lname_searchable == q).fetch(10)
        for section in sections:
            r = {}
            r['value'] = section.key.urlsafe()
            r['section_name'] = section.name
            r['section_path'] = section.path
            res.append(r)
        return jsonify({'results': res})

    # sections_tree_ent = ndb.Key('SectionTree', g.language).get()
    # if sections_tree_ent:
    # 	sections_tree = sections_tree_ent.tree
    # else:
    # 	sections_tree = {}
    #
    # root_routes = get_root_routes()
    # return render_template(
    # 	'atuincms/pages/admin/index.html',
    # 	menuid='pages',
    # 	sections_tree=sections_tree,
    # 	root_routes=root_routes
    # )

    sections = get_sections_by_parent(None)
    root_routes = atuincms.router.get_root_routes()
    # menu_lang_form = MenuLangFormAdmin()
    section_form = SectionFormAdmin()

    return render_template(
        'atuincms/sections/admin/index.html',
        menuid='sections',
        sections=sections,
        root_routes=root_routes,
        section_form=section_form
    )


@bp.route('admin/atuincms/sections/<section_key_us>')
@login_role_required("ADMIN")
def section_get(section_key_us):
    s = ndb.Key(urlsafe=section_key_us).get() or abort(404)
    return jsonify(s.to_dict())


@bp.route('admin/atuincms/sections/<section_key_us>/subsections')
@login_role_required("ADMIN")
def get_subsections(section_key_us=None):
    subsections = get_sections_by_parent(section_key_us)

    return render_template('atuincms/sections/admin/subsections.html', subsections=subsections)


@bp.route("admin/atuincms/sections", methods=['POST'])
@bp.route("admin/atuincms/sections/<section_key_us>", methods=['POST'])
@login_role_required("ADMIN")
def section_save(section_key_us=None):
    form = SectionFormAdmin()

    # form validation
    if not form.validate_on_submit():
        return "VALIDATION_ERROR", 400

    # get and validate parent section
    if form.parent_section.data == '/':
        parent_section_key = None
    else:
        parent_section = ndb.Key(urlsafe=form.parent_section.data).get() or abort(404)
        parent_section_key = parent_section.key

    # section instance
    if section_key_us:
        # edit
        # print 'admin section save EDIT'
        section = ndb.Key(urlsafe=section_key_us).get() or abort(404)
    else:
        # new
        # print 'admin section save NEW'
        section = Section()

    # update data
    g.cache.clear()
    section.parent_section = parent_section_key
    section.set_name(form.name.data, g.language)
    section.put()
    return 'ok'


@bp.route("admin/atuincms/sections/<section_key_us>", methods=['DELETE'])
@login_role_required("ADMIN")
def section_delete(section_key_us):
    g.cache.clear()
    section = ndb.Key(urlsafe=section_key_us).get() or abort(404)
    section.key.delete()
    return 'ok'


@bp.route("admin/atuincms/sections/tree")
@login_role_required("ADMIN")
def tree():
    lang = request.args.get('lang', g.language)

    sections_tree_entity = ndb.Key('SectionTree', lang).get()
    if sections_tree_entity:
        sections_tree = sections_tree_entity.tree
    else:
        sections_tree = {}

    return jsonify(results=sections_tree)
