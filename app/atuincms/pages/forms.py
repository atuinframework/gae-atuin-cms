# - coding: utf-8 -
from flask_wtf import FlaskForm

from wtforms import StringField, RadioField, TextAreaField, HiddenField, FileField, SelectField
from wtforms.validators import DataRequired, Optional


class AcmsNewPageFormAdmin(FlaskForm):
    lang = HiddenField(default='it')
    name = StringField(validators=[DataRequired()])
    description = TextAreaField()
    template = SelectField(validators=[DataRequired()])


class AcmsEditPageFormAdmin(FlaskForm):
    parent_section = StringField(validators=[DataRequired()])


class AcmsPageInfoFormAdmin(FlaskForm):
    language = StringField(validators=[DataRequired()])
    name = StringField(validators=[DataRequired()])
    description = TextAreaField()


class AcmsImageUploadFormAdmin(FlaskForm):
    upload = FileField(validators=[DataRequired()])
