# -*- coding: UTF-8 -*-
# Copyright 2015 Luc Saffre
# This file is part of Lino Welfare.
#
# Lino Welfare is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Lino Welfare is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with Lino Welfare.  If not, see
# <http://www.gnu.org/licenses/>.


"""Table definitions for `lino_welfare.modlib.immersion`.

"""
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from lino.api import dd

from lino_welfare.modlib.isip.mixins import ContractBaseTable

from lino_welfare.modlib.integ.roles import IntegrationAgent, IntegrationStaff


class Goals(dd.Table):
    """
    """
    required_roles = dd.login_required(IntegrationStaff)
    model = 'immersion.Goal'
    column_names = 'name *'
    detail_layout = """
    id name
    ContractsByGoal
    """


class ContractTypes(dd.Table):
    """The default table for :class:`ContractType` instances.
    """
    required_roles = dd.login_required(IntegrationStaff)
    model = 'immersion.ContractType'
    column_names = 'name exam_policy template *'
    detail_layout = """
    id name
    exam_policy template overlap_group
    full_name
    ContractsByType
    """
    insert_layout = """
    name
    exam_policy
    """


class ContractDetail(dd.DetailLayout):
    box1 = """
    id:8 client:25 user:15 language:8
    type goal company contact_person contact_role
    applies_from applies_until exam_policy
    sector function
    reference_person printed
    date_decided date_issued date_ended ending:20
    responsibilities
    """

    right = """
    cal.EntriesByController
    cal.TasksByController
    """

    main = """
    box1:70 right:30
    """


class Contracts(ContractBaseTable):

    required_roles = dd.login_required(IntegrationAgent)
    model = 'immersion.Contract'
    column_names = 'id client company applies_from applies_until user type *'
    order_by = ['id']
    detail_layout = ContractDetail()
    insert_layout = """
    client
    company
    type goal
    """

    parameters = dict(
        type=models.ForeignKey(
            'immersion.ContractType', blank=True,
            verbose_name=_("Only immersion trainings of type")),
        **ContractBaseTable.parameters)

    params_layout = """
    user type start_date end_date observed_event
    company ending_success ending
    """

    @classmethod
    def get_request_queryset(cls, ar):
        qs = super(Contracts, cls).get_request_queryset(ar)
        pv = ar.param_values
        if pv.company:
            qs = qs.filter(company=pv.company)
        return qs


class ContractsByClient(Contracts):
    """
    """
    master_key = 'client'
    auto_fit_column_widths = True
    column_names = ('applies_from applies_until type '
                    'company contact_person user remark:20 *')


class ContractsByProvider(Contracts):
    master_key = 'company'
    column_names = 'client applies_from applies_until user type *'


class ContractsByPolicy(Contracts):
    master_key = 'exam_policy'


class ContractsByType(Contracts):
    master_key = 'type'
    column_names = "applies_from client user *"
    order_by = ["applies_from"]


class ContractsByGoal(Contracts):
    master_key = 'goal'
    column_names = "applies_from client user *"
    order_by = ["applies_from"]


class ContractsByEnding(Contracts):
    master_key = 'ending'



class MyContracts(Contracts):
    column_names = "applies_from client type company applies_until date_ended ending *"

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(MyContracts, self).param_defaults(ar, **kw)
        kw.update(user=ar.get_user())
        return kw


