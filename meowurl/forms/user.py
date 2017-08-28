from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Email, Length

from meowurl.dbmodels import User, InviteCode
from meowurl import app


class LoginForm(FlaskForm):
    username = StringField('username', validators=[
                           DataRequired('Username is required! ')])
    password = StringField('password', validators=[
                           DataRequired('Password is required! ')])

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        if not FlaskForm.validate(self):
            return False

        user = User.get_user(self.username.data)
        if not user:
            self.username.errors.append('User does not exist!')
            return False

        if not user.check_password(self.password.data):
            self.password.errors.append('Incorrect Password!')
            return False

        self.user = user
        return True


class RegisterForm(FlaskForm):
    name = StringField('name', validators=[
                       DataRequired('Username is required!')])
    email = StringField('email', validators=[DataRequired(
        'Email is required!'), Email('Invalid email format!')])
    password = StringField('password', validators=[
                           DataRequired('Password is required!'),
                           Length(min=app.config['MIN_PASSWORD_LENGTH'],
                                  max=app.config['MAX_PASSWORD_LENGTH'],
                                  message='Password length must be %d-%d' %
                                  (app.config['MIN_PASSWORD_LENGTH'], app.config['MAX_PASSWORD_LENGTH']))]
                           )
    repeat_password = StringField(
        'repeat_password', validators=[DataRequired('Repeat password is required!')])
    invite_code = StringField('invite_code')

    def validate(self):
        if not FlaskForm.validate(self):
            return False

        if User.get_user(self.name.data):
            self.name.errors.append('Username Already Registered!')

        # Check for email existance
        email_user = User.query.filter(User.email == self.email.data).first()
        if email_user:
            self.email.errors.append('Email Already Registered!')

        # Check password
        if self.password.data != self.repeat_password.data:
            self.password.errors.append('Password does not match!')

        # Check for invite code
        if not app.config['OPEN_REGISTRATION']:
            if not self.invite_code.data:
                self.password.errors.append('Invite code is required!')
            else:
                code = InviteCode.query.get(self.invite_code.data)
                if not code:
                    self.password.errors.append('Invite code is invalid!')
        return True
