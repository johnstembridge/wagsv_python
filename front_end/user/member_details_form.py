from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, SelectField
from wtforms.validators import InputRequired, Email

from back_end.interface import get_member_select_choices, save_member_details
from front_end.form_helpers import set_select_field, set_select_field_new


class MemberListForm(FlaskForm):
    member = SelectField(label='Choose Member')
    edit_member = SubmitField(label='Edit member')
    add_member = SubmitField(label='Add member')

    def populate_member_list(self):
        set_select_field(self.member, None, get_member_select_choices())


class EditMemberDetailsForm(FlaskForm):
    first_name = StringField(label='First Name', validators=[InputRequired()])
    last_name = StringField(label='Last Name', validators=[InputRequired()])
    email = StringField(label='Email', validators=[InputRequired(), Email("Invalid email address")])
    address = StringField(label='Address')
    post_code = StringField(label='Post Code')
    phone = StringField(label='Phone')
    member_id_return = HiddenField()
    mugshot = HiddenField()
    name_return = HiddenField()

    save = SubmitField(label='Save')

    def populate_details(self, member):
        MemberDetails.populate(self, member)
        self.name_return.data = self.first_name.data + ' ' + self.last_name.data

    def save_details(self, member_id):
        member = {
            'first_name': self.first_name.data,
            'last_name': self.last_name.data,
            'email': self.email.data,
            'address': self.address.data,
            'post_code': self.post_code.data,
            'phone': self.phone.data,
        }
        save_member_details(member_id, member)
        return True


class ShowMemberDetailsForm(FlaskForm):
    first_name = StringField(label='First Name')
    last_name = StringField(label='Last Name')
    email = StringField(label='Email')
    address = StringField(label='Address')
    post_code = StringField(label='Post Code')
    phone = StringField(label='Phone')
    mugshot = HiddenField()

    def populate_details(self, member):
        MemberDetails.populate(self, member)
        

class MemberDetails:

    @staticmethod
    def populate(form, member, edit=False):
        #set_select_field_new(self.proposer, get_member_select_choices(), default_selection=proposer, item_name='proposer')
        player = member.player
        contact = member.contact
        form.first_name.data = player.first_name
        form.last_name.data = player.last_name
        form.email.data = contact.email
        form.address.data = contact.address
        form.post_code.data = contact.post_code
        form.phone.data = contact.phone
        form.mugshot.data = "http://www.wags.org/pictures/mugshots/{}.jpg".format(player.first_name + '_' + player.last_name)
