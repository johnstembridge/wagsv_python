from flask_login import login_required

from front_end.admin.help import WagsHelp
from globals.decorators import role_required
from front_end.admin.news_admin import MaintainNews
from wags_admin import app


@app.route('/help', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def list_help():
    return WagsHelp.list_help()


@app.route('/help/<subject>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def show_help(subject):
    return WagsHelp.show_help(subject)
