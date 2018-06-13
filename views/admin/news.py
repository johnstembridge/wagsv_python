from flask_login import login_required

from globals.decorators import role_required
from front_end.admin.news_admin import MaintainNews
from wags_admin import app


@app.route('/news', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def news_main():
    return MaintainNews.list_news()


@app.route('/news/<news_date>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_news(news_date):
    return MaintainNews.edit_news(news_date)
