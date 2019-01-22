from werkzeug.urls import url_parse, url_unparse, url_join
from flask import render_template, flash, redirect, request
from flask_login import current_user, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from globals import config
from globals.enumerations import UserRole, MemberStatus
from models.wags_db import User, Role
from back_end.interface import get_member_by_email, get_user, save_user


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

    def populate(self):
        pass


def user_login(app, next_page):
    if current_user.is_authenticated:
        return redirect(config.adjust_url_for_https(app, next_page))
    form = LoginForm()
    if form.is_submitted():
        if form.validate_on_submit():
            user = get_user(user_name=form.username.data)
            if user is None or not user.check_password(form.password.data):
                flash('Invalid username or password', 'danger')
                return render_template('{}/login.html'.format(app), title='Sign In', form=form, app=app, url_for_app=config.url_for_app)
            # if app not in [role.role.name for role in user.roles]:
            #     flash('Sorry, you do not have {} access'.format(app))
            #     return redirect(config.adjust_url_for_https(app))
            login_user(user, remember=form.remember_me.data)
            if not next_page or url_parse(next_page).netloc != '':
                next_page = config.adjust_url_for_https(app)
            else:
                next_page = config.adjust_url_for_https(app, next_page)
            return redirect(next_page)
    else:
        form.populate()

    return render_template('{}/login.html'.format(app), title='Sign In', form=form, app=app,  url_for_app=config.url_for_app)


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = get_user(user_name=username.data)
        if user is not None:
            raise ValidationError('Please use a different username.')


def user_register(app):
    if current_user.is_authenticated:
        return redirect(config.adjust_url_for_https(app))
    form = RegistrationForm()
    if form.is_submitted():
        if form.validate_on_submit():
            member = get_member_by_email(form.email.data)
            if member:
                if member.status not in [MemberStatus.full_member, MemberStatus.overseas_member]:
                    flash('Sorry, you are not a current member')
                    return redirect(config.adjust_url_for_https(app))
                user = User(user_name=form.username.data, member_id=member.id)
                user.set_password(form.password.data)
                if app == 'user':
                    role = Role(role=UserRole.user)
                if app == 'admin':
                    role = Role(role=UserRole.admin)
                user.roles.append(role)
                save_user(user)
                flash('Congratulations, you are now a registered {}!'.format(app))
                return redirect(config.url_for_app(app, 'user_login'))
            else:
                flash('Cannot find your membership - please give your WAGS contact email address')
    return render_template('{}/register.html'.format(app), title='Register', form=form)


def user_logout(app):
    logout_user()
    return redirect(config.adjust_url_for_https(app))


def is_safe_url(target):
    ref_url = url_parse(request.host_url)
    test_url = url_parse(url_join(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc
