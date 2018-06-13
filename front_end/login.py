from werkzeug.urls import url_parse
from flask import render_template, flash, redirect
from flask_login import current_user, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from globals.config import url_for
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
        return redirect(qualify_url(app, next_page))
    form = LoginForm()
    if form.is_submitted():
        if form.validate_on_submit():
            user = get_user(user_name=form.username.data)
            if user is None or not user.check_password(form.password.data):
                flash('Invalid username or password', 'danger')
                return render_template('{}/login.html'.format(app), title='Sign In', form=form)
            # if app not in [role.role.name for role in user.roles]:
            #     flash('Sorry, you do not have {} access'.format(app))
            #     return redirect(qualify_url(app))
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
        user = get_user(user_name=username.data)
        if user is not None:
            raise ValidationError('Please use a different username.')


def user_register(app):
    if current_user.is_authenticated:
        return redirect(qualify_url(app))
    form = RegistrationForm()
    if form.is_submitted():
        if form.validate_on_submit():
            member = get_member_by_email(form.email.data)
            if member:
                if member.status not in [MemberStatus.full_member, MemberStatus.overseas_member]:
                    flash('Sorry, you are not a current member')
                    return redirect(qualify_url(app))
                user = User(user_name=form.username.data, member_id=member.id)
                user.set_password(form.password.data)
                if app == 'user':
                    role = Role(role=UserRole.user)
                if app == 'admin':
                    role = Role(role=UserRole.admin)
                user.roles.append(role)
                save_user(user)
                flash('Congratulations, you are now a registered {}!'.format(app))
                return redirect(url_for(app, 'user_login'))
            else:
                flash('Cannot find your membership - please give your WAGS contact email address')
    return render_template('{}/register.html'.format(app), title='Register', form=form)


def qualify_url(app, page=None):
    return (url_for(app, 'index') + (page or '')).replace("//", "/")


def user_logout(app):
    logout_user()
    return redirect(qualify_url(app))
