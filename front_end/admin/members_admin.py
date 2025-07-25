from flask import render_template, flash, redirect

from front_end.admin.member_details_form import MemberDetailsForm
from front_end.admin.member_list_form import MemberListForm
from front_end.form_helpers import flash_errors, render_link
from globals.config import url_for_admin

class MaintainMembers:

    @staticmethod
    def list_members(status):

        form = MemberListForm()
        form.populate_member_list(status)
        return render_template('admin/member_list.html', form=form, render_link=render_link)

    @staticmethod
    def edit_member(member_id, from_form):
        form = MemberDetailsForm()
        form.member_id.data = member_id
        if form.validate_on_submit():
            if form.save.data:
                if form.save_member(member_id):
                    flash('member saved', 'success')
                    if from_form == 'add':
                        return redirect(url_for_admin('index'))
                    else:
                        return redirect(url_for_admin('members_list_' + from_form))
        elif form.errors:
            flash_errors(form)
        if not form.is_submitted():
            form.populate_member(member_id)
        return render_template('admin/member_details.html', form=form, render_link=render_link)

