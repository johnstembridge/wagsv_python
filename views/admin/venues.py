from flask_login import login_required

from globals.decorators import role_required
from wags_admin import app
from front_end.admin.venues_admin import MaintainVenues


@app.route('/venues', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def venues_main():
    return MaintainVenues.list_venues()


@app.route('/venues/<int:venue_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_venue(venue_id):
    return MaintainVenues.edit_venue(venue_id)


@app.route('/venues/<int:venue_id>/courses/<int:course_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_course(venue_id, course_id):
    return MaintainVenues.edit_course(venue_id, course_id)
