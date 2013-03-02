# -*- coding: UTF-8 -*-
## Copyright 2012 Luc Saffre
## This file is part of the Lino project.
## Lino is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
## Lino is distributed in the hope that it will be useful, 
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
## GNU General Public License for more details.
## You should have received a copy of the GNU General Public License
## along with Lino; if not, see <http://www.gnu.org/licenses/>.
"""

"""

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from lino.utils.xmlgen.cbss import tcs


class Command(BaseCommand):
    #~ args = '<user1>, ...'
    help = 'Tests whether the CBSS connection works.'

    def handle(self, *args, **options):
      
        req = tcs.build_request("hello cbss service")
        print "Sending request..."
        print tcs.execute('test',req,settings.SITE.cbss2_user_params)
      
