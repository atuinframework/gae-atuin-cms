# -*- coding: utf-8 -*-
import datetime
from flask.blueprints import Blueprint
from flask import request, redirect, flash, render_template, g, session
from flask_babel import _
from atuin.auth.models import User
from flask_login import login_user, logout_user
from google.appengine.api import users as gae_users

bp = Blueprint('atuincms.auth', __name__)


@bp.route("atuincms/auth/login")
@bp.route("en/atuincms/auth/login", endpoint='login_en')
def login():
    return render_template('atuincms/auth/loginpage.html')
