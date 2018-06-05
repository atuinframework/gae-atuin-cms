# - coding: utf-8 -
from flask_wtf import FlaskForm

from wtforms import StringField, SelectField, TextAreaField, HiddenField, DateField, IntegerField
from wtforms.validators import DataRequired, Optional

from languages import lang_title_l as langs


class SectionFormAdmin(FlaskForm):
    lang = StringField(validators=[DataRequired()])
    parent_section = StringField(validators=[DataRequired()])
    name = StringField(validators=[DataRequired()])
