from werkzeug.urls import url_parse
from flask import render_template, flash, redirect
from flask_login import current_user, login_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from globals.config import url_for_admin
from models.user import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

    def populate(self):
        pass


def admin_login(next_page):
    if current_user.is_authenticated:
        return redirect(url_for_admin('index'))
    form = LoginForm()
    if form.is_submitted():
        if form.validate_on_submit():
            user = User.get(username=form.username.data)
            if user is None or not user.check_password(form.password.data):
                flash('Invalid username or password', 'danger')
                return render_template('admin/login.html', title='Sign In', form=form)
            login_user(user, remember=form.remember_me.data)
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for_admin('index')
            else:
                next_page = (url_for_admin('index') + next_page).replace("//", "/")
            return redirect(next_page)
    else:
        form.populate()

    return render_template('admin/login.html', title='Sign In', form=form)


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


def admin_register():
    if current_user.is_authenticated:
        return redirect(url_for_admin('index'))
    form = RegistrationForm()
    if form.is_submitted():
        if form.validate_on_submit():
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            User.add(user)
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for_admin('admin/admin_login'))
    return render_template('admin/register.html', title='Register', form=form)


