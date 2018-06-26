from flask import render_template
from werkzeug.utils import redirect

from back_end.interface import get_member
from front_end.form_helpers import render_link
from front_end.user.member_details_form import EditMemberDetailsForm, ShowMemberDetailsForm, ShowMemberAccountsForm
from globals.config import url_for_user


class Members:

    @staticmethod
    def contact(member_id, edit=False):
        member = get_member(member_id)
        if edit:
            form = EditMemberDetailsForm()
        else:
            form = ShowMemberDetailsForm()
        if form.is_submitted():
            if form.save_details(member_id):
                #flash('Details saved', 'success')
                return redirect(url_for_user('edit_contact_details'))
        form.populate_details(member)
        if edit:
            return render_template('user/edit_member_details.html', form=form)
        else:
            return render_template('user/show_member_details.html', form=form)

    @staticmethod
    def select():
        pass

    @staticmethod
    def account(member_id, year):
        form = ShowMemberAccountsForm()
        form.populate_account(member_id, year)
        return render_template('user/account.html', form=form, year=year, render_link=render_link)
