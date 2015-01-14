# -*- coding: UTF-8 -*-
# Copyright 2013-2015 Luc Saffre
# License: BSD (see file COPYING for details)

"""Recherche active d'emploi.

.. autosummary::
   :toctree:

    fixtures.demo
    models


"""

from lino import ad

from django.utils.translation import ugettext_lazy as _


class Plugin(ad.Plugin):
    verbose_name = _("Active Job Search")

    def setup_explorer_menu(self, site, profile, m):
        menugroup = site.plugins.integ
        m = m.add_menu(menugroup.app_label, menugroup.verbose_name)
        m.add_action('active_job_search.Proofs')