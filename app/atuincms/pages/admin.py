# -*- coding: utf-8 -*-
from flask.blueprints import Blueprint
from flask import g, render_template, jsonify, flash, request, abort
from forms import AcmsNewPageFormAdmin, AcmsPageInfoFormAdmin, AcmsEditPageFormAdmin
from flask_babel import _
from google.appengine.ext import ndb, blobstore

from atuin.auth import login_role_required
from atuincms.router import Route, Template, load_page_by_key, get_root_routes

bp = Blueprint('atuincms.pages.admin', __name__)


@bp.route("admin/atuincms/pages/new")
@bp.route("en/admin/atuincms/pages/new", endpoint='page_new_en')
@login_role_required("ADMIN")
def page_new():
    form = AcmsNewPageFormAdmin()
    form.template.choices = sorted(Template.available_templates(), key=lambda e: e[1].name)
    return render_template('atuincms/pages/admin/page_new.html', menuid='pages', new_page_admin_form=form)


@bp.route("admin/atuincms/pages", methods=['POST'])
@bp.route("en/admin/atuincms/pages", methods=['POST'], endpoint='index_en')
@login_role_required("ADMIN")
def save_new():
    form = AcmsNewPageFormAdmin()
    form.template.choices = Template.available_templates()
    if not form.validate_on_submit():
        return "VALIDATION_ERROR", 400

    template_id = form.template.data
    name = form.name.data
    description = form.description.data

    page = Template(template_id).new_page()
    page.set_name(name, g.language)
    page.set_description(description, g.language)
    page.put()

    res = {
        'result': 'ok',
        'url': g.lurl_for('.page_management', page_key_us=page.key.urlsafe())
    }
    return jsonify(res)


@bp.route('admin/atuincms/pages/<page_key_us>')
@login_role_required("ADMIN")
def page_get(page_key_us):
    page = load_page_by_key(page_key_us)
    return jsonify(page.to_dict())


@bp.route("admin/atuincms/pages")
@bp.route("en/admin/atuincms/pages", endpoint='pages_en')
@login_role_required("ADMIN")
def pages():
    res = []
    q = request.args.get('q', '')
    q = q.lower()
    routes = Route.query(Route.searchable_page_names == q).fetch(10)

    for route in routes:
        r = {
            'value': route.page_key.urlsafe(),
            'page_name': route.get_page_name(g.language),
            'page_url': route.get_page_url(g.language)
        }
        res.append(r)
    return jsonify({'results': res})


