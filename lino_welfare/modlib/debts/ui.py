# -*- coding: UTF-8 -*-
# Copyright 2012-2015 Luc Saffre
# License: BSD (see file COPYING for details)

"""
The :xfile:`ui.py` module for `lino_welfare.modlib.debts`.

"""

from __future__ import unicode_literals

import logging
logger = logging.getLogger(__name__)

import decimal

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy as pgettext

from lino.api import dd
from lino.core.constants import _handle_attr_name

from lino.modlib.accounts.choicelists import AccountTypes
from lino.modlib.users.mixins import ByUser

from lino_welfare.modlib.pcsw import models as pcsw


class Clients(pcsw.Clients):
    # ~ Black right-pointing triangle : Unicode number: U+25B6  HTML-code: &#9654;
    # ~ Black right-pointing pointer Unicode number: U+25BA HTML-code: &#9658;
    help_text = u"""Wie Kontakte --> Klienten, aber mit Kolonnen und Filterparametern für Schuldnerberatung."""
    required = dict(user_groups='debts')
    params_panel_hidden = True
    title = _("DM Clients")
    order_by = "last_name first_name id".split()
    allow_create = False  # see blog/2012/0922
    use_as_default_table = False
    column_names = "name_column:20 national_id:10 gsm:10 address_column email phone:10 id "

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(Clients, self).param_defaults(ar, **kw)
        kw.update(coached_by=ar.get_user())
        return kw


class Actors(dd.Table):
    required = dd.required(user_groups='debts', user_level='manager')
    #~ required_user_groups = ['debts']
    model = 'debts.Actor'
    column_names = "budget seqno partner header remark *"


class ActorsByBudget(Actors):
    """The table used to edit Actors in a Budget's detail.

    """
    required = dd.required(user_groups='debts')
    master_key = 'budget'
    column_names = "seqno partner header remark *"
    auto_fit_column_widths = True
    help_text = _("To be filled if there is more than one person involved.")


class ActorsByPartner(Actors):
    required = dd.required(user_groups='debts')
    master_key = 'partner'
    label = _("Is actor in these budgets:")
    editable = False


class BudgetDetail(dd.FormLayout):
    """
    Defines the Detail form of a :class:`Budget`.
    
    """
    main = "general entries1 entries2 summary_tab preview_tab"
    general = dd.Panel("""
    date partner id user
    intro
    ActorsByBudget
    """, label=_("General"))

    entries1 = dd.Panel("""
    ExpensesByBudget
    IncomesByBudget
    """, label=_("Expenses & Income"))

    entries2 = dd.Panel("""
    LiabilitiesByBudget
    AssetsByBudget
    """, label=_("Liabilities & Assets"))

    tmp_tab = """
    PrintExpensesByBudget
    PrintIncomesByBudget
    """

    summary_tab = dd.Panel("""
    summary1:30 summary2:40
    DistByBudget
    """, label=pgettext(u"debts", u"Summary"))

    summary1 = """
    ResultByBudget
    DebtsByBudget
    BailiffDebtsByBudget
    """
    summary2 = """
    conclusion:30x5
    dist_amount printed total_debt
    include_yearly_incomes print_empty_rows print_todos
    """

    preview_tab = dd.Panel("""
    data_box
    summary_box
    """, label=_("Preview"))

    #~ ExpensesSummaryByBudget IncomesSummaryByBudget
    #~ LiabilitiesSummaryByBudget AssetsSummaryByBudget

    #~ def setup_handle(self,h):
        #~ h.general.label = _("General")
        #~ h.entries1.label = _("Expenses & Income")
        #~ h.entries2.label = _("Liabilities & Assets")
        #~ h.summary_tab.label = pgettext(u"debts",u"Summary")
        #~ h.tmp_tab.label = _("Preview")


