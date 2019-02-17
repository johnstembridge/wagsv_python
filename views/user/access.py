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
