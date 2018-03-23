from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, TextAreaField, SelectField, FieldList, FormField
from back_end.interface import get_member, \
    get_current_members  # , get_member_select_list, save_member, get_new_member_id
from front_end.form_helpers import set_select_field
from globals.enumerations import MemberStatus


class MemberListForm(FlaskForm):
    member = SelectField(label='member')
    edit_member = SubmitField(label='Edit member')
    add_member = SubmitField(label='Add member')
    editable = HiddenField(label='Editable')

    def populate_member_list(self):
        set_select_field(self.member, 'member', get_member_select_list(), '')
        self.editable = True


class MemberDetailsForm(FlaskForm):
    member_id = StringField(label='Member Id')
    status = SelectField(label='Status')
    first_name = StringField(label='First Name')
    surname = StringField(label='Surname')
    proposer = SelectField(label='Proposer')
    email = StringField(label='Email')
    editable = HiddenField(label='Editable')
    save = SubmitField(label='Save')

    def populate_member(self, member_id):
        self.editable.data = True
        member = get_member('membcode', member_id)
        self.member_id.data = member['membcode']
        set_select_field(self.status, 'status', [s.name for s in MemberStatus], MemberStatus(int(member['status'])).name)
        self.first_name.data = member['salutation']
        self.surname.data = member['surname']
        set_select_field(self.proposer, 'proposer', list(get_current_members().values()), member['proposer'])

        self.email.data = member['home_email']

    def save_member(self, member_id):
        errors = self.errors
        if len(errors) > 0:
            return False
        member = {
            'salutation': self.first_name.data,
            'surname': self.surname.data,
            'status': self.status.data,
            'proposer': self.proposer.data,
            'home_email': self.email.data,
        }
        if member_id == "0":
            member_id = str(get_new_member_id())

        save_member(member_id, member)
        return True
