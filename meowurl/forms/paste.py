from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired, AnyOf, Length, Regexp

from meowurl import app
from meowurl.extra import conv_id_str
from meowurl.dbmodels import Paste


class BaseForm(FlaskForm):
    ''' This is the form used to create a new paste '''
    content = StringField('content', validators=[
        DataRequired(message='No content!'),
        Length(min=1, max=app.config['MAX_CONTENT_LENGTH'], message='Content too long!')])

    password = StringField('password')

class PasteForm(BaseForm):
    format = StringField('format', validators=[
        AnyOf(['url', 'text', 'file'], message='Invalid format!')],
    )


class EditPasteForm(BaseForm):
    id = StringField('id', validators=[Regexp('[%s]+' % app.config['URL_CHARSET'])])
    rmpass = BooleanField('rmpass')

    def __init__(self):
        super().__init__()
        self.paste = None

    def validate(self):
        if not super().validate():
            return False

        paste = Paste.get_paste(conv_id_str(self.id.data))
        if not paste:
            self.id.errors.append('Paste does not exist!')
            return False
        self.paste = paste
        return True
