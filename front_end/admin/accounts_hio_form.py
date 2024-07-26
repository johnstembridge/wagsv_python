from back_end.data_utilities import html_unescape, html_escape
from back_end.interface import get_front_page_items, update_front_page
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField


class AccountsHioForm(FlaskForm):
    hole_in_one = StringField(label='Hole in one fund')
    submit_hole_in_one = SubmitField(label='Update')

    def populate(self, year):
        self.hole_in_one.data = html_unescape(get_front_page_items('hole_in_one_fund')['hole_in_one_fund'])

    def update_hole_in_one(self):
        hio = html_escape(self.hole_in_one.data)
        update_front_page({'hole_in_one_fund': hio})
        return True
