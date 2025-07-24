from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, SelectField, DateField
from wtforms.validators import InputRequired, Optional
import datetime

from back_end.interface import get_member, get_member_select_choices, save_member, get_players_as_of, \
    get_current_members_as_players, get_player_by_name, member_account_balance
from back_end.data_utilities import fmt_curr
from front_end.form_helpers import set_select_field
from globals.enumerations import MemberStatus


class MemberListForm(FlaskForm):
    member = SelectField(label='Choose Member')
    edit_member = SubmitField(label='Edit member')
    add_member = SubmitField(label='Add member')

    def populate_member_list(self):
        set_select_field(self.member, get_member_select_choices(current=False), 'member')


