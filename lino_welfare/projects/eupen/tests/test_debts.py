# -*- coding: UTF-8 -*-
# Copyright 2015-2017 Luc Saffre
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

"""Some test cases for :mod:`lino_welfare.modlib.debts`.

How to run only this test::

  $ go welfare
  $ cd lino_welfare/projects/eupen
  $ python manage.py test tests.test_debts

"""

from __future__ import unicode_literals
from __future__ import print_function

import logging
logger = logging.getLogger(__name__)

import os
import json
from bs4 import BeautifulSoup


from lino.utils.djangotest import RemoteAuthTestCase
from lino.utils import AttrDict
from django.utils.datastructures import MultiValueDict

from django.conf import settings
from lino.modlib.users.choicelists import UserTypes
from lino.api.shell import countries, pcsw, users
from lino.api import rt
from lino.api.doctest import test_client


class DebtsTests(RemoteAuthTestCase):
    maxDiff = None
    # override_djangosite_settings = dict(use_java=True)

    def test01(self):
        # print("20180502 test_debts.test01()")

        # Member = rt.models.households.Member
        Household = rt.models.households.Household
        Person = rt.models.contacts.Person
        Genders = rt.models.system.Genders
        Budget = rt.models.debts.Budget
        Actor = rt.models.debts.Actor
        Entry = rt.models.debts.Entry
        
        def check_count(b, a, e):
            self.assertEqual(Budget.objects.count(), b)
            self.assertEqual(Actor.objects.count(), a)
            self.assertEqual(Entry.objects.count(), e)
        
        

        u = users.User(username='root',
                       user_type=UserTypes.admin,
                       language="en")
        u.save()
        # be = countries.Country(name="Belgium", isocode="BE")
        # be.save()
        # kw = dict()
        # # kw.update(card_number="123456789")
        # # kw.update(national_id="680601 053-29")
        # kw.update(id=116)
        # kw.update(first_name="Jean")
        # kw.update(middle_name="Jacques")
        # kw.update(last_name="Jeffin")
        # obj = pcsw.Client(**kw)
        # obj.full_clean()
        # obj.save()

        from lino_welfare.modlib.debts.fixtures.minimal import objects
        for o in objects():
            o.save()
        # from lino_xl.lib.households.fixtures.std import objects
        # for o in objects():
        #     o.save()

        # Reproduce ticket #521
        ar = rt.login('root')
        
        p1 = Person(first_name="A", last_name="A", gender=Genders.male)
        p1.save()
        p2 = Person(first_name="B", last_name="B", gender=Genders.female)
        p2.save()
        h = Household.create_household(ar, p1, p2, None)

        # The household has for whatever reason an empty member
        # entry. Lino should ignore this entry.
        h.add_member(None)

        check_count(0, 0, 0)
        
        b = Budget(partner=h, user=u)
        b.save()
        b.fill_defaults()
        # from django.utils.encoding import force_text
        # s = ' & '.join([force_text(a) for a in b.get_actors()])
        # s = '{0} & {1}'.format(*b.get_actors())
        # self.assertEqual(s, "Mr. & Mrs.")

        ##
        ## Reproduce ticket #159 ('NoneType' object is not iterable
        ## (after duplicating a budget)) and verify ticket #471
        ## (Become the author after duplicating a budget).
        ##
        
        self.assertEqual(b.user.username, 'root')
        self.assertEqual(b.id, 1)

        ou = users.User(username='other',
                        user_type=UserTypes.admin,
                        language="en")
        ou.save()
        ar = rt.login('other')

        check_count(1, 2, 44)
        
        new = b.duplicate.run_from_code(ar)
        self.assertEqual(new.user.username, 'other')
        self.assertEqual(new.id, 2)
        
        check_count(2, 4, 88)
        new = Budget.objects.get(pk=2)
        self.assertEqual(new.user.username, 'other')
       
        url = "/api/debts/Budgets/1?&an=duplicate&sr=1"
        dlg = []
        dlg.append((
            "This will create a copy of Budget 1 for A & B A-B Are you sure?",
            'yes'))
        dlg.append((
            'Duplicated Budget 1 for A & B A-B to Budget 3 for A & B A-B.',
            None))
        self.check_callback_dialog(self.client.get, 'other', url, dlg)

        check_count(3, 6, 132)

        new = Budget.objects.get(pk=3)
        self.assertEqual(new.user.username, 'other')
