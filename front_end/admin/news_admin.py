from flask import render_template, redirect, flash

from front_end.admin.news_forms import NewsListForm, NewsDayForm
from front_end.form_helpers import render_link
from globals.config import url_for_admin


class MaintainNews:

    @staticmethod
    def list_news():
        form = NewsListForm()
        if form.is_submitted():
            if form.add_news.data:
                return redirect(url_for_admin('edit_news', news_date='new'))
            if form.edit_news.data:
                return redirect(url_for_admin('edit_news', news_date=form.news_item.data))
        form.populate_news_list()

        return render_template('admin/news_list.html', form=form, render_link=render_link)

    @staticmethod
    def edit_news(news_date):
        if news_date == '0':
            return redirect(url_for_admin('news_main'))
        form = NewsDayForm()
        if form.is_submitted():
            if form.save.data:
                m = form.save_news_day(news_date)
                if m:
                    flash('News ' + m, 'success')
                    return redirect(url_for_admin('news_main'))
            if form.add_item.data:
                form.add_news_item()
        else:
            form.populate_news_day(news_date)
        title = 'News ' + news_date
        return render_template('admin/news_day.html', title=title, form=form, render_link=render_link)
