# -*- coding: utf-8 -*-
import time
from flask.blueprints import Blueprint
from flask import render_template, make_response

bp = Blueprint('atuin.js_translations', __name__)


@bp.route(u'en/atuin/js_translations.js', endpoint='index_en')
@bp.route(u'atuin/js_translations.js')
def index():
    resp = make_response(render_template('atuin/js_translations/base.js'))
    resp.headers['Content-Type'] = 'application/javascript'
    resp.cache_control.max_age = 60 * 60
    resp.expires = int(time.time() + 60 * 60)

    return resp
