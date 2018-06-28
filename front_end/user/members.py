from flask import render_template
from werkzeug.utils import redirect

from front_end.form_helpers import render_link
from front_end.user.members_form import EditMemberDetailsForm, ShowMemberDetailsForm, ShowMemberAccountsForm, \
    MembersAreaForm
from globals.config import url_for_user, url_for_wags_site


class Members:

    @staticmethod
    def contact(member_id, edit=False):
        if edit:
            form = EditMemberDetailsForm()
        else:
            form = ShowMemberDetailsForm()
        if form.is_submitted():
            if edit and form.save_details(member_id):
                #flash('Details saved', 'success')
                return redirect(url_for_user('edit_contact_details'))
            else:
                return redirect(url_for_user('show_contact_details', member_id=form.choose_member.data))
        form.populate_details(member_id)
        if edit:
            return render_template('user/edit_member_details.html', form=form)
        else:
            return render_template('user/show_member_details.html', form=form)

    @staticmethod
    def account(member_id, year):
        form = ShowMemberAccountsForm()
        form.populate_account(member_id, year)
        return render_template('user/account.html', form=form, year=year, render_link=render_link)

    @staticmethod
    def area(member_id, year):
        form = MembersAreaForm()
        form.populate(member_id, year)
        return render_template('user/member.html', form=form, year=year, render_link=render_link, url_for_wags_site=url_for_wags_site)
