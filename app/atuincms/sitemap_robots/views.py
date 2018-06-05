# -*- coding: utf-8 -*-
from flask import g, render_template, make_response, request
from flask.blueprints import Blueprint
from atuincms.router import Template
from atuincms.router.models import Route

bp = Blueprint('atuincms.sitemap', __name__)


@bp.route("robots.txt")
def robots():
    template = render_template('atuincms/sitemap_robots/robots.txt', url_root=request.url_root)
    response = make_response(template)
    response.headers['Content-Type'] = 'text/plain'

    return response


@bp.route("sitemap.xml")
def sitemap():
    routes = []
    routes = Route.query().fetch()
    for r in routes:
        p = Template(r.template_id).load_page(r.page_key)
        lastmod = ''
        if p:
            lastmod = p.ins_timestamp.isoformat()
        for lang, loc_page_info in r.page_names.iteritems():
            loc_page_info['lastmod'] = lastmod

    template = render_template('atuincms/sitemap_robots/sitemap.xml', routes=routes, url_root=request.url_root)
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'

    return response
