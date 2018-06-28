from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, SelectField, FieldList, FormField
from wtforms.validators import InputRequired, Email

from back_end.data_utilities import fmt_date, fmt_curr, parse_date, parse_float
from back_end.interface import get_member_select_choices, save_member_details, get_member, get_member_account
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

    def populate_details(self, member_id):
        MemberDetails.populate(self, member_id, edit=True)
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
    choose_member = SelectField(label='Choose Member', coerce=int)
    load = SubmitField(label='Load')
    first_name = StringField(label='First Name')
    last_name = StringField(label='Last Name')
    email = StringField(label='Email')
    address = StringField(label='Address')
    post_code = StringField(label='Post Code')
    phone = StringField(label='Phone')
    mugshot = HiddenField()

    def populate_details(self, member_id):
        MemberDetails.populate(self, member_id)
        

class MemberDetails:

    @staticmethod
    def populate(form, member_id, edit=False):
        if not edit:
            set_select_field_new(form.choose_member, get_member_select_choices(), None, member_id)
        member = get_member(member_id)
        if member:
            player = member.player
            contact = member.contact
            form.first_name.data = player.first_name
            form.last_name.data = player.last_name
            form.email.data = contact.email
            form.address.data = contact.address
            form.post_code.data = contact.post_code
            form.phone.data = contact.phone
            form.mugshot.data = "http://www.wags.org/pictures/mugshots/{}.jpg".format(player.first_name + '_' + player.last_name)


class AccountItemForm(FlaskForm):
    date = StringField(label='Date')
    item = StringField(label='Item')
    debit = StringField(label='Debit')
    credit = StringField(label='Credit')


class ShowMemberAccountsForm(FlaskForm):
    title = StringField(label='Title')
    balance = StringField(label='Balance')
    negative_balance = HiddenField(label='Negative Balance')
    items = FieldList(FormField(AccountItemForm))

    def populate_account(self, member_id, year):
        member = get_member(member_id)
        self.title.data = '{} - Account information {}'.format(member.player.full_name(), year)
        balance = 0
        account = get_member_account(member.player.full_name(), year)
        for item in account.rows():
            item_form = AccountItemForm()
            item_form.date = fmt_date(parse_date(item['date'], reverse=True))
            item_form.item = item['item']
            debit = parse_float(item['debit'])
            item_form.debit = fmt_curr(debit)
            credit = parse_float(item['credit'])
            item_form.credit = fmt_curr(credit)
            self.items.append_entry(item_form)
            balance += (credit or 0) - (debit or 0)

        self.balance.data = fmt_curr(balance)
        self.negative_balance.data = balance < 0


class MembersAreaForm(FlaskForm):
    year = HiddenField(label='Year')
    member_id = HiddenField(label='Member Id')
    player_id = HiddenField(label='Player Id')
    member_name = StringField(label='Member name')
    inc_bal_url = HiddenField(label='IncBalUrl')

    def populate(self, member_id, year):
        self.year.data = year
        self.member_id.data = member_id
        member = get_member(member_id)
        self.member_name.data = member.player.full_name()
        self.player_id.data = member.player_id
        self.inc_bal_url.data = 'http://www.wags.org/' + str(year - 1) + '/incexp.htm'
