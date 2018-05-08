from front_end.admin.news_admin import MaintainNews
from wags_admin import app


@app.route('/news', methods=['GET', 'POST'])
def news_main():
    return MaintainNews.list_news()


@app.route('/news/<news_date>', methods=['GET', 'POST'])
def edit_news(news_date):
    return MaintainNews.edit_news(news_date)
