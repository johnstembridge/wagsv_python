from wags_admin import app
from front_end.admin.home import get_user_current_year
from front_end.admin import accounts_admin


@app.route('/accounts', methods=['GET', 'POST'])
def accounts_main():
    current_year = get_user_current_year()
    return accounts_admin.upload_file(current_year)


@app.route('/accounts/<year>/upload', methods=['GET', 'POST'])
def accounts_upload_file(year):
    return accounts_admin.upload_file(year)
