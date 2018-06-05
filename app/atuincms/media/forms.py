# - coding: utf-8 -
from flask_wtf import FlaskForm
from wtforms import FileField
from wtforms.validators import DataRequired


class UploadForm(FlaskForm):
    upload = FileField(validators=[DataRequired()])
