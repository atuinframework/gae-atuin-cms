# - coding: utf-8 -
from flask_wtf import FlaskForm

from wtforms import StringField, SelectField, TextAreaField, HiddenField, DateField, IntegerField
from wtforms.validators import DataRequired, Optional


class MenuFormAdmin(FlaskForm):
    lang = StringField(validators=[DataRequired()])
    parent_menu = StringField(validators=[DataRequired()])
    linked_page = StringField()
    name = StringField(validators=[DataRequired()])
    description = TextAreaField()


class MenuLangFormAdmin(FlaskForm):
    language = StringField(validators=[DataRequired()])
    name = StringField(validators=[DataRequired()])
    description = TextAreaField()
