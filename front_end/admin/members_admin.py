from flask import render_template, redirect, flash

from front_end.admin.member_details_form import MemberDetailsForm, MemberListForm
from front_end.utility import render_link
from globals.config import url_for_admin


class MaintainMembers:

    @staticmethod
    def list_members():
        form = MemberListForm()
        if form.is_submitted():
            if form.add_member.data:
                return redirect(url_for_admin('edit_member', venue_id="0"))
            if form.edit_member.data:
                return redirect(url_for_admin('edit_member', venue_id=form.member.data))
        form.populate_member_list()

        return render_template('admin/member_list.html', form=form, render_link=render_link)

    @staticmethod
    def edit_member(member_id):
        form = MemberDetailsForm()
        if form.is_submitted():
            if form.save.data:
                if form.save_member(member_id):
                    flash('member saved', 'success')
                    return redirect(url_for_admin('members_main'))
            if form.add_course.data:
                return redirect(url_for_admin('edit_course', member_id=member_id, course_id=0))
        if not form.is_submitted():
            form.populate_member(member_id)
        member = member_id if member_id != "0" else "(new)"
        return render_template('admin/member_details.html', member_id=member, form=form, render_link=render_link)

