from functools import wraps

from flask import abort
from flask_login import current_user


def role_required(*role):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user:
                if role[0] not in [user_role.role.name for user_role in current_user.roles]:
                    # flash('Sorry, you do not have {} access'.format(role))
                    abort(401)
            return f(*args, **kwargs)
        return wrapped
    return wrapper
