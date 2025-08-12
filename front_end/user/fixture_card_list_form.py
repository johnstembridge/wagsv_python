from flask_wtf import FlaskForm
from wtforms import StringField, FieldList, FormField
from globals.config import url_for_user, url_for_html
import os

class FixtureCardItemForm(FlaskForm):
    year = StringField()
    image_url = StringField()

class FixtureCardListForm(FlaskForm):
    card_list = FieldList(FormField(FixtureCardItemForm))

    def populate_card_list(self):
        path = url_for_html('pictures', 'fixture_cards')
        for file in os.listdir(path)[1:]:
            item_form = FixtureCardItemForm()
            year = file[-8:][:4]
            item_form.year.data = year
            item_form.image_url.data = url_for_html('pictures', 'fixture_cards', file)
            self.card_list.append_entry(item_form)
