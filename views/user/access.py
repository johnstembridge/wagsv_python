from flask import request
from flask_login import LoginManager
from front_end import login
from wags_user import app
from globals import config
from back_end.interface import get_user

role = 'user'
login_manager = LoginManager(app)
login_manager.login_view = config.qualify_url(role, '/login')
login_manager.login_message = 'You must be a WAGS member to access this page'


@login_manager.user_loader
def load_user(id):
    return get_user(id=int(id))


@app.route('/login', methods=['GET', 'POST'])
def user_login():
    next_page = request.args.get('next')
    return login.user_login(role, next_page, app)


@app.route('/logout', methods=['GET', 'POST'])
def user_logout():
    return login.user_logout(role)


@app.route('/register', methods=['GET', 'POST'])
def user_register():
    return login.user_register(role)


@app.route('/re_register', methods=['GET', 'POST'])
def user_re_register():
    return login.user_register(role, new=False)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    return login.user_reset_password_request(role, app)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    return login.user_reset_password(role, app, token)
