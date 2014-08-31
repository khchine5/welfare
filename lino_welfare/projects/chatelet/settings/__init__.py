# -*- coding: UTF-8 -*-
# Copyright 2008-2014 Luc Saffre
# This file is part of the Lino project.
# Lino is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
# Lino is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with Lino; if not, see <http://www.gnu.org/licenses/>.

"""
The settings.py used for building both `/docs` and `/userdocs`
"""
from lino_welfare.projects.base import *


class Site(Site):

    title = "Lino pour CPAS"
    languages = 'fr nl'
    hidden_languages = None
    uppercase_last_name = True

    demo_fixtures = """std few_languages props all_countries
    demo cbss mini demo2 local """.split()

    migration_class = 'lino_welfare.projects.chatelet.migrate.Migrator'

    def get_apps_modifiers(self, **kw):
        kw = super(Site, self).get_apps_modifiers(**kw)
        kw.update(debts=None)  # remove whole app
        kw.update(sepa=None)  # remove whole app
        kw.update(iban=None)  # remove whole app
        # alternative implementations
        kw.update(courses='lino_welfare.projects.chatelet.modlib.courses')
        kw.update(pcsw='lino_welfare.projects.chatelet.modlib.pcsw')
        return kw

    # def setup_plugins(self):
    #     """
    #     Change the default value of certain plugin settings.

    #     """
    #     self.plugins.courses.configure(pupil_model='pcsw.Client')
    #     # self.plugins.courses.configure(teacher_model='users.User')
    #     super(Site, self).setup_plugins()

    # def get_default_language(self):
    #     return 'fr'

    def setup_choicelists(self):
        """
        This defines default user profiles for
        :mod:`lino_welfare.settings.chatelet`.
        """

        # must import it to activate workflows:
        from lino.modlib.courses import workflows

        from lino import dd
        from django.utils.translation import ugettext_lazy as _
        dd.UserProfiles.reset(
            '* office coaching integ courses cbss newcomers reception')
        add = dd.UserProfiles.add_item
        add('000', _("Anonymous"),                   '_ _ _ _ _ _ _ _',
            name='anonymous',
            readonly=True,
            authenticated=False)
        add('100', _("Integration Agent"),           'U U U U U U _ _')
        add('110', _("Integration Agent (Manager)"), 'U M M M M U _ _')
        add('200', _("Newcomers consultant"),        'U U U _ M U U _')
        add('210', _("Reception clerk"),             'U _ _ _ _ _ _ U')
        add('400', _("Social agent"),                'U U U _ U U _ _')
        add('410', _("Social agent (Manager)"),      'U M M _ M U _ _')
        add('900', _("Administrator"),               'A A A A A A A A',
            name='admin')

    def get_admin_main_items(self):

        # Mathieu: je remarque que le module "Visiteurs qui
        # m'attendent" ne fonctionne plus. Hors, c'est surtout ce
        # système qui est intéressant pour les travailleurs sociaux
        # qui attendent leurs rdv ou qui tiennent des permanences.

        yield self.modules.reception.MyWaitingVisitors
        yield self.modules.cal.MyEvents
        yield self.modules.cal.MyTasks
        
        yield self.modules.reception.WaitingVisitors
        yield self.modules.integ.UsersWithClients
        #~ yield self.modules.reception.ReceivedVisitors


# the following line should not be active in a checked-in version
#~ DATABASES['default']['NAME'] = ':memory:'
