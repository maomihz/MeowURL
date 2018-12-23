from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp, NoneOf

from meowurl.dbmodels import User, InviteCode
from meowurl import app


class LoginForm(FlaskForm):
    username = StringField('username', validators=[
                           DataRequired('Username is required! ')])
    password = StringField('password', validators=[
                           DataRequired('Password is required! ')])

    def validate(self):
        if not FlaskForm.validate(self):
            return False

        # Check that the username exists in the database
        user = User.get_user(self.username.data)
        if not user:
            self.username.errors.append('User does not exist!')
            return False

        # Check if the password for the user is correct
        if not user.check_password(self.password.data):
            self.password.errors.append('Incorrect Password!')
            return False

        return True


class RegisterForm(FlaskForm):
    name = StringField('name', validators=[
                       DataRequired('Username is required!'),
                       Regexp(r'^[a-z0-9][a-z0-9\._]+?$', message='Username can only contain letters, underscore and dot. '), 
                       NoneOf(app.config['RESERVED_USERNAMES'], message='You cannot register this reserved username!')])
    email = StringField('email', validators=[DataRequired(
        'Email is required!'), Email('Invalid email format!')])
    
    # Enforce password security policy
    password = StringField('password', validators=[
                           DataRequired('Password is required!'),
                           Length(min=app.config['MIN_PASSWORD_LENGTH'],
                                  max=app.config['MAX_PASSWORD_LENGTH'],
                                  message='Password length must be %d-%d' %
                                  (app.config['MIN_PASSWORD_LENGTH'], app.config['MAX_PASSWORD_LENGTH'])),
                           EqualTo('repeat_password', message='Password does not match!')
                           ])
    repeat_password = StringField(
        'repeat_password', validators=[DataRequired('Repeat password is required!')])
    invite_code = StringField('invite_code')


    def validate_user(form, field):
        if User.get_user(field.data):
            raise ValidationError('Username Already Registered!')
        
    def validate_email(form, field):
        if User.query.filter(User.email == field.data).first():
            raise ValidationError('Email Already Registered!')

    def validate(self):
        if not FlaskForm.validate(self):
            return False

        # Check for invite code
        if not app.config['OPEN_REGISTRATION']:
            if not self.invite_code.data:
                self.password.errors.append('Invite code is required!')
                return False
            else:
                code = InviteCode.query.get(self.invite_code.data)
                if not code:
                    self.password.errors.append('Invite code is invalid!')
                    return False
        return True
