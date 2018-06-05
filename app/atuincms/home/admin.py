# - coding: utf-8 -
from flask import g, render_template, redirect, flash, url_for
from flask.blueprints import Blueprint
from flask_babel import _

from google.appengine.ext import deferred

from atuin.auth import login_role_required, current_user

bp = Blueprint('atuincms.home.admin', __name__)


@bp.route("admin/atuincms")
@bp.route("en/admin/atuincms", endpoint='index_en')
@login_role_required("ADMIN")
def index():
	return render_template('atuincms/home/admin/index.html')


@bp.route("admin/atuincms/flush-cache")
@bp.route("en/admin/atuincms/flush-cache", endpoint='flush_cache_en')
@login_role_required("ADMIN")
def flush_cache():
	g.cache.clear()
	flash(_('Cache emptied successfully'))
	return redirect(url_for('.index'))
