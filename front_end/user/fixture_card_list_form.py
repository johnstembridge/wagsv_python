from flask_wtf import FlaskForm
from wtforms import StringField, FieldList, FormField, HiddenField
from globals import config
from globals.config import url_for_html
import os

class FixtureCardItemForm(FlaskForm):
    year = StringField()
    thumb_url = StringField()
    image_url = StringField()
    start_row = HiddenField()
    end_row = HiddenField()

class FixtureCardListForm(FlaskForm):
    card_list = FieldList(FormField(FixtureCardItemForm))

    def populate_card_list(self):
        path = os.path.join(config.get('locations')['pictures'], 'fixture_cards')
        files = sorted(os.listdir(path), reverse=True)
        count = 0
        for file in files[1:]:
            item_form = FixtureCardItemForm()
            year = file[-8:][:4]
            item_form.year.data = year
            item_form.thumb_url.data = url_for_html('pictures', 'fixture_cards', 'thumbs', file)
            item_form.image_url.data = url_for_html('pictures', 'fixture_cards', file)
            item_form.start_row = count%4 == 0
            item_form.end_row = (count+1)%4 == 0 or count == len(files)-2
            count += 1
            self.card_list.append_entry(item_form)