class Budgets(dd.Table):
    """
    Base class for lists of :class:`Budgets <Budget>`.
    Serves as base for :class:`MyBudgets` and :class:`BudgetsByPartner`,
    but is directly used by :menuselection:`Explorer --> Debts -->Budgets`.
    """
    model = 'debts.Budget'
    required = dd.required(user_groups='debts', user_level='manager')
    #~ required_user_groups = ['debts']
    detail_layout = BudgetDetail()
    insert_layout = """
    partner
    date user
    """

    @dd.constant()
    def spacer(self):
        return '<br/>'


class MyBudgets(Budgets, ByUser):
    required = dd.required(user_groups='debts')


class BudgetsByPartner(Budgets):
    master_key = 'partner'
    label = _("Is partner of these budgets:")
    required = dd.required(user_groups='debts')


#

class Entries(dd.Table):
    model = 'debts.Entry'
    required = dd.required(user_groups='debts', user_level='admin')

    #~ required_user_groups = ['debts']
    #~ required_user_level = UserLevels.manager


class EntriesByType(Entries):
    _account_type = None
    #~ required_user_level = None
    required = dd.required(user_groups='debts')

    @classmethod
    def get_known_values(self):  # 20130906
        return dict(account_type=self._account_type)

    @classmethod
    def get_actor_label(self):  # 20130906
        if self._account_type is not None:
            return self._account_type.text
        return self._label or self.__name__

    @classmethod
    def unused_class_init(self):
        super(EntriesByType, self).class_init()
        if self._account_type is not None:
            #~ self.label = self._account_type.text 20130906
            #~ print 20120411, unicode(self.label)
            self.known_values = dict(account_type=self._account_type)

    #~ @dd.chooser()
    #~ def account_choices(cls):
        #~ print '20120918 account_choices', account_type
        #~ return accounts.Account.objects.filter(type=cls._account_type)


class EntriesByAccount(Entries):
    master_key = 'account'


class EntriesByBudget(Entries):

    """
    Base class for the tables used to edit Entries by budget.
    """
    master_key = 'budget'
    column_names = "account description amount actor:10 periods:10 remark move_buttons:8 seqno todo id"
    hidden_columns = "seqno id"
    auto_fit_column_widths = True
    required = dd.required(user_groups='debts')
    #~ required_user_level = None
    order_by = ['seqno']


class ExpensesByBudget(EntriesByBudget, EntriesByType):
    _account_type = AccountTypes.expenses


class IncomesByBudget(EntriesByBudget, EntriesByType):
    _account_type = AccountTypes.incomes


class LiabilitiesByBudget(EntriesByBudget, EntriesByType):
    _account_type = AccountTypes.liabilities
    column_names = "account partner remark amount actor:10 bailiff distribute monthly_rate move_buttons:8 todo seqno id"


class AssetsByBudget(EntriesByBudget, EntriesByType):
    _account_type = AccountTypes.assets
    column_names = "account remark amount actor move_buttons:8 todo seqno id"


