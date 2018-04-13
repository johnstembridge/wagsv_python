from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, SelectField, FieldList, FormField, DateField, TextAreaField
from back_end.data_utilities import parse_date, encode_date
from back_end.interface import get_last_event, get_event, get_next_event
from front_end.form_helpers import set_select_field
from globals.config import url_for_old_service
from globals.enumerations import NewsItemType
from models.news import News, NewsDay, NewsItem
import datetime


class NewsListForm(FlaskForm):
    news_item = SelectField(label='News Item')
    edit_news = SubmitField(label='Edit news item')
    add_news = SubmitField(label='Add news item')

    def populate_news_list(self):
        news = News()
        set_select_field(self.news_item, 'news item', news.news_select_choices(), '')


class NewsItemForm(FlaskForm):
    text = StringField(label='Item')
    link = StringField(label='url')
    title = StringField(label='Title')


class NewsDayForm(FlaskForm):
    date = DateField(label='Date')
    is_new = HiddenField()
    items = FieldList(FormField(NewsItemForm))
    message = TextAreaField()
    item_to_add = SelectField(label='Item to add',
                              choices=NewsItemType.choices(),
                              coerce=NewsItemType.coerce)
    save = SubmitField()
    add_item = SubmitField(label='Add item')

    def populate_news_day(self, news_date):
        is_new = news_date == 'new'
        self.is_new.data = is_new
        if is_new:
            news_day = NewsDay(date=datetime.date.today())
            self.save.label.text = 'Publish'
        else:
            news_date = news_date.replace('-', '/')
            news_day = News().get_news_day(news_date)
            self.save.label.text = 'Save'
        self.date.data = parse_date(news_day.date)
        self.message.data = news_day.message
        for i in range(5):
            if i < len(news_day.items):
                item = news_day.items[i]
            else:
                item = NewsItem()
            item_form = NewsItemForm()
            item_form.text = item.text
            item_form.link = item.link
            item_form.title = item.title
            self.items.append_entry(item_form)

    def save_news_day(self, orig_date):
        date = self.date.data
        orig_date = orig_date.replace('-', '/')
        message = self.message.data
        items = []
        for item in self.items:
            if len(item.text.data) > 0:
                items.append((item.text.data, item.link.data, item.title.data))
        news_day = NewsDay(date, message, items)
        if self.is_new.data == 'True':
            News().publish_news_day(news_day)
            return 'published'
        else:
            News().save_news_day(news_day, orig_date=orig_date)
            return 'saved'

    def add_news_item(self):
        item_type = self.item_to_add.data
        year = datetime.date.today().year
        if item_type == NewsItemType.account_update:
            item = NewsItem(text='Accounts updated in members area', link='', title='')
        elif item_type == NewsItemType.handicap_update:
            item = NewsItem(text='Handicaps updated', link='/wagsuser/handicaps', title='show current handicaps')
        elif item_type == NewsItemType.event_result:
            event = get_event(*get_last_event())
            item = NewsItem(text='Results for {} updated'.format(event['venue']),
                            link='/wagsuser/events/{}/{}/results?event_type=1'.format(year, event['num']),
                            title='show results')
        elif item_type == NewsItemType.open_booking:
            event = get_event(*get_next_event())
            item = NewsItem(text='Booking now open for {} {}'.format(event['venue'], encode_date(event['date'])),
                            link='/wagsuser/events/{}/{}/book'.format(year, event['num']),
                            title='book now')
        else:
            return
        free = [ind for ind, item in enumerate(self.items.data) if item['text'] == '']
        if len(free) == 0:
            free = [len(self.items)]
            self.items.append_entry(NewsItemForm())
        self.items[free[0]].text.data = item.text
        self.items[free[0]].link.data = item.link
        self.items[free[0]].title.data = item.title
        if self.is_new.data == 'True':
            self.save.label.text = 'Publish'
