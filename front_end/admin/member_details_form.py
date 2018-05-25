from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, SelectField, DateField, IntegerField
from wtforms.validators import InputRequired, Email
import datetime

from back_end.data_utilities import fmt_date, decode_member_address
from back_end.interface import get_member, get_current_members, get_member_select_list, save_member, \
    add_player, get_player_id, update_player_handicap,get_players, update_player_name, get_all_member_names
from back_end.interface_old import get_all_members
from front_end.form_helpers import set_select_field
from globals.enumerations import MemberStatus, PlayerStatus
from models.wags_db import Member


class MemberListForm(FlaskForm):
    member = SelectField(label='Choose Member')
    edit_member = SubmitField(label='Edit member')
    add_member = SubmitField(label='Add member')

    def populate_member_list(self):
        set_select_field(self.member, None, get_member_select_list())


class MemberDetailsForm(FlaskForm):
    member_id = StringField(label='Member Id')
    status = SelectField(label='Status', coerce=MemberStatus.coerce)
    first_name = StringField(label='First Name', validators=[InputRequired()])
    surname = StringField(label='Surname', validators=[InputRequired()])
    proposer = SelectField(label='Proposer')
    email = StringField(label='Email', validators=[InputRequired(), Email("Invalid email address")])
    address = StringField(label='Address')
    post_code = StringField(label='Post Code')
    phone = StringField(label='Phone')
    handicap = StringField(label='Handicap')
    as_of = DateField(label='as of')
    save = SubmitField(label='Save')
    member_id_return = HiddenField()

    def validate(self):
        new_member = self.member_id.data == 'new'
        self.member_id.data = self.member_id_return.data
        if not super(MemberDetailsForm, self).validate():
            return False
        result = True
        if new_member:
            current_members = [n.lower() for n in get_all_members()]
            name = self.first_name.data + ' ' + self.surname.data
            if name.lower() in current_members:
                self.first_name.errors.append('{} is already a member'.format(name))
                result = False
            date = fmt_date(datetime.date.today())
            current_guests = [n.lower() for n in get_players(date, PlayerStatus.guest)]
            if not name.lower() in current_guests:
                self.first_name.errors.append('{} has not been a guest'.format(name))
                result = False
        return result

    def populate_member(self, member_id):
        self.member_id_return.data = self.member_id.data = member_id
        new_member = member_id == "new"
        if new_member:
            member = Member()
            set_select_field(self.proposer, 'proposer', get_member_select_list())
        else:
            member = get_member(member_id)
            proposer = member.proposer.player.full_name() if member.proposer else ''
            set_select_field(self.proposer, 'proposer', get_member_select_list(), proposer)
            player = member.player
            contact = member.contact
            state = player.state_as_of(datetime.date.today())
            set_select_field(self.status, None, MemberStatus.choices(), member.status.value)
            self.first_name.data = player.first_name
            self.surname.data = player.last_name
            self.email.data = contact.email
            self.address.data = contact.address
            self.post_code.data = contact.post_code
            self.phone.data = contact.phone
            self.handicap.data = state.handicap
            self.as_of.data = state.date

    def save_member(self, member_id):
        new_member = member_id == "new"
        if new_member:
            member_id = self.member_id_return.data
        member = {
            'first_name': self.first_name.data,
            'last_name': self.surname.data,
            'status': self.status.data,
            'proposer': self.proposer.data,
            'email': self.email.data,
            'address': self.address.data,
            'post_code': self.post_code.data,
            'phone': self.phone.data,
        }
        save_member(member_id, member)

        # set player status and handicap
        name = self.first_name.data + ' ' + self.surname.data
        orig_name = self.name_return.data
        handicap = self.handicap.data
        player_id = get_player_id(name if new_member else orig_name)
        date = fmt_date(self.as_of.data)
        if player_id is None:
            add_player(name, handicap, PlayerStatus.member, date)
        if (not new_member) and name != orig_name:
            update_player_name(player_id, name)
        if new_member or \
                handicap != self.handicap_return.data or \
                (str(self.status.data.value)) != self.status_return.data:
            if self.status.data in [MemberStatus.full_member, MemberStatus.overseas_member]:
                status = PlayerStatus.member
            else:
                status = PlayerStatus.ex_member
            update_player_handicap(player_id, handicap, str(status.value), date)

        return True