class PrintEntriesByBudget(dd.VirtualTable):
    """Base class for the printable tables of entries by budget
(:class:`PrintExpensesByBudget`, :class:`PrintIncomesByBudget`,
:class:`PrintLiabilitiesByBudget` and :class:`PrintAssetsByBudget`).
    
This is historically the first table that uses Lino's per-request
dynamic columns feature.

This feature means that a single table can have different "column
sets".  You must define a `get_handle_name` method which returns a
"handle name" for each request.  In you case if you want a column set
per user) you would add the user name to the default name::

    from lino.core.constants import _handle_attr_name

    class MyTable(...):

        @classmethod
        def get_handle_name(self, ar):
            hname = _handle_attr_name
            hname += ar.get_user().username
            return hname
    
TODO: more explnations....


    """
    slave_grid_format = 'html'
    _account_type = None

    @classmethod
    def get_actor_label(self):  # 20130906
        if self._account_type is not None:
            return self._account_type.text
        return self._label or self.__name__

    @classmethod
    def get_handle_name(self, ar):
        hname = _handle_attr_name
        if ar.master_instance is not None:
            #~ hname = super(PrintEntriesByBudget,self).get_handle_name(ar)
            hname += str(len(ar.master_instance.get_actors()))
        return hname

    @classmethod
    def get_column_names(self, ar):
        """
        Builds columns dynamically by request. Called once per UI handle.
        """
        if 'dynamic_amounts' in self.column_names:
            amounts = ''
            if ar.master_instance is not None:
                actors = ar.master_instance.get_actors()
                if len(actors) == 1:
                    amounts = 'amount0'
                else:
                    for i, a in enumerate(actors):
                        if i <= 4:  # amount4
                            amounts += 'amount' + str(i) + ' '
                    amounts += 'total '
            return self.column_names.replace('dynamic_amounts', amounts)
        return self.column_names

    @classmethod
    def override_column_headers(self, ar):
        d = dict()
        if ar.master_instance is not None:
            for i, a in enumerate(ar.master_instance.get_actors()):
                d['amount' + str(i)] = a.header
        return d

    class Row:

        def __init__(self, e):
            self.has_data = e.budget.print_empty_rows
            self.description = e.description
            self.periods = e.periods
            self.partner = e.partner
            self.bailiff = e.bailiff
            self.remarks = []
            self.account = e.account
            self.monthly_rate = e.monthly_rate
            #~ self.todos = [''] * len(e.budget.get_actors())
            self.todo = ''
            self.amounts = [decimal.Decimal(0)] * len(e.budget.get_actors())
            self.total = decimal.Decimal(0)
            self.collect(e)

        def matches(self, e):
            if e.partner != self.partner:
                return False
            if e.bailiff != self.bailiff:
                return False
            if e.account != self.account:
                return False
            if e.monthly_rate != self.monthly_rate:
                return False
            if e.periods != self.periods:
                return False
            if e.description != self.description:
                return False
            return True

        def collect(self, e):
            if e.actor is None:
                i = 0
            else:
                i = e.budget.get_actor_index(e.actor)
            amount = e.amount  # / e.periods
            #~ if amount != 0:
            if amount:
                self.has_data = True
                self.amounts[i] += amount
                self.total += amount
            if e.remark:
                self.remarks.append(e.remark)
            if self.todo:
                self.todo += ', '
            self.todo += e.todo
            return True

    @classmethod
    def get_data_rows(self, ar):
        """
        """
        budget = ar.master_instance
        if budget is None:
            return
        qs = budget.entry_set.filter(
            account__type=self._account_type).order_by('seqno')
        if ar.filter:
            qs = qs.filter(ar.filter)
        row = None
        for e in qs:
            if row is None:
                row = self.Row(e)
            elif row.matches(e):
                row.collect(e)
            else:
                if row.has_data:
                    yield row
                row = self.Row(e)
        if row is not None:
            if row.has_data:
                yield row

    @dd.virtualfield(dd.PriceField(_("Total")))
    def total(self, obj, ar):
        return obj.total / obj.periods

    @dd.displayfield(_("Description"))
    def full_description(self, obj, ar):
        desc = obj.description
        if len(obj.remarks) > 0:
            desc += ' (%s)' % ', '.join(obj.remarks)
        if obj.periods != 1:
            desc += " (%s / %s)" % (obj.total, obj.periods)
        return desc

    @dd.displayfield(_("Description"))
    def description(self, obj, ar):
        return obj.description

    @dd.displayfield(_("Remarks"))
    def remarks(self, obj, ar):
        return ', '.join(obj.remarks)

    @dd.displayfield(_("Yearly amount"))
    def yearly_amount(self, obj, ar):
        if obj.periods == 1:
            return ''
        if obj.periods == 12:
            return str(obj.total)
        return "%s / %s" % (obj.total, obj.periods)

    @dd.virtualfield(models.ForeignKey('contacts.Partner'))
    def partner(self, obj, ar):
        return obj.partner

    @dd.virtualfield(models.ForeignKey(
        'contacts.Company', verbose_name=_("Debt collection agency")))
    def bailiff(self, obj, ar):
        return obj.bailiff

    # TODO: generate amountN columns dynamically.

    @dd.virtualfield(dd.PriceField(_("Amount")))
    def amount0(self, obj, ar):
        return obj.amounts[0] / obj.periods

    @dd.virtualfield(dd.PriceField(_("Amount")))
    def amount1(self, obj, ar):
        return obj.amounts[1] / obj.periods

    @dd.virtualfield(dd.PriceField(_("Amount")))
    def amount2(self, obj, ar):
        return obj.amounts[2] / obj.periods

    @dd.virtualfield(dd.PriceField(_("Amount")))
    def amount3(self, obj, ar):
        return obj.amounts[3] / obj.periods

    @dd.virtualfield(dd.PriceField(_("Amount")))
    def amount4(self, obj, ar):
        return obj.amounts[4] / obj.periods

    @dd.virtualfield(dd.PriceField(_("Monthly rate")))
    def monthly_rate(self, obj, ar):
        return obj.monthly_rate


