from flask_wtf import FlaskForm
from wtforms import StringField, FieldList, FormField, HiddenField
from globals import config
from globals.config import url_for_html
import os

class FixtureCardItemForm(FlaskForm):
    year = StringField()
    image_url = StringField()
    new_row = HiddenField()

class FixtureCardListForm(FlaskForm):
    card_list = FieldList(FormField(FixtureCardItemForm))

    def populate_card_list(self):
        path = os.path.join(config.get('locations')['pictures'], 'fixture_cards')
        files = sorted(os.listdir(path), reverse=True)
        count = 0
        for file in files:
            item_form = FixtureCardItemForm()
            year = file[-8:][:4]
            item_form.year.data = year
            item_form.image_url.data = url_for_html('pictures', 'fixture_cards', file)
            item_form.new_row = "y" if count %3 == 0 else "n"
            self.card_list.append_entry(item_form)
