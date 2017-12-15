from flask import render_template, redirect, url_for, flash
from venues_forms import VenueListForm, VenueDetailsForm
from utility import render_link


class MaintainVenues:

    @staticmethod
    def list_venues():
        form = VenueListForm()
        if form.is_submitted():
            if form.add_venue.data:
                return redirect(url_for('edit_venue', venue_id="0"))
            if form.edit_venue.data:
                return redirect(url_for('edit_venue', venue_id=form.venue.data))
        form.populate_venue_list()

        return render_template('venue_list.html', form=form, render_link=render_link)

    @staticmethod
    def edit_venue(venue_id):
        form = VenueDetailsForm()
        if form.is_submitted():
            if form.save_venue(venue_id):
                flash('Venue saved', 'success')
        if not form.is_submitted():
            form.populate_venue(venue_id)
        venue = venue_id if venue_id != "0" else "(new)"
        return render_template('venue_details.html', venue_id=venue, form=form, render_link=render_link)

