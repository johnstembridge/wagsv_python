from flask import request
from flask_login import LoginManager
from front_end import login
from wags_admin import app
from globals import config
from back_end.interface import get_user

role = 'admin'
login_manager = LoginManager(app)
login_manager.login_view = config.get('url_prefix')[role]+'/login'


@login_manager.user_loader
def load_user(id):
    return get_user(id=int(id))


@app.route('/login', methods=['GET', 'POST'])
def admin_login():
    next_page = request.args.get('next')
    return login.user_login(role, next_page)


@app.route('/logout', methods=['GET', 'POST'])
def user_logout():
    return login.user_logout(role)


@app.route('/register', methods=['GET', 'POST'])
def admin_register():
    return login.user_register(role)