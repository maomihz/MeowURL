from meowurl import app, db

from random import choice
from string import ascii_letters, digits
from itertools import repeat


class InviteCode(db.Model):
    __tablename__ = app.config['DB_PREFIX'] + 'invitecode'

    code = db.Column(db.String(64), primary_key=True)
    owner_name = db.Column(db.String(64),
                           db.ForeignKey(app.config['DB_PREFIX'] + 'user.username'), nullable=True,
                           )

    def __init__(self, code):
        self.code = code

    @staticmethod
    def generate_code(count=1, length=32):
        codes = []
        chars = ascii_letters + digits
        for i in range(count):
            code = InviteCode(''.join([choice(a) for a in repeat(chars, length)]))
            codes.append(code)
        return codes

    @staticmethod
    def use_code(code):
        c = InviteCode.check_code(code)
        if c:
            db.session.delete(c)
            db.session.commit()
            return True

    @staticmethod
    def check_code(code):
        c = InviteCode.query.get(code)
        return c


    def __repr__(self):
        return 'InviteCode <%s>' % self.code

    __str__ = __repr__
