from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import CSRFProtect
from flask_sendmail import Mail

from globals import logging, config

db_path = config.get('db_path')
db = SQLAlchemy()

mail = Mail()


def init_app(app, create=False):
    app.config['SECRET_KEY'] = config.get('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = db_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    Bootstrap(app)
    CSRFProtect(app)
    logging.log_init(app)
    mail.init_app(app)
    db.init_app(app)

    if create:
        db.create_all()
