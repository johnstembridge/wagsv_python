from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import CSRFProtect
from flask_sendmail import Mail

from globals import logging, config

db_path = config.get('db_path')
engine = create_engine(db_path, convert_unicode=True, echo=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()
mail = Mail()


def init_app(app, create=False):
    app.config['SECRET_KEY'] = config.get('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = db_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    bootstrap = Bootstrap(app)
    csrf = CSRFProtect(app)
    logging.log_init(app)
    mail.init_app(app)

    db = SQLAlchemy(app)
    if create:
        import models.wags_db
        models.wags_db.Base.metadata.create_all(bind=engine)
