# -*- coding: UTF-8 -*-
# Copyright 2012-2016 Luc Saffre
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

"""
Fills the Sectors table using the official data from
http://www.bcss.fgov.be/binaries/documentation/fr/documentation/general/lijst_van_sectoren_liste_des_secteurs.xls

"""
from builtins import next
from lino.api import dd
from django.conf import settings
from lino.utils import ucsv
from lino.core.utils import resolve_model
from os.path import join, dirname

GERMAN = []
GERMAN.append((17, 1, u'ÖSHZ', u'Öffentliche Sozialhilfezentren'))


def objects():

    Sector = resolve_model('cbss.Sector')

    fn = join(dirname(__file__), 'lijst_van_sectoren_liste_des_secteurs.csv')
    reader = ucsv.UnicodeReader(
        open(fn, 'r'), encoding='latin1', delimiter=';')

    headers = next(reader)
    if headers != [u'Sector', u'', u'verkorte naam', u'Omschrijving', u'Abréviation', u'Nom']:
        raise Exception("Invalid file format: %r" % headers)
    next(reader)  # ignore second header line
    code = None
    for row in reader:
        s0 = row[0].strip()
        s1 = row[1].strip()
        if s0 or s1:
            kw = {}
            if len(s0) > 0:
                code = int(s0)
            kw.update(code=code)
            if row[1]:
                kw.update(subcode=int(row[1]))
            kw.update(
                **dd.babelkw(
                    'name', de=row[5], fr=row[5], nl=row[3], en=row[5]))
            kw.update(
                **dd.babelkw(
                    'abbr', de=row[4], fr=row[4], nl=row[2], en=row[4]))
            yield Sector(**kw)

    info = settings.SITE.get_language_info('de')
    if info:
        for code, subcode, abbr, name in GERMAN:
            sect = Sector.objects.get(code=code, subcode=subcode)
            if info.index == 0:
                sect.abbr = abbr
                sect.name = name
            else:
                sect.abbr_de = abbr
                sect.name_de = name
            sect.save()

    # default value for SiteConfig.sector is "CPAS"
    #~ settings.SITE.site_config.sector = Sector.objects.get(code=17,subcode=1)
    #~ settings.SITE.site_config.save()
