from flask import render_template, redirect, flash

from front_end.form_helpers import flash_errors, render_link
from .venues_forms import VenueListForm, VenueDetailsForm
from .course_details_form import CourseCardForm
from globals.config import url_for_admin


class MaintainVenues:

    @staticmethod
    def list_venues():
        form = VenueListForm()
        if form.is_submitted():
            if form.edit_venue.data and int(form.venue.data) > 0:
                return redirect(url_for_admin('edit_venue', venue_id=form.venue.data))
        if form.add_venue.data:
            return redirect(url_for_admin('edit_venue', venue_id="0"))
        form.populate_venue_list()

        return render_template('admin/venue_list.html', form=form, render_link=render_link)

    @staticmethod
    def edit_venue(venue_id):
        form = VenueDetailsForm()
        if form.is_submitted():
            if form.save.data or form.add_course.data or form.remove_course.data:
                if form.save_venue(venue_id):
                    flash('Venue saved', 'success')
                    return redirect(url_for_admin('venues_main'))
            if form.new_course.data:
                return redirect(url_for_admin('edit_course', venue_id=venue_id, course_id=0))
        if not form.is_submitted():
            form.populate_venue(venue_id)
        venue = venue_id if venue_id != 0 else "(new)"
        return render_template('admin/venue_details.html', venue_id=venue, form=form, render_link=render_link)

    @staticmethod
    def edit_course(venue_id, course_id):
        form = CourseCardForm()
        if form.validate_on_submit():
            add_new = False
            if form.add_new_card.data:
                add_new = True
            if form.save_course_card(venue_id, course_id, add_new):
                flash('card saved', 'success')
                return redirect(url_for_admin('edit_venue', venue_id=venue_id))
        elif form.errors:
            flash_errors(form)
        if not form.is_submitted():
            form.populate_card(course_id)
        return render_template('admin/course_card.html', form=form, render_link=render_link)
