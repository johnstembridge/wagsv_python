from flask import render_template, flash

from front_end.form_helpers import render_link
from globals.config import url_for_admin
from .accounts_hio_form import AccountsHioForm
from .accounts_upload_form import AccountsUploadForm
from .accounts_member_accounts_form import AccountsMemberBalancesForm, ShowMemberAccountsForm


def upload_file(year):
    form = AccountsUploadForm()
    if form.is_submitted():
        if form.submit_upload.data:
            if form.upload(year):
                flash('file uploaded successfully', 'success')
                # return redirect(url_for_admin('upload_file', year=year))
    else:
        return render_template('admin/accounts_upload.html', form=form, year=year, url_for_admin=url_for_admin,
                               render_link=render_link)


def hole_in_one(year):
    form = AccountsHioForm()
    if form.is_submitted():
        if form.submit_hole_in_one.data:
            if form.update_hole_in_one():
                flash('Hole in one fund updated successfully', 'success')
    else:
        return render_template('admin/accounts_hio.html', form=form, year=year, url_for_admin=url_for_admin,
                               render_link=render_link)


def accounts_member_balances(year):
    form = AccountsMemberBalancesForm()
    form.populate(int(year))
    return render_template('admin/account_balances.html', form=form, year=year, render_link=render_link,
                           url_for_admin=url_for_admin)


def member_account(member_id,year):
    form = ShowMemberAccountsForm()
    form.populate(member_id, year)
    return render_template('admin/member_account.html', form=form, year=year, render_link=render_link,
                           url_for_admin=url_for_admin)
