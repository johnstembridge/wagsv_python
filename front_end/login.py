from werkzeug.urls import url_parse
from flask import render_template, flash, redirect
from flask_login import current_user, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from globals.config import url_for
from models.user import User
from back_end.interface import get_member_by_email


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

    def populate(self):
        pass


def user_login(app, next_page):
    if current_user.is_authenticated:
        return redirect(app, qualify_url(app, next_page))
    form = LoginForm()
    if form.is_submitted():
        if form.validate_on_submit():
            user = User.get(username=form.username.data)
            if user is None or not user.check_password(form.password.data):
                flash('Invalid username or password', 'danger')
                return render_template('{}/login.html'.format(app), title='Sign In', form=form)
            login_user(user, remember=form.remember_me.data)
            if not next_page or url_parse(next_page).netloc != '':
                next_page = qualify_url(app)
            else:
                next_page = qualify_url(app, next_page)
            return redirect(next_page)
    else:
        form.populate()

    return render_template('{}/login.html'.format(app), title='Sign In', form=form)


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.get(username=username.data)
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.get(email=email.data)
        if user is not None:
            raise ValidationError('Please use a different email address.')


def user_register(app):
    if current_user.is_authenticated:
        return redirect(qualify_url(app))
    form = RegistrationForm()
    if form.is_submitted():
        if form.validate_on_submit():
            member = get_member_by_email(form.email.data)
            if member:
                user = User(username=form.username.data, email=form.email.data)
                user.set_password(form.password.data)
                User.add(user)
                flash('Congratulations, you are now a registered user!')
                return redirect(url_for(app, 'user_login'))
            else:
                flash('Unknown member - please give your WAGS home contact email address')
    return render_template('{}/register.html'.format(app), title='Register', form=form)


def qualify_url(app, page=None):
    return (url_for(app, 'index') + page or '').replace("//", "/")


def user_logout(app):
    logout_user()
    return redirect(qualify_url(app))