class PrintIncomesByBudget(PrintEntriesByBudget):
    _account_type = AccountTypes.incomes
    column_names = "full_description dynamic_amounts"


class PrintExpensesByBudget(PrintEntriesByBudget):
    _account_type = AccountTypes.expenses
    column_names = "description remarks yearly_amount dynamic_amounts"
    # column_names = "full_description dynamic_amounts"


class PrintLiabilitiesByBudget(PrintEntriesByBudget):
    _account_type = AccountTypes.liabilities
    column_names = "partner:20 remarks:20 monthly_rate dynamic_amounts"


class PrintAssetsByBudget(PrintEntriesByBudget):
    _account_type = AccountTypes.assets
    column_names = "full_description dynamic_amounts"

ENTRIES_BY_TYPE_TABLES = (
    PrintExpensesByBudget,
    PrintIncomesByBudget,
    # PrintLiabilitiesByBudget,
    PrintAssetsByBudget)


def entries_table_for_group(group):
    for t in ENTRIES_BY_TYPE_TABLES:
        if t._account_type == group.account_type:
            return t


if False:  # TODO: replace the above by selectable "table layouts"

    class TableLayout(dd.Choice):
        account_type = None
        layout_columns = None

    class TableLayouts(dd.ChoiceList):
        verbose_name = _("Table layout")
        item_class = TableLayout
        column_names = 'value name text columns'

        @dd.virtualfield(models.CharField(_("Columns"), max_length=20))
        def layout_columns(cls, choice, ar):
            return choice.layout_columns


#~ class EntriesSummaryByBudget(EntriesByBudget,EntriesByType):
    #~ """
    #~ """
    #~ order_by = ('account','partner', 'remark', 'seqno')
    #~ column_names = "summary_description amount1 amount2 amount3 total"
class SummaryTable(dd.VirtualTable):
    auto_fit_column_widths = True
    column_names = "desc amount"
    slave_grid_format = 'html'

    @dd.displayfield(_("Description"))
    def desc(self, row, ar):
        return row[0]

    @dd.virtualfield(dd.PriceField(_("Amount")))
    def amount(self, row, ar):
        return row[1]

    @classmethod
    def get_sum_text(self, ar):
        """
        Return the text to display on the totals row.
        """
        return self.label

    @classmethod
    def get_data_rows(self, ar):
        for row in self.get_summary_numbers(ar):
            if row[1]:  # don't show summary rows with value 0
                yield row