@bp.route("admin/atuincms/pages/<page_key_us>/edit", methods=['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
@bp.route("en/admin/atuincms/pages/<page_key_us>/edit", methods=['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
          endpoint='page_management_en')
@login_role_required("ADMIN")
def page_management(page_key_us):
    page = load_page_by_key(page_key_us)
    target = request.args.get('target', '')

    # handle CMS operations before passing control to the page
    # parent section management
    if target == 'acms-page-edit':
        g.cache.delete(page.url)
        return page_edit(page)

    # page info management
    if target == 'acms-page-info':
        g.cache.delete(page.url)
        return page_info(page)

    # page deletion
    if target == 'acms-page-delete':
        g.cache.clear()
        return page_delete(page)

    menuid = 'sections'
    acms_edit_page_form = AcmsEditPageFormAdmin()
    acms_page_info_form = AcmsPageInfoFormAdmin()

    return page.handle_admin_request(
        menuid=menuid,
        acms_edit_page_form=acms_edit_page_form,
        acms_page_info_form=acms_page_info_form
    )


def page_info(page):
    if request.method == 'GET':
        return jsonify(descriptions=page.descriptions)

    if request.method == 'POST':
        form = AcmsPageInfoFormAdmin()
        if not form.validate_on_submit():
            return "VALIDATION_ERROR", 400

        # update data
        page.set_name(form.name.data, form.language.data)
        page.set_description(form.description.data, form.language.data)
        page.put()

        res = {
            'result': 'ok',
            'url': g.lurl_for('.page_management', page_key_us=page.key.urlsafe())
        }
        return jsonify(res)


def page_edit(page):
    if request.method == 'POST':
        form = AcmsEditPageFormAdmin()
        if not form.validate_on_submit():
            return "VALIDATION_ERROR", 400

        # parent section urlsafe key
        ps_key_us = form.parent_section.data
        if ps_key_us == '/':
            ps_key = None
        else:
            ps_key = ndb.Key(urlsafe=ps_key_us)

        # update data
        page.parent_section = ps_key
        page.put()
        res = {
            'result': 'ok',
            'url': g.lurl_for('.page_management', page_key_us=page.key.urlsafe())
        }
        return jsonify(res)


def page_delete(page):
    if request.method == 'DELETE':
        page.key.delete()
        res = {
            'result': 'ok',
            'url': g.lurl_for('atuincms.sections.admin.index')
        }
        return jsonify(res)


@bp.route('admin/atuincms/pages/<page_key_us>/texts/<text_id>', methods=['GET', 'POST', 'DELETE'])
@login_role_required("ADMIN")
def page_text(page_key_us, text_id):
    page = load_page_by_key(page_key_us)

    if request.method == 'GET':
        text = page.text(text_id)
        text_html = page.text_html(text_id)
        return jsonify(text=text, text_html=text_html)

    if request.method == 'POST':
        g.cache.delete(page.url)
        new_text = request.form['text']
        page.text_save(text_id, new_text)
        page.put()

    if request.method == 'DELETE':
        g.cache.delete(page.url)
        page.text_delete(text_id)
        page.put()

    text = page.text(text_id)
    text_html = page.text_html(text_id)
    return jsonify(result='ok', text=text, text_html=text_html)


@bp.route('admin/atuincms/pages/<page_key_us>/images/<image_id>', methods=['POST', 'DELETE'])
@login_role_required("ADMIN")
def page_image(page_key_us, image_id):
    page = load_page_by_key(page_key_us)

    if request.method == 'POST':
        g.cache.delete(page.url)
        # upload new image
        blob_key = request.files['upload'].mimetype_params['blob-key']
        blob = blobstore.get(blob_key)
        page.image_save(image_id, blob)

    if request.method == 'DELETE':
        g.cache.delete(page.url)
        page.image_delete(image_id)

    page.put()
    image_url = page.image_url(image_id)
    image_exists = page.image_exists(image_id)
    return jsonify(result='ok', image_url=image_url, image_exists=image_exists)


@bp.route('admin/atuincms/pages/<page_key_us>/linked-pages/<linked_page_id>', methods=['GET', 'POST', 'DELETE'])
@login_role_required("ADMIN")
def page_linked_page(page_key_us, linked_page_id):
    page = load_page_by_key(page_key_us)

    if request.method == 'GET':
        res = {
            'value': page.linked_page_key_us(linked_page_id),
            'exists': page.linked_page_exists(linked_page_id),
            'page_name': page.linked_page_name(linked_page_id),
            'page_url': page.linked_page_url(linked_page_id)
        }
        return jsonify(**res)

    if request.method == 'POST':
        g.cache.delete(page.url)
        linked_page_key_us = request.form['linked_page']
        if linked_page_key_us:
            page.linked_page_save(linked_page_id, linked_page_key_us)
            flash(_('Linked paged saved successfully'))
        else:
            page.linked_page_delete(linked_page_id)
        page.put()

    if request.method == 'DELETE':
        g.cache.delete(page.url)
        page.linked_page_delete(linked_page_id)
        page.put()

    res = {
        'result': 'ok',
        'page_key_us': page.linked_page_key_us(linked_page_id),
        'page_name': page.linked_page_name(linked_page_id),
        'page_url': page.linked_page_url(linked_page_id)
    }
    return jsonify(**res)


@bp.route('admin/atuincms/pages/<page_key_us>/linked-sections/<linked_section_id>', methods=['GET', 'POST', 'DELETE'])
@login_role_required("ADMIN")
def linked_section(page_key_us, linked_section_id):
    page = load_page_by_key(page_key_us)

    if request.method == 'GET':
        res = {
            'value': page.linked_section_key_us(linked_section_id),
            'exists': page.linked_section_exists(linked_section_id),
            'section_name': page.linked_section_name(linked_section_id),
            'section_path': page.linked_section_path(linked_section_id)
        }
        return jsonify(**res)

    if request.method == 'POST':
        g.cache.delete(page.url)
        linked_section_key_us = request.form['linked_section']
        if linked_section_key_us:
            page.linked_section_save(linked_section_id, linked_section_key_us)
            flash(_('Linked section saved successfully'))
        else:
            page.linked_section_delete(linked_section_id)
        page.put()

    if request.method == 'DELETE':
        g.cache.delete(page.url)
        page.linked_section_delete(linked_section_id)
        page.put()

    res = {
        'result': 'ok',
        'page_key_us': page.linked_page_key_us(linked_section_id),
        'page_name': page.linked_section_name(linked_section_id),
        'section_path': page.linked_section_path(linked_section_id)
    }
    return jsonify(**res)


def index(page, **kwargs):
    return render_template('atuincms/pages/admin/base.html', **kwargs)


def request_handler(page, method, target, **kwargs):
    pass
