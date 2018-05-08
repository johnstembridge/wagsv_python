from wags_admin import app
from front_end.admin.venues_admin import MaintainVenues


@app.route('/venues', methods=['GET', 'POST'])
def venues_main():
    return MaintainVenues.list_venues()


@app.route('/venues/<venue_id>', methods=['GET', 'POST'])
def edit_venue(venue_id):
    return MaintainVenues.edit_venue(venue_id)


@app.route('/venues/<venue_id>/courses/<course_id>', methods=['GET', 'POST'])
def edit_course(venue_id, course_id):
    return MaintainVenues.edit_course(venue_id, course_id)
