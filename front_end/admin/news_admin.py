from flask import render_template, redirect, flash

from admin.news_forms import NewsListForm, NewsDayForm
from front_end.form_helpers import flash_errors
from front_end.utility import render_link
from globals.config import url_for_admin


class MaintainNews:

    @staticmethod
    def list_news():
        form = NewsListForm()
        if form.is_submitted():
            if form.add_news.data:
                return redirect(url_for_admin('edit_news', news_date=None))
            if form.edit_news.data:
                return redirect(url_for_admin('edit_news', news_date=form.news_item.data))
        form.populate_news_list()

        return render_template('admin/news_list.html', form=form, render_link=render_link)

    @staticmethod
    def edit_news(news_date):
        form = NewsDayForm()
        if form.is_submitted():
            if form.save.data:
                if form.save_news(news_date):
                    flash('News saved', 'success')
                    return redirect(url_for_admin('news_main'))
        else:
            form.populate_news_day(news_date)
        return render_template('admin/news_item.html', form=form, render_link=render_link)
