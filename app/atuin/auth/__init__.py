# -*- coding: utf-8 -*-
"""
With help from the original decorators.py from
https://github.com/kamalgill/flask-appengine-template/blob/master/src/application/decorators.py
"""
import flask_login as login
from functools import wraps
from google.appengine.api import users
from flask import redirect, request, abort

setattr(login.AnonymousUserMixin, "username", "GUEST")

login_manager = login.LoginManager()
login_required = login.login_required
current_user = login.current_user


def gae_admin_required(func):
	"""Requires App Engine admin credentials"""

	@wraps(func)
	def decorated_view(*args, **kwargs):
		if users.get_current_user():
			if not users.is_current_user_admin():
				abort(401)  # Unauthorized
			return func(*args, **kwargs)
		return redirect(users.create_login_url(request.url))

	return decorated_view


def login_role_required(*roles):
	"""Require specific role"""

	def real_decorator(func):
		@wraps(func)
		def decorated_view(*args, **kwargs):
			if current_user.is_authenticated and current_user.role in roles:
				return func(*args, **kwargs)
			abort(403)

		return decorated_view

	return real_decorator
