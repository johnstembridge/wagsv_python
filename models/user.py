from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from back_end.interface import get_admin_user, add_admin_user


class User(UserMixin):

    def __init__(self, username=None, email=None, password_hash=None):
        if type(username) is dict:
            self.id = username['id']
            self.username = username['username']
            self.password_hash = username['password_hash']
            self.email = username['email']
        else:
            self.id = None
            self.username = username
            self.password_hash = password_hash
            self.email = email

    def set_id(self, id):
        self.id = id

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def record(self):
        return {'id': self.id, 'username': self.username, 'email': self.email, 'password_hash': self.password_hash}

    @staticmethod
    def get(id=None, username=None, email=None):
        u = User()
        if id:
            u = get_admin_user('id', id)
        if username:
            u = get_admin_user('username', username)
        elif email:
            u = get_admin_user('email', email)
        if u['id']:
            return User(u)
        else:
            return None

    @staticmethod
    def add(user):
        add_admin_user(user)



