from werkzeug.security import check_password_hash, generate_password_hash
from hashlib import sha256
from datetime import datetime
from uuid import uuid4
import codecs
from sqlalchemy.ext.hybrid import hybrid_property

from meowurl import db, app
from meowurl.extra import conv_id_str, URL_REGEX


class Paste(db.Model):
    __tablename__ = app.config['DB_PREFIX'] + 'paste'

    # Integer ID
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Binary UTF-8 encoded content and SHA256 Hash
    _content = db.Column('content', db.LargeBinary(), nullable=False)
    content_hash = db.Column(db.LargeBinary())
    is_url = db.Column(db.Boolean())

    # Owner's username
    owner_name = db.Column(db.String(64), db.ForeignKey(app.config['DB_PREFIX'] + 'user.username'))
    edit_code = db.Column(db.String(64))

    # Password protection
    _password = db.Column('password', db.String(100))
    protected = db.Column(db.Boolean(), default=False)

    # Creation date
    date = db.Column(db.DateTime)

    @hybrid_property
    def content(self):
        return self._content

    @content.setter
    def content(self, content):
        self._content = codecs.encode(content, 'utf-8')
        self.content_hash = sha256(self._content).digest()
        self.is_url = True if URL_REGEX.match(content) else False

    @db.validates('content')
    def validate_content(self, key, content):
        content_len = len(content)
        if content_len <= 0:
            raise AssertionError('Empty Content!')
        if content_len > app.config['MAX_CONTENT_LENGTH']:
            raise AssertionError('Content Too Long!')
        return content

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        if password:
            self._password = generate_password_hash(
                password, method='pbkdf2:sha256:1200', salt_length=8)
            self.protected = True
        else:
            self._password = None
            self.protected = False


    def __init__(self, content, password=''):
        # Set password and contents
        self.content = content
        self.password = password
        self.edit_code = str(uuid4())
        self.date = datetime.utcnow()

    def check_edit_code(self, edit_code):
        return self.edit_code == edit_code

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def as_dict(self):
        return dict(
            id=conv_id_str(self.id),
            content=codecs.decode(self.content, 'utf-8'),
            is_url=self.is_url,
            owner=self.owner.as_dict(),
            edit_code=self.edit_code,
            protected=self.protected,
            date=self.date,
        )

    def __repr__(self):
        return '<Paste #%d: %s>' % (self.id, self.content)


    @classmethod
    def get_paste(cls, id):
        paste = cls.query.get(id)
        return paste

    @classmethod
    def edit_paste(cls, id, content, password):
        paste = cls.query.get(id)
        if not paste:
            return None
        paste.content = content
        paste.password = password

        db.session.commit()

    @classmethod
    def get_all(cls, limit=0, offset=0):
        if limit > 0:
            return cls.query.order_by(-Paste.id).limit(limit).offset(offset).all()
        return cls.query.order_by(-Paste.id).all()