#~ class BudgetSummary(SummaryTable):
class ResultByBudget(SummaryTable):
    help_text = _("""Shows the Incomes & Expenses for this budget.""")
    label = _("Incomes & Expenses")
    required = dd.required(user_groups='debts')
    master = 'debts.Budget'

    @classmethod
    def get_summary_numbers(self, ar):
        budget = ar.master_instance
        if budget is None:
            return
        yield ["Monatliche Einkünfte", budget.sum('amount', 'I', periods=1)]
        if budget.include_yearly_incomes:
            yi = budget.sum('amount', 'I', periods=12)
            if yi:
                yield [
                    ("Jährliche Einkünfte (%s / 12)"
                     % dd.decfmt(yi * 12, places=2)),
                    yi]

        a = budget.sum('amount', 'I', exclude=dict(periods__in=(1, 12)))
        yield ["Einkünfte mit sonstiger Periodizität", a]

        yield ["Monatliche Ausgaben", -budget.sum('amount', 'E', periods=1)]
        yield ["Ausgaben mit sonstiger Periodizität",
               -budget.sum('amount', 'E', exclude=dict(periods__in=(1, 12)))]

        ye = budget.sum('amount', 'E', periods=12)
        if ye:
            yield [
                ("Monatliche Reserve für jährliche Ausgaben (%s / 12)"
                 % dd.decfmt(ye * 12, places=2)),
                -ye]

        #~ ye = budget.sum('amount','E',models.Q(periods__ne=1) & models.Q(periods__ne=12))
        #~ if ye:
            #~ yield [
              #~ u"Monatliche Reserve für sonstige periodische Ausgaben",
              #~ -ye]

        yield ["Raten der laufenden Kredite", -budget.sum('monthly_rate', 'L')]

    @classmethod
    def get_sum_text(self, ar):
        return "Restbetrag für Kredite und Zahlungsrückstände"


class DebtsByBudget(SummaryTable):
    label = _("Debts")
    required = dd.required(user_groups='debts')
    master = 'debts.Budget'
    bailiff_isnull = True

    @classmethod
    def get_summary_numbers(self, ar):
        budget = ar.master_instance
        if budget is None:
            return
        for grp in budget.account_groups('L'):
            for acc in grp.account_set.all():
                yield [_("%s (distributable)") % dd.babelattr(acc, 'name'),
                       budget.sum('amount', account=acc, distribute=True,
                                  bailiff__isnull=self.bailiff_isnull)]
                yield [dd.babelattr(acc, 'name'),
                       budget.sum('amount', account=acc, distribute=False,
                                  bailiff__isnull=self.bailiff_isnull)]
        #~ "Total Kredite / Schulden"


class BailiffDebtsByBudget(DebtsByBudget):
    label = _("Bailiff Debts")
    bailiff_isnull = False


class DistByBudget(EntriesByBudget):

    column_names = "partner description amount dist_perc dist_amount"
    filter = models.Q(distribute=True)
    label = _("Debts distribution")
    known_values = dict(account_type=AccountTypes.liabilities)
    slave_grid_format = 'html'
    help_text = _("""\
Répartition au marc-le-franc.
A table with one row per entry in Liabilities which has "distribute" checked,
proportionally distributing the `Distributable amount` among the debtors.
""")

    @classmethod
    def get_title_base(self, ar):
        return self.label

    @classmethod
    def get_data_rows(self, ar):
        budget = ar.master_instance
        if budget is None:
            return
        qs = self.get_request_queryset(ar)
        #~ fldnames = ['amount1','amount2','amount3']
        #~ sa = [models.Sum(n) for n in fldnames]
        total = decimal.Decimal(0)

        entries = []
        for e in qs.annotate(models.Sum('amount')):
            #~ assert e.periods is None
            total += e.amount__sum
            entries.append(e)

        for e in entries:
            e.dist_perc = 100 * e.amount / total
            #~ if e.dist_perc == 0:
                #~ e.dist_amount = decimal.Decimal(0)
            #~ else:
            e.dist_amount = budget.dist_amount * e.dist_perc / 100
            yield e

    @dd.virtualfield(dd.PriceField(_("%")))
    def dist_perc(self, row, ar):
        return row.dist_perc

    @dd.virtualfield(dd.PriceField(_("Monthly payback suggested")))
    def dist_amount(self, row, ar):
        return row.dist_amount

    @classmethod
    def override_column_headers(self, ar):
        d = dict()
        d.update(partner=_("Creditor"))
        d.update(amount=_("Debt"))
        return d

    @dd.displayfield(_("Description"))
    def description(self, obj, ar):
        desc = obj.description
        if obj.remark:
            desc += ' (%s)' % obj.remark
        return desc
            #~ return "%s (%s / %s)" % (obj.description,obj.total,obj.periods)
        #~ return obj.description

