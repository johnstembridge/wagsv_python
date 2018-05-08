from flask import request
from flask_login import LoginManager
from front_end.admin import login
from wags_admin import app
from globals import config
from models.user import User

login_manager = LoginManager(app)
login_manager.login_view = config.get('url_prefix')['admin']+'/login'


@login_manager.user_loader
def load_user(id):
    return User.get(id=int(id))


@app.route('/login', methods=['GET', 'POST'])
def admin_login():
    next_page = request.args.get('next')
    return login.admin_login(next_page)


@app.route('/register', methods=['GET', 'POST'])
def admin_register():
    return login.admin_register()
