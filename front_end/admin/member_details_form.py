from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, SelectField, DateField
from wtforms.validators import InputRequired, Optional, Email
import datetime

from back_end.interface import get_member, get_member_select_choices, save_member, get_players_as_of, \
    get_members_as_players, get_player_by_name, member_account_balance
from back_end.data_utilities import fmt_curr, parse_float
from front_end.form_helpers import MySelectField, set_select_field
from globals.enumerations import MemberStatus, PlayerStatus, UserRole


class MemberListForm(FlaskForm):
    member = SelectField(label='Choose Member')
    edit_member = SubmitField(label='Edit member')
    add_member = SubmitField(label='Add member')

    def populate_member_list(self):
        set_select_field(self.member, get_member_select_choices(current=False), 'member')


class MemberDetailsForm(FlaskForm):
    member_id = HiddenField(label='Member Id')
    status = SelectField(label='Status', choices=MemberStatus.choices(), coerce=MemberStatus.coerce)
    first_name = StringField(label='First Name', validators=[InputRequired()])
    last_name = StringField(label='Last Name', validators=[InputRequired()])
    proposer = MySelectField(label='Proposer', coerce=int, validators=[Optional()])
    email = StringField(label='Email', validators=[InputRequired(), Email()])
    address = StringField(label='Address')
    post_code = StringField(label='Post Code')
    phone = StringField(label='Phone')
    club_membership = StringField(label='Club Membership')
    accepted_date = DateField(label='Accepted')
    handicap = StringField(label='Handicap')
    whs_handicap = StringField(label='WHS Handicap')
    as_of = DateField(label='as of', validators=[Optional()])
    access = SelectField(label='Access', choices=UserRole.choices(), coerce=UserRole.coerce)
    save = SubmitField(label='Save')
    account_balance = StringField(label='Account Balance')
    negative_balance = HiddenField(label='Negative Balance')
    member_id_return = HiddenField()
    name_return = HiddenField()
    status_return = HiddenField()
    handicap_return = HiddenField()

    def validate(self):
        new_member = self.member_id.data == 0
        self.member_id.data = self.member_id_return.data
        proposer = self.proposer.data if self.proposer.data else 0
        set_select_field(self.proposer, get_member_select_choices(), default_selection=proposer,
                         item_name='proposer')
        if not super(MemberDetailsForm, self).validate():
            return False
        result = True
        if new_member:
            current_members = [n.full_name().lower() for n in get_members_as_players()]
            name = self.first_name.data + ' ' + self.last_name.data
            if name.lower() in current_members:
                self.first_name.errors.append('{} is already a member'.format(name))
                result = False
            date = datetime.date.today()
            current_guests = [n.full_name().lower() for n in get_players_as_of(date, PlayerStatus.guest)]
            if not name.lower() in current_guests:
                self.first_name.errors.append('{} has not been a guest'.format(name))
                result = False
            else:
                player = get_player_by_name(name)
                self.handicap_return.data = player.handicaps[-1].handicap
                self.status_return.data = str(player.handicaps[-1].status.value)

        return result

    def populate_member(self, member_id):
        new_member = member_id == 0
        if new_member:
            self.first_name.data = 'new'
            self.last_name.data = 'member'
            self.status_return.data = MemberStatus.full_member.value
            self.handicap_return.data = 0
            set_select_field(self.proposer, get_member_select_choices(), item_name='proposer')
        else:
            member = get_member(member_id)
            proposer = member.proposer_id if member.proposer else 0
            set_select_field(self.proposer, get_member_select_choices(), default_selection=proposer, item_name='proposer')
            player = member.player
            contact = member.contact
            state = player.state_as_of(datetime.date.today())
            set_select_field(self.status, MemberStatus.choices(), default_selection=member.status)
            self.status_return.data = member.status.value
            self.first_name.data = player.first_name
            self.last_name.data = player.last_name
            self.name_return.data = self.first_name.data + ' ' + self.last_name.data
            self.email.data = contact.email
            self.address.data = contact.address
            self.post_code.data = contact.post_code
            self.phone.data = contact.phone
            self.club_membership.data = member.club_membership
            self.accepted_date.data = member.accepted_date()
            self.handicap_return.data = self.handicap.data = state.handicap
            self.as_of.data = state.date
            self.whs_handicap.data = member.whs_handicap
            role = member.user.roles[-1].role if member.user else UserRole.user
            set_select_field(self.access, UserRole.choices(), default_selection=role)
            balance = member_account_balance(member_id, datetime.date.today().year)
            self.account_balance.data = fmt_curr(balance)
            self.negative_balance.data = balance < 0

    def save_member(self, member_id):
        member = {
            'first_name': self.first_name.data,
            'last_name': self.last_name.data,
            'handicap': float(self.handicap.data or self.handicap_return.data),
            'status': self.status.data,
            'as_of': self.as_of.data,
            'proposer_id': self.proposer.data,
            'email': self.email.data,
            'address': self.address.data,
            'post_code': self.post_code.data,
            'phone': self.phone.data,
            'club_membership': self.club_membership.data,
            'whs_handicap': parse_float(self.whs_handicap.data),
            'accepted': self.accepted_date.data,
            'orig_name': self.name_return.data,
            'orig_status': int(self.status_return.data),
            'orig_handicap': float(self.handicap_return.data),
            'access': self.access.data
        }
        save_member(member_id, member)
        return True
