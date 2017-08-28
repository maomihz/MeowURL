from meowurl import app, db
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
from .paste import Paste
from .invitecode import InviteCode

import re

class User(db.Model):
    __tablename__ = app.config['DB_PREFIX'] + 'user'

    uid = db.Column(db.Integer())
    _name = db.Column('name', db.String(64))

    # Username is lower case name
    username = db.Column(db.String(64), unique=True, primary_key=True)
    _password = db.Column('password', db.String(128), nullable=True)
    email = db.Column(db.String(64), unique=True, nullable=True)

    # Anonymous user is users without username and email
    anonymous = db.Column(db.Boolean())

    # Registration date of the user
    regdate = db.Column(db.DateTime())

    pastes = db.relationship('Paste', backref='owner', lazy='dynamic')
    invite_codes = db.relationship('InviteCode', backref='owner', lazy='dynamic')
    invites_left = db.Column(db.Integer())

    def __init__(self, name, email, password, anonymous=False):
        self.anonymous = anonymous
        self.name = name
        self.password = password
        self.email = email

        last_user = User.query.filter(User.anonymous.isnot(True)).order_by(-User.uid).first()
        self.uid = 1 if not last_user else last_user.uid + 1

        self.regdate = datetime.utcnow()
        self.pastes = []
        self.invite_codes = []
        self.invites_left = app.config['USER_INVITES']

    @hybrid_property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
        self.username = name.lower()

    @db.validates('username')
    def validate_username(self, key, username):
        username_regex = re.compile(r'^[a-z0-9][a-z0-9\._]+?$')
        anonymous_regex = re.compile(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
        if self.anonymous:
            if not anonymous_regex.match(username):
                raise AssertionError('Illegal anonymous user!')
        else:
            if not username_regex.match(username):
                raise AssertionError('Username can only contain letters, underscore and dot. ')
            if username in app.config['RESERVED_USERNAMES']:
                raise AssertionError('You cannot register this reserved username!')

        user = User.query.get(username)
        if user:
            raise AssertionError('The username already exist!')
        return username

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        if not self.anonymous:
            password_len = len(password)
            self._password = generate_password_hash(password, method='pbkdf2:sha256:1200')

    @db.validates('email')
    def check_email(self, key, email):
        return email

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def add_paste(self, content, password):
        paste = Paste(content, password)
        self.pastes.append(paste)
        db.session.commit()
        return paste

    def generate_code(self, count=1):
        available = min(self.invites_left, count)
        codes = InviteCode.generate_code(available)
        self.invite_codes.extend(codes)
        self.invites_left -= available
        db.session.commit()
        return codes


    def as_dict(self):
        return dict(
            username=self.username,
            anonymous=self.anonymous,
        )

    @classmethod
    def check_email_exist(cls, email):
        return cls.query.filter(User.email == email).first()

    @classmethod
    def add_user(cls, name, password, email, invite_code=None, anonymous=False):
        user = User(name, password, email, anonymous)

        # If open registration is not set, check and use invite code
        if not anonymous and not app.config['OPEN_REGISTRATION']:
            InviteCode.use_code(invite_code)
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def add_anonymous_user(cls, name):
        return cls.add_user(name, None, None, anonymous=True)

    @classmethod
    def get_user(cls, name):
        user = cls.query.get(name.lower())
        return user
