from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, SelectField, DateField
from wtforms.validators import InputRequired, Email
import datetime

from back_end.data_utilities import fmt_date, encode_member_address, decode_member_address, parse_date, encode_date
from back_end.interface import get_member, get_current_members, get_member_select_list, get_new_member_id, save_member, \
    add_player, get_player_id, update_player_handicap, get_all_members, get_handicap_history, get_players, \
    update_player_name
from front_end.form_helpers import set_select_field
from globals.enumerations import MemberStatus, PlayerStatus


class MemberListForm(FlaskForm):
    member = SelectField(label='Member')
    edit_member = SubmitField(label='Edit member')
    add_member = SubmitField(label='Add member')

    def populate_member_list(self):
        set_select_field(self.member, 'member', get_member_select_list(), '')


class MemberDetailsForm(FlaskForm):
    member_id = StringField(label='Member Id')
    status = SelectField(label='Status', choices=MemberStatus.choices(), coerce=MemberStatus.coerce)
    first_name = StringField(label='First Name', validators=[InputRequired()])
    surname = StringField(label='Surname', validators=[InputRequired()])
    proposer = SelectField(label='Proposer', choices=[(c, c) for c in get_current_members().values()])
    email = StringField(label='Email', validators=[InputRequired(), Email("Invalid email address")])
    address = StringField(label='Address')
    post_code = StringField(label='Post Code')
    home_phone = StringField(label='Home Phone')
    mobile_phone = StringField(label='Mobile Phone')
    handicap = StringField(label='Handicap')
    as_of = DateField(label='as of')
    save = SubmitField(label='Save')
    member_id_return = HiddenField()
    status_return = HiddenField()
    handicap_return = HiddenField()
    name_return = HiddenField()

    def validate(self):
        new_member = self.member_id.data == 'new'
        if not new_member:
            self.proposer.choices = [(c, c) for c in get_all_members().values()]
        self.member_id.data = self.member_id_return.data
        if not super(MemberDetailsForm, self).validate():
            return False
        result = True
        if new_member:
            current_members = [n.lower() for n in get_current_members().values()]
            name = self.first_name.data + ' ' + self.surname.data
            if name.lower() in current_members:
                self.first_name.errors.append('{} is already a member'.format(name))
                result = False
            date = fmt_date(datetime.datetime.today().date())
            current_guests = [n.lower() for n in get_players(date, PlayerStatus.guest)]
            if not name.lower() in current_guests:
                self.first_name.errors.append('{} has not been a guest'.format(name))
                result = False
        return result

    def populate_member(self, member_id):
        new_member = member_id == "new"
        if new_member:
            member = {'membcode': get_new_member_id(),
                      'status': str(MemberStatus.full_member.value),
                      'salutation': '',
                      'surname': '',
                      'proposer': '',
                      'home_email': '',
                      'work_email': '',
                      'address': '',
                      'post_code': '',
                      'home_tel': '',
                      'mobile_tel': '',
                      'handicap': '28',
                      'as_of': datetime.datetime.today().date()
                      }
        else:
            member = get_member('membcode', member_id)
            player_id = get_player_id(member['salutation'] + ' ' + member['surname'])
            date = fmt_date(datetime.datetime.today().date())
            hist = get_handicap_history(player_id, date)
            member['handicap'] = hist[0][1]
            member['as_of'] = parse_date(hist[0][0])
        self.member_id_return.data = self.member_id.data = member['membcode']
        self.status_return.data = self.status.data = MemberStatus(int(member['status']))
        self.first_name.data = member['salutation']
        self.surname.data = member['surname']
        self.name_return.data = self.first_name.data + ' ' + self.surname.data
        if not new_member:
            self.proposer.choices = [(c, c) for c in get_all_members().values()]
        self.proposer.data = member['proposer']
        self.email.data = member['home_email'] if member['home_email'] != '' else member['work_email']
        self.address.data = encode_member_address(member)
        self.post_code.data = member['post_code']
        self.home_phone.data = member['home_tel']
        self.mobile_phone.data = member['mobile_tel']
        self.handicap_return.data = self.handicap.data = member['handicap']
        self.as_of.data = member['as_of']

    def save_member(self, member_id):
        new_member = member_id == "new"
        if new_member:
            member_id = self.member_id_return.data
        member = {
            'membcode': member_id,
            'salutation': self.first_name.data,
            'surname': self.surname.data,
            'status': str(self.status.data.value),
            'proposer': self.proposer.data,
            'home_email': self.email.data,
            'post_code': self.post_code.data,
            'home_tel': self.home_phone.data,
            'mobile_tel': self.mobile_phone.data
        }
        decode_member_address(self.address.data, member)
        save_member(member)

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
