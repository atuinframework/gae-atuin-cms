# -*- coding: utf-8 -*-
import datetime
from flask.blueprints import Blueprint
from flask import g, render_template, jsonify, flash, request, abort, redirect
from flask_login import current_user

from permission_policies import user_role_polices

from atuin.auth import login_role_required
from models import ndb, User
from forms import UserFormAdmin

bp = Blueprint('atuin.auth.admin', __name__)


@bp.route("atuin/admin/auth/users")
@bp.route("en/atuin/admin/auth/users", endpoint='user_index_en')
@login_role_required("ADMIN")
def users():
	search = request.args.get('q', None)
	if search is not None:
		res = []
		if search:
			search = search.strip().lower()
			users = User.query().filter(User.name_searchable == search).fetch(
				30)

			for u in users:
				usr = u.to_dict(include=[
					'name',
					'surname',
					'username',
					'email',
					'logo_image_url'
				])
				usr['key'] = u.get_urlsafe()
				res.append(usr)

		return jsonify(results=res)

	users = User.query().order(User.name).fetch(100)
	user_form_admin = UserFormAdmin()
	return render_template(
		"atuin/auth/admin/users.html",
		menuid='admin', submenuid='users',
		user_form_admin=user_form_admin,
		users=users,
		user_role_polices=user_role_polices
	)


@bp.route("atuin/admin/auth/users/<user_key_us>")
@login_role_required("ADMIN")
def user(user_key_us):
	user = User.get_by_key(user_key_us)
	if not user:
		abort(404)
	user_d = user.to_dict(exclude=['password', 'logo_image', 'preferences'])
	return jsonify(user_d)


@bp.route("atuin/admin/auth/users", methods=['POST'])
@bp.route("atuin/admin/auth/users/<user_key_us>", methods=['POST'])
@login_role_required("ADMIN")
def user_save(user_key_us=None):
	# form validation
	form = UserFormAdmin()
	if not form.validate_on_submit():
		return "VALIDATION_ERROR", 400

	if user_key_us:
		# edit user
		user = User.get_by_key(user_key_us)
		if not user:
			abort(404)
	else:
		# new user
		user = User()

	user.active = form.active.data
	print 'print form.active.data'
	print form.active.data
	user.role = form.role.data

	user.email = form.email.data
	user.username = form.username.data
	if form.password.data != '':
		user.set_password(form.password.data)

	user.prefix = form.prefix.data
	user.name = form.name.data
	user.surname = form.surname.data
	user.gender = form.gender.data

	user.notes = form.notes.data

	# TODO what about insertion of repeated usernames?
	user.put()

	flash(u'User %s saved' % user.username)

	return jsonify(result='ok')


@bp.route("atuin/admin/auth/users/<user_key_us>", methods=['DELETE'])
@login_role_required("ADMIN")
def user_delete(user_key_us):
	user = ndb.Key(urlsafe=user_key_us).get() or abort(404)
	if user == current_user:
		return jsonify(result='ko', error='Cannot delete yourself!!')

	user.key.delete()
	return jsonify(result='ok')
