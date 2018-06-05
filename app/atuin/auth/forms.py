# -*- coding: utf-8 -*-
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, BooleanField, \
    DateTimeField, SelectField, SelectMultipleField, TextAreaField
from wtforms.validators import DataRequired, Optional

from permission_policies import user_role_polices

user_roles_choices = [(role_id, role['title']) for role_id, role in user_role_polices.iteritems()]


class LoginForm(FlaskForm):
    email = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])


class UserFormAdmin(FlaskForm):
    active = BooleanField()
    role = RadioField(choices=user_roles_choices, validators=[DataRequired()])

    email = StringField(validators=[DataRequired()])
    username = StringField(validators=[DataRequired()])
    password = PasswordField()

    prefix = SelectField(
        choices=[('MISS', 'Miss'), ('MRS', 'Mrs'), ('MR', 'Mr'), ('MS', 'Ms')],
        validators=[Optional()])
    name = StringField(validators=[DataRequired()])
    surname = StringField(validators=[DataRequired()])
    gender = SelectField(choices=[('M', 'Male'), ('F', 'Female')],
                         validators=[Optional()])

    notes = TextAreaField()
