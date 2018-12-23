from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired, Length

from flask import g
from meowurl import app

class NewPasteForm(FlaskForm):
    content = StringField('content', validators=[
                          DataRequired('No Content.'),
                          Length(message='Content too long', max=app.config['MAX_CONTENT_LENGTH'])
                          ])
    password = StringField('password')

class EditPasteForm(NewPasteForm):
    rmpass = BooleanField()
