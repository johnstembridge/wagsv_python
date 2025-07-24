from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, SelectField, FieldList, FormField
from wtforms.validators import InputRequired, Email

from back_end.data_utilities import fmt_date, fmt_curr, parse_date, parse_float
from back_end.interface import get_member_select_choices, save_member_details, get_member, get_member_account, \
    accounts_last_updated
from front_end.form_helpers import set_select_field
from globals import config
from globals.config import url_for_html


class EditMemberDetailsForm(FlaskForm):
    status = HiddenField()
    first_name = StringField(label='First Name', validators=[InputRequired()])
    last_name = StringField(label='Last Name', validators=[InputRequired()])
    email = StringField(label='Email', validators=[InputRequired(), Email("Invalid email address")])
    address = StringField(label='Address')
    post_code = StringField(label='Post Code')
    phone = StringField(label='Phone')
    club_membership = StringField(label='Club Membership')
    whs_handicap = StringField(label='WHS Handicap')
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
            'club_membership': self.club_membership.data,
            'whs_handicap': float(self.whs_handicap.data)
        }
        save_member_details(member_id, member)
        return True


class ShowMemberDetailsForm(FlaskForm):
    choose_member = SelectField(label='Choose Member', coerce=int)
    load = SubmitField(label='Load')
    status = StringField(label='Status')
    first_name = StringField(label='First Name')
    last_name = StringField(label='Last Name')
    email = StringField(label='Email')
    address = StringField(label='Address')
    post_code = StringField(label='Post Code')
    phone = StringField(label='Phone')
    club_membership = StringField(label='Club Membership')
    whs_handicap = StringField(label='WHS Handicap')
    mugshot = HiddenField()

    def populate_details(self, member_id):
        MemberDetails.populate(self, member_id)


class MemberDetails:

    @staticmethod
    def populate(form, member_id, edit=False):
        if not edit:
            set_select_field(form.choose_member, get_member_select_choices(), 'member', member_id)
        member = get_member(member_id)
        if member:
            player = member.player
            contact = member.contact
            form.status.data = member.status.name
            form.first_name.data = player.first_name
            form.last_name.data = player.last_name
            form.email.data = contact.email
            form.address.data = contact.address
            form.post_code.data = contact.post_code
            form.phone.data = contact.phone
            form.club_membership.data = member.club_membership
            form.whs_handicap.data = member.whs_handicap
            form.mugshot.data = url_for_html('pictures', 'mugshots', player.full_name().replace(' ', '_') + '.jpg')


class AccountItemForm(FlaskForm):
    date = StringField(label='Date')
    item = StringField(label='Item')
    debit = StringField(label='Debit')
    credit = StringField(label='Credit')


class ShowMemberAccountsForm(FlaskForm):
    title = StringField(label='Title')
    last_updated = StringField()
    balance = StringField(label='Balance')
    negative_balance = HiddenField(label='Negative Balance')
    items = FieldList(FormField(AccountItemForm))

    def populate_account(self, member_id, year):
        member = get_member(member_id)
        self.title.data = '{} - Account information {}'.format(member.player.full_name(), year)
        self.last_updated.data = fmt_date(accounts_last_updated(year))
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
        self.inc_bal_url.data = config.url_for_html('reports', str(year - 1), 'incexp.htm')
