from meowurl import app, db
from flask import g
import pylibmc
from meowurl.dbmodels import User, Paste
import contextlib


class Client(pylibmc.Client):
    def __build_prefix(self, prefix):
        return '_'.join([app.config['MEMCACHE_PREFIX'], prefix]) + '_' + g.session_id

    def set(self, prefix, item):
        return super().set(self.__build_prefix(prefix), item)

    def get(self, prefix):
        return super().get(self.__build_prefix(prefix))

    def delete(self, prefix):
        return super().delete(self.__build_prefix(prefix))

    def get_login(self):
        return self.get('login')

    def set_login(self, username):
        old_user = g.user
        g.user = User.get_user(username)
        old_pastes = old_user.pastes.all()

        # Transfer ownership
        if old_user.anonymous:
            g.user.pastes.extend(old_user.pastes)
            old_user.pastes = []
        db.session.commit()
        self.set('login', g.user.username)

    def set_logout(self):
        return self.delete('login')

    def add_authorized(self, id):
        authorized_list = self.get('authorized_list') or set()
        authorized_list.add(id)
        self.set('authorized_list', authorized_list)

    def get_authorized(self, id):
        authorized_list = self.get('authorized_list') or set()
        paste = Paste.get_paste(id)

        with contextlib.suppress(AttributeError):
            return paste.owner is g.user or paste.id in authorized_list
        return False

    # Customized version of flash
    def flash(self, message):
        flashes = self.get('flash') or []
        flashes.append(message)
        self.set('flash', flashes)

    def get_flashed_messages(self):
        flashes = self.get('flash')
        self.delete('flash')
        return flashes
