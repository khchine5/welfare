# -*- coding: UTF-8 -*-
# Copyright 2012-2015 Luc Saffre
# License: BSD (see file COPYING for details)

"""
Database models for `lino_welfare.modlib.debts`.

"""

from __future__ import unicode_literals

from django.db import models

from lino.api import dd, _

from lino.modlib.accounts.choicelists import AccountTypes


class TableLayout(dd.Choice):
    # account_type = None
    columns_spec = None

    # def __init__(self, account_type, value, verbose_name, columns_spec):
    def __init__(self, value, verbose_name, columns_spec):
        # self.account_type = AccountTypes.items_dict[account_type]
        self.columns_spec = columns_spec
        # value = account_type + value
        super(TableLayout, self).__init__(value, verbose_name, None)


class TableLayouts(dd.ChoiceList):
    item_class = TableLayout
    verbose_name = _("Table layout")
    verbose_name_plural = _("Table layouts")
    column_names = 'value text columns_spec'

    @dd.virtualfield(models.CharField(_("Columns"), max_length=20))
    def columns_spec(cls, choice, ar):
        return choice.columns_spec

add = TableLayouts.add_item
add('10',  # used by PrintExpensesByBudget
    _("Description, remarks, yearly amount, actor amounts"),
    "description remarks yearly_amount:12 dynamic_amounts")

add('11',
    _("Description, remarks, actor amounts"),
    "description remarks dynamic_amounts")

add('20',  # used by PrintLiabilitiesByBudget
    _("Partner, remarks, monthly rate, actor amounts"),
    "partner:20 remarks:20 monthly_rate dynamic_amounts")

add('30',  # used by PrintAssetsByBudget, PrintIncomesByBudget
    _("Full description, actor amounts"),
    "full_description dynamic_amounts")

# add('I', '10',  # used by PrintAssetsByBudget, PrintIncomesByBudget
#     _("Full description, actor amounts"),
#     "full_description dynamic_amounts")
