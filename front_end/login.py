from flask import render_template, flash, redirect
from flask_login import current_user, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from globals.config import url_for_app, qualify_url
from globals.enumerations import UserRole, MemberStatus
from globals.email import send_mail
from models.wags_db import User, Role
from back_end.interface import get_member_by_email, get_user, save_user


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

    def populate(self):
        pass


def user_login(wags_app, next_page, app=None):
    if current_user.is_authenticated:
        return redirect(qualify_url(wags_app, next_page))
    form = LoginForm()
    if form.is_submitted():
        if form.validate_on_submit():
            user = get_user(user_name=form.username.data)
            if user is None or not user.check_password(form.password.data):
                flash('Invalid username or password', 'danger')
                return render_template('{}/login.html'.format(wags_app), title='Sign In', form=form, wags_app=wags_app,
                                       url_for_app=url_for_app)
            # if wags_app not in [role.role.name for role in user.roles]:
            #     flash('Sorry, you do not have {} access'.format(wags_app))
            #     return redirect(qualify_url(wags_app))
            login_user(user, remember=form.remember_me.data)
            if not next_page:
                next_page = qualify_url(wags_app)
            else:
                next_page = qualify_url(wags_app, next_page)
            return redirect(next_page)
    else:
        form.populate()

    return render_template('{}/login.html'.format(wags_app), title='Sign In', form=form, wags_app=wags_app,
                           url_for_app=url_for_app)


def validate_username(self, username):
    user = get_user(user_name=username.data)
    if user is not None:
        if user.member.contact.email != self.email.data:
            raise ValidationError('Please use a different username.')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), validate_username])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


def user_register(wags_app, new=True):
    # Register user (new is True) or reset login
    if new and current_user.is_authenticated:
        return redirect(qualify_url(wags_app))
    form = RegistrationForm()
    form_title = 'Register' if new else 'Reset login details'
    if not new and not form.is_submitted():
        form.username.data = current_user.user_name
        form.email.data = current_user.member.contact.email
    else:
        if form.validate_on_submit():
            member = get_member_by_email(form.email.data)
            if member:
                if member.status not in [MemberStatus.full_member, MemberStatus.overseas_member]:
                    flash('Sorry, you are not a current member', 'danger')
                    return redirect(qualify_url(wags_app))
                if not member.user:
                    user = User(user_name=form.username.data, member_id=member.id)
                else:
                    user = member.user # get_user(member.user.id)
                    user.user_name = form.username.data
                user.set_password(form.password.data)
                role = Role(role=UserRole.admin) if wags_app == 'admin' else Role(role=UserRole.user)
                if role.role.value not in [r.role.value for r in user.roles]:
                    user.roles.append(role)
                save_user(user)
                if new:
                    flash('Congratulations, you are now a registered {}!'.format(wags_app), 'success')
                    return redirect(url_for_app(wags_app, 'user_login'))
                else:
                    flash('Login details reset'.format(wags_app), 'success')
                    return redirect(url_for_app(wags_app, 'members_area'))
            else:
                flash('Cannot find your membership - please give your WAGS contact email address')
    return render_template('{}/register.html'.format(wags_app), title=form_title, form=form)


def user_logout(wags_app):
    logout_user()
    return redirect(qualify_url(wags_app))


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField()


def user_reset_password_request(wags_app, app):
    if current_user.is_authenticated:
        return redirect(url_for_app( 'index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = get_member_by_email(form.email.data).user
        if user:
            expires = send_password_reset_email(user, app)
            message = 'Check your email for the instructions to reset your password'
            flash(message, 'success')
        else:
            flash('Email not recognised', 'danger')
        return redirect(url_for_app(wags_app, 'user_login'))
    return render_template('user/reset_password_request.html', title='Reset Password', form=form)


def send_password_reset_email(user, app):
    token, expires = user.get_reset_password_token(app)
    send_mail(to=user.member.contact.email,
              sender='admin@wags.org',
              subject='[WAGS] Reset Your Password',
              message=render_template('user/reset_password.txt',
                                      url_for_app=url_for_app,
                                      user=user,
                                      token=token,
                                      expires=expires)
              )


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField()


def user_reset_password(wags_app, app, token):
    if current_user.is_authenticated:
        return redirect(url_for_app(wags_app, 'index'))
    user = User.verify_reset_password_token(app, token)
    if not user:
        return redirect(url_for_app(wags_app, 'index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        save_user(user)
        flash('Your password has been reset', 'success')
        return redirect(url_for_app(wags_app, 'user_login'))
    return render_template('user/reset_password.html', form=form)
