from flask import render_template, redirect, flash

from front_end.admin.member_details_form import MemberDetailsForm, MemberListForm
from front_end.form_helpers import flash_errors, render_link
from globals.config import url_for_admin


class MaintainMembers:

    @staticmethod
    def list_members():
        form = MemberListForm()
        if form.is_submitted():
            if form.add_member.data:
                return redirect(url_for_admin('edit_member', member_id=0))
            if form.edit_member.data:
                return redirect(url_for_admin('edit_member', member_id=form.member.data))
        form.populate_member_list()

        return render_template('admin/member_list.html', form=form, render_link=render_link)

    @staticmethod
    def edit_member(member_id):
        form = MemberDetailsForm()
        form.member_id.data = member_id
        if form.validate_on_submit():
            if form.save.data:
                if form.save_member(member_id):
                    flash('member saved', 'success')
                    return redirect(url_for_admin('members_main'))
        elif form.errors:
            flash_errors(form)
        if not form.is_submitted():
            form.populate_member(member_id)
        return render_template('admin/member_details.html', form=form, render_link=render_link)

