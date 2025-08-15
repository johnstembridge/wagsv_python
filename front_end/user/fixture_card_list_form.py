from flask_wtf import FlaskForm
from wtforms import StringField, FieldList, FormField
from globals import config
import os

class FixtureCardItemForm(FlaskForm):
    year = StringField()
    image_url = StringField()

class FixtureCardListForm(FlaskForm):
    card_list = FieldList(FormField(FixtureCardItemForm))

    def populate_card_list(self):
        path = os.path.join(config.get('locations')['pictures'], 'fixture_cards')
        for file in os.listdir(path)[1:]:
            item_form = FixtureCardItemForm()
            year = file[-8:][:4]
            item_form.year.data = year
            item_form.image_url.data = os.path.join(path, file)
            self.card_list.append_entry(item_form)
