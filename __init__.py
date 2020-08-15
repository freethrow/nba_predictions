#!/usr/bin/python
# -*- coding: utf-8 -*-


from flask import Flask, flash, redirect, url_for


from flask_admin import Admin

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_login import login_required, current_user
from config import config

from flask_bootstrap import Bootstrap


db = SQLAlchemy()
bootstrap = Bootstrap()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
login_manager.login_message = u"Moraš da se uloguješ da bi nastavio."



from models import User, Series, Prediction




def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)


    bootstrap.init_app(app)


    db.init_app(app)
    login_manager.init_app(app)

    from flask_admin.contrib.sqla import ModelView
    class NbaModelView(ModelView):

        def is_accessible(self):
            if current_user.is_authenticated():
                return current_user.is_admin
            else:
                return False

        def inaccessible_callback(self, name, **kwargs):
            # redirect to login page if user doesn't have access
            return redirect(url_for('login', next=request.url))


    admin = Admin(app, name='nba', template_mode='bootstrap3')
    admin.add_view(NbaModelView(Series, db.session))
    admin.add_view(NbaModelView(User, db.session))
    admin.add_view(NbaModelView(Prediction, db.session))

    @app.errorhandler(500)
    def internal_error(exception):
        app.logger.exception(exception)
        return render_template('500.html'), 500

    @app.errorhandler(404)
    def page_not_found(e):

        return render_template('404.html'), 404

    # logging

    import logging
    from logging.handlers import RotatingFileHandler

    file_handler = RotatingFileHandler('nba.baller.rs.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))

    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)


    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    app.debug = True



    return app
