from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, SelectField
from wtforms.validators import InputRequired, Email

from back_end.interface import get_member, get_current_members, get_member_select_list, get_new_member_id, save_member
from front_end.form_helpers import set_select_field
from globals.enumerations import MemberStatus


class MemberListForm(FlaskForm):
    member = SelectField(label='Member')
    edit_member = SubmitField(label='Edit member')
    add_member = SubmitField(label='Add member')

    def populate_member_list(self):
        set_select_field(self.member, 'member', get_member_select_list(), '')


class MemberDetailsForm(FlaskForm):
    member_id = StringField(label='Member Id')
    member_id_return = HiddenField(label='Member Id return')
    status = SelectField(label='Status', choices=MemberStatus.choices(), coerce=MemberStatus.coerce)
    first_name = StringField(label='First Name', validators=[InputRequired()])
    surname = StringField(label='Surname', validators=[InputRequired()])
    proposer = SelectField(label='Proposer', choices=[(c, c) for c in get_current_members().values()])
    email = StringField(label='Email', validators=[InputRequired(), Email("Invalid email address")])
    save = SubmitField(label='Save')

    def validate(self):
        new_member = self.member_id.data == 'new'
        self.member_id.data = self.member_id_return.data
        if not super(MemberDetailsForm, self).validate():
            return False
        result = True
        current_members = [n.lower() for n in  get_current_members().values()]
        name = self.first_name.data + ' ' + self.surname.data
        if new_member:
            if name.lower() in current_members:
                self.first_name.errors.append('{} is already a member'.format(name))
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
                      'home_email': ''
                      }
        else:
            member = get_member('membcode', member_id)
        self.member_id.data = member['membcode']
        self.member_id_return.data = member['membcode']
        self.status.data = MemberStatus(int(member['status']))
        self.first_name.data = member['salutation']
        self.surname.data = member['surname']
        self.proposer.data = member['proposer']
        self.email.data = member['home_email']

    def save_member(self, member_id):
        new_member = member_id == "new"
        if new_member:
            member_id = self.member_id_return.data
        errors = self.errors
        if len(errors) > 0:
            return False
        member = {
            'membcode': member_id,
            'salutation': self.first_name.data,
            'surname': self.surname.data,
            'status': str(self.status.data.value),
            'proposer': self.proposer.data,
            'home_email': self.email.data,
        }
        save_member(member)
        return True
