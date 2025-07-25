import datetime
from flask_wtf import FlaskForm
from wtforms import FieldList, FormField, StringField, HiddenField

from back_end.interface import get_all_members, get_members_as_players
from back_end.data_utilities import fmt_date, fmt_num



class MemberListItemForm(FlaskForm):
    member = StringField(label='Member')
    member_type = StringField(label='Type')
    handicap = StringField(label='Handicap')
    club = StringField(label='Club')
    whs_handicap = StringField(label='WHS')
    proposer = StringField(label='Proposer')
    accepted = StringField(label='Accepted')
    member_id = HiddenField(label='Member id')


class MemberListForm(FlaskForm):
    member_list = FieldList(FormField(MemberListItemForm))
    list_type = StringField(label='List type')

    def populate_member_list(self, status):
        current = status == 'current'
        self.list_type = 'current' if current else 'all'
        for player in get_members_as_players(current):
            member = player.member
            item_form = MemberListItemForm()
            item_form.member = member.player.full_name()
            item_form.member_type = member.status.name
            item_form.handicap = fmt_num(member.player.state_as_of(datetime.date.today()).handicap, 1)
            item_form.club = member.club_membership
            item_form.whs_handicap = fmt_num(member.whs_handicap, 1) if member.whs_handicap else ''
            item_form.proposer = member.proposer.player.full_name() if member.proposer else ''
            item_form.accepted = fmt_date(member.accepted) if member.accepted else ''
            item_form.member_id = member.id
            self.member_list.append_entry(item_form)
