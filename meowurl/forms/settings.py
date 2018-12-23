from flask_wtf import FlaskForm
from wtforms import IntegerField
from wtforms.validators import AnyOf, DataRequired

from flask import g

class UserSettingsForm(FlaskForm):
    gencode = IntegerField('gencode', validators=[DataRequired(), AnyOf([1, 10],
                           'You are not allowed to generate such amount. ')])
    def validate(self):
        if not FlaskForm.validate(self):
            return False

        # Check whether the user have enough invites left
        if g.user.invites_left < self.gencode.data:
            self.gencode.errors.append('You do not have enough invites!')
            return False

        return True
