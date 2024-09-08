from flask_wtf import FlaskForm
from wtforms import StringField, FieldList, FormField, HiddenField
from back_end.interface import all_members_account_balance, get_member, get_member_account, accounts_last_updated
from back_end.data_utilities import fmt_curr, parse_float, fmt_date, parse_date


class AccountsMemberBalancesItemForm(FlaskForm):
    member = StringField(label='Member')
    balance = StringField(label='Balance')
    negative_balance = HiddenField(label='Negative Balance')
    member_id = HiddenField(label='Member id')


class AccountsMemberBalancesForm(FlaskForm):
    year = StringField()
    last_updated = StringField()
    balances = FieldList(FormField(AccountsMemberBalancesItemForm))

    def populate(self, year):
        self.year.data = str(year)
        self.last_updated.data = fmt_date(accounts_last_updated(year))
        all = all_members_account_balance(year)
        for item in all.data:
            member_id = item[all.column_index('member_id')]
            if (get_member(member_id)).status.current_member():
                item_form = AccountsMemberBalancesItemForm()
                item_form.member = item[all.column_index('member')]
                balance = parse_float(item[all.column_index('balance')])
                item_form.balance = fmt_curr(balance)
                item_form.negative_balance = balance < 0
                item_form.member_id = member_id
                self.balances.append_entry(item_form)


class AccountItemForm(FlaskForm):
    date = StringField(label='Date')
    item = StringField(label='Item')
    debit = StringField(label='Debit')
    credit = StringField(label='Credit')


class ShowMemberAccountsForm(FlaskForm):
    year = StringField()
    last_updated = StringField()
    title = StringField(label='Title')
    balance = StringField(label='Balance')
    negative_balance = HiddenField(label='Negative Balance')
    items = FieldList(FormField(AccountItemForm))

    def populate(self, member_id, year):
        self.year.data = str(year)
        self.last_updated.data = fmt_date(accounts_last_updated(year))
        member = get_member(member_id)
        self.title.data = '{} - Transactions'.format(member.player.full_name())
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
