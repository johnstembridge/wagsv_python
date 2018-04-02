from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, TextAreaField, SelectField, FieldList, FormField, DateField
from back_end.interface import get_venue_select_list, get_venue, save_venue, get_new_venue_id, get_courses_for_venue
from data_utilities import parse_date
from front_end.form_helpers import set_select_field
from models.news import News, NewsDay
from datetime import datetime


class NewsListForm(FlaskForm):
    news_item = SelectField(label='News Item')
    edit_news = SubmitField(label='Edit news item')
    add_news = SubmitField(label='Add news item')

    def populate_news_list(self):
        news = News()
        set_select_field(self.news_item, 'news item', news.news_select_choices(), '')


class NewsItemForm(FlaskForm):
    text = StringField(label='Text')
    link = StringField(label='url')


class NewsDayForm(FlaskForm):
    items = FieldList(FormField(NewsItemForm))
    date = DateField(label='date')
    orig_date = HiddenField()
    save = SubmitField(label='Save')

    def populate_news_day(self, news_date=None):
        if news_date is not None:
            news_date = news_date.replace('-', '/')
            news_day = News().get_news_day(news_date)
        else:
            news_day = NewsDay(date = datetime.date.today())

        self.date.data = parse_date(news_day.date)
        self.orig_date.data = parse_date(news_day.date)
        for i in range(5):
            if i < len(news_day.items):
                item = news_day.items[i]
            else:
                item = ('', '')
            item_form = NewsItemForm()
            item_form.link = item[0]
            item_form.text = item[1]
            self.items.append_entry(item_form)

    def save_news_day(self, news_date):
        date = self.date.data
        orig_date = self.orig_date.data
        items = []
        for item in self.items:
            if len(item.text.data) > 0:
                items.append((item.link.data, item.text.data))

        News.save_news(date, items)
        return True
