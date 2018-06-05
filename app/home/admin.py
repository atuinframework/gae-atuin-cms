# -*- coding: utf-8 -*-
import datetime
from flask.blueprints import Blueprint
from flask import g, render_template, jsonify, flash, request, abort, redirect
import flask_login as login

from atuin.auth import login_role_required

bp = Blueprint('home.admin', __name__)


@bp.route("admin")
@bp.route("en/admin", endpoint='index_en')
def index():
    current_user = login.current_user

    if current_user.is_authenticated and current_user.role == 'ADMIN':
        return redirect(g.lurl_for('atuincms.menus.admin.index'))

    return redirect(g.lurl_for('atuincms.auth.login'))
