
from flask import request
from flask_login import LoginManager
from front_end import login
from wags_user import app
from globals import config
from back_end.interface import get_user

role = 'user'
login_manager = LoginManager(app)
login_endpoint = 'user_login'
login_manager.login_view = login_endpoint
app.logger.info('Login View: {}'.format(login_manager.login_view))


@login_manager.user_loader
def load_user(id):
    return get_user(id=int(id))


@app.route('/login', methods=['GET', 'POST'])
def user_login():
    next_page = request.args.get('next')
    app.logger.info('Next Page: {}'.format(next_page))
    app.logger.info('Converted Next Page: {}'.format(config.adjust_url_for_https(role, next_page)))
    res = login.user_login(role, next_page)
    app.logger.info('Redirect: {}'.format(res))
    return res


@app.route('/logout', methods=['GET', 'POST'])
def user_logout():
    return login.user_logout(role)


@app.route('/register', methods=['GET', 'POST'])
def user_register():
    return login.user_register(role)
