# -*- coding: utf-8 -*-
from flask import g, request, render_template, abort
from flask.blueprints import Blueprint
from . import weak_load_page_by_url
from atuin.settings import CACHE_DEFAULT_TIME

bp = Blueprint('atuincms.router', __name__)


@bp.route("<path:p_url>", methods=['GET', 'POST', 'HEAD', 'PUT', 'DELETE', 'OPTIONS'])
@bp.route("/", methods=['GET', 'POST', 'HEAD', 'PUT', 'DELETE', 'OPTIONS'])
def route_pages(p_url=None):
	url = request.path

	if len(request.args) > 0:
		cache_key = request.full_path
	else:
		cache_key = request.path

	# try to load the response for the page from cache
	response = g.cache.get(cache_key)
	if response is not None:
		# print 'response not none!! SERVING CACHE for cache_key: ' + url
		return response

	# cached page not found, try to render the page
	p = weak_load_page_by_url(url)
	if p:
		response = p.handle_request()
		if p.cacheable:
			# print 'CACHABLE'
			g.cache.set(cache_key, response, CACHE_DEFAULT_TIME)
		return response

	# home page requested and there's no page
	if url == '/' and p is None:
		return render_template('atuincms/pages/no_home_page.html')

	return abort(404)
