# -*- coding: UTF-8 -*-
## Copyright 2013 Luc Saffre
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
This module contains "watch_tim" tests. 
You can run only these tests by issuing::

  python manage.py test pcsw.WatchTimTest
  
"""

from __future__ import unicode_literals


import logging
logger = logging.getLogger(__name__)

#~ from django.utils import unittest
#~ from django.test.client import Client
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import translation

#from lino.igen import models
#from lino.modlib.contacts.models import Contact, Companies
#from lino.modlib.countries.models import Country
#~ from lino.modlib.contacts.models import Companies


from lino import dd
from lino.utils import i2d
from lino.utils import babel
#~ from lino.core.modeltools import resolve_model
#Companies = resolve_model('contacts.Companies')
from lino.utils.test import TestCase

#~ Person = dd.resolve_model('contacts.Person')
#~ Property = dd.resolve_model('properties.Property')
#~ PersonProperty = dd.resolve_model('properties.PersonProperty')

#~ from lino.apps.pcsw.models import Person
#~ from lino.modlib.cv.models import PersonProperty
#~ from lino.modlib.properties.models import Property

from lino_welfare.modlib.pcsw.management.commands.watch_tim import process_line


POST_GEORGES = """{"method":"POST","alias":"PAR","id":"0000023633","time":"20130220 08:55:30",\
"user":"MELANIE","data":{"IDPAR":"0000023633","FIRME":"Schneider Georges","NAME2":"",\
"RUE":"","CP":"","IDPRT":"S","PAYS":"B","TEL":"","FAX":"","COMPTE1":"","NOTVA":"",\
"COMPTE3":"","IDPGP":"","DEBIT":"","CREDIT":"","ATTRIB":"N","IDMFC":"30","LANGUE":"D",\
"IDBUD":"","PROF":"80","CODE1":"","CODE2":"","CODE3":"",\
"DATCREA":{"__date__":{"year":2013,"month":2,"day":20}},"ALLO":"","NB1":"","NB2":"",\
"IDDEV":"","MEMO":"","COMPTE2":"","RUENUM":"","RUEBTE":"","DEBIT2":"","CREDIT2":"",\
"IMPDATE": {"__date__":{"year":0,"month":0,"day":0}},"ATTRIB2":"","CPTSYSI":"",\
"EMAIL":"","MVIDATE":{"__date__":{"year":0,"month":0,"day":0}},"IDUSR":"","DOMI1":""}}"""

PUT_MAX_MORITZ = """{"method":"PUT","alias":"PAR","id":"0000005088","time":"20130222 12:06:01",
"user":"MELANIE","data":{"IDPAR":"0000005088","FIRME":"Müller Max Moritz","NAME2":"",
"RUE":"Werthplatz 12","CP":"4700","IDPRT":"I","PAYS":"B","TEL":"","FAX":"",
"COMPTE1":"001-1234567-89","NOTVA":"BE-0999.999.999","COMPTE3":"","IDPGP":"",
"DEBIT":"","CREDIT":"","ATTRIB":"A","IDMFC":"","LANGUE":"D","IDBUD":"",
"PROF":"80","CODE1":"RH","CODE2":"","CODE3":"",
"DATCREA":{"__date__":{"year":1991,"month":8,"day":12}},
"ALLO":"Herr","NB1":"","NB2":"","IDDEV":"","MEMO":"","COMPTE2":"",
"RUENUM":"","RUEBTE":"","DEBIT2":"","CREDIT2":"",
"IMPDATE":{"__date__":{"year":1999,"month":5,"day":3}},"ATTRIB2":"",
"CPTSYSI":"","EMAIL":"","MVIDATE":{"__date__":{"year":0,"month":0,"day":0}},
"IDUSR":"ALICIA","DOMI1":""}}
"""

POST_PXS = """{"method":"POST","alias":"PXS","id":"0000023635","time":"20130222 11:07:42",
"user":"MELANIEL","data":{"IDPAR":"0000023635","NAME":"Heinz Hinz",
"GEBDAT":{"__date__":{"year":0,"month":0,"day":0}},"APOTHEKE":"","HILFE":"",
"ANTEIL":"","IDMUT":"","VOLLMACHT":{"__date__":{"year":0,"month":0,"day":0}},
"LAUFZEIT":{"__date__":{"year":0,"month":0,"day":0}},"DRINGEND":"","MONATLICH":"",
"SOZIAL":"","MIETE":"","MAF":"","REFERENZ":"","MEMO":"","SEXE":"","GENERIKA":"",
"IDPRT":"S","CARDNUMBER":"","VALID1":{"__date__":{"year":0,"month":0,"day":0}},
"VALID2":{"__date__":{"year":0,"month":0,"day":0}},"CARDTYPE":0,"NATIONALIT":"",
"BIRTHPLACE":"","NOBLECOND":"","CARDISSUER":""}}
"""

# // 2013-02-25 11:46:31 Exception("Cannot handle conversion from <class 'lino_welfare.modlib.pcsw.models.Household'> to <class 'lino_welfare.modlib.pcsw.models.Client'>",)
PUT_PAR_POTTER = """{"method":"PUT","alias":"PAR","id":"0000004260","time":"20130225 11:44:16",
"user":"WIL011","data":{"IDPAR":"0000004260","FIRME":"Voldemort-Potter Harald",
"NAME2":"","RUE":"Schilsweg 26","CP":"4700","IDPRT":"I","PAYS":"B","TEL":"","FAX":"","COMPTE1":"",
"NOTVA":"BE-0999.999.999","COMPTE3":"","IDPGP":"","DEBIT":"","CREDIT":"","ATTRIB":"A","IDMFC":"",
"LANGUE":"D","IDBUD":"","PROF":"80","CODE1":"ER","CODE2":"","CODE3":"",
"DATCREA":{"__date__":{"year":1985,"month":7,"day":23}},"ALLO":"Eheleute","NB1":"","NB2":"",
"IDDEV":"","MEMO":"","COMPTE2":"","RUENUM":"","RUEBTE":"","DEBIT2":"","CREDIT2":"",
"IMPDATE":{"__date__":{"year":2000,"month":6,"day":26}},"ATTRIB2":"","CPTSYSI":"","EMAIL":"",
"MVIDATE":{"__date__":{"year":0,"month":0,"day":0}},"IDUSR":"ALICIA","DOMI1":""}}
"""

#// 2013-02-25 12:00:37 Exception("Cannot handle conversion from <class 'lino_welfare.modlib.pcsw.models.Person'> to <class 'lino_welfare.modlib.pcsw.models.Household'>",)

PUT_PAR_6283 = """
{"method":"PUT","alias":"PAR","id":"0000006283","time":"20130225 11:52:56","user":"WIL011","data":
{"IDPAR":"0000006283","FIRME":"Willekens-Delanuit Paul","NAME2":"","RUE":"Rotenbergplatz","CP":"4700",
"IDPRT":"I","PAYS":"B","TEL":"","FAX":"","COMPTE1":"","NOTVA":"","COMPTE3":"","IDPGP":"",
"DEBIT":"","CREDIT":"","ATTRIB":"A","IDMFC":"","LANGUE":"D","IDBUD":"","PROF":"80","CODE1":"",
"CODE2":"","CODE3":"","DATCREA":{"__date__":{"year":1998,"month":11,"day":17}},
"ALLO":"Eheleute","NB1":"","NB2":"","IDDEV":"","MEMO":"","COMPTE2":"","RUENUM":"  24","RUEBTE":"",
"DEBIT2":"","CREDIT2":"","IMPDATE":{"__date__":{"year":1999,"month":8,"day":9}},
"ATTRIB2":"","CPTSYSI":"","EMAIL":"",
"MVIDATE":{"__date__":{"year":0,"month":0,"day":0}},"IDUSR":"","DOMI1":""}}
"""


"""
// 2013-02-26 12:05:13 ValidationError({'national_id': [u'Client with this National ID already exists.']})
{"method":"POST","alias":"PAR","id":"0000023624","time":"20130226 12:05:12","user":"MELANIEL",
"data":{"IDPAR":"0000023624","FIRME":"Van Beneden Fon","NAME2":"","RUE":"Bergstrasse",
"CP":"4700","IDPRT":"S","PAYS":"B","TEL":"","FAX":"","COMPTE1":"","NOTVA":"","COMPTE3":"",
"IDPGP":"","DEBIT":"","CREDIT":"","ATTRIB":"","IDMFC":"30","LANGUE":"D","IDBUD":"",
"PROF":"80","CODE1":"","CODE2":"","CODE3":"",
"DATCREA":{"__date__":{"year":2013,"month":2,"day":18}},"ALLO":"Frau",
"NB1":"VAFO940702","NB2":"940702 234-24","IDDEV":"","MEMO":"","COMPTE2":"",
"RUENUM":" 123","RUEBTE":"","DEBIT2":"","CREDIT2":"",
"IMPDATE":{"__date__":{"year":0,"month":0,"day":0}},
"ATTRIB2":"","CPTSYSI":"","EMAIL":"",
"MVIDATE":{"__date__":{"year":0,"month":0,"day":0}},"IDUSR":"WILMA","DOMI1":""}}
"""


User = dd.resolve_model('users.User')
Partner = dd.resolve_model('contacts.Partner')
Company = dd.resolve_model('contacts.Company')
Person = dd.resolve_model('contacts.Person')
Client = dd.resolve_model('pcsw.Client')
Coaching = dd.resolve_model('pcsw.Coaching')
Household = dd.resolve_model('households.Household')
households_Type = dd.resolve_model("households.Type")

class WatchTimTest(TestCase):
    pass
    #~ def setUp(self):
        #~ settings.LINO.never_build_site_cache = True
        #~ super(DemoTest,self).setUp()
            
  
def test00(self):
    User(username='watch_tim').save()
    User(username='alicia').save()
    User(username='roger').save()
    households_Type(name="Eheleute",pk=1).save()
    
def test01(self):
    """
    AttributeError 'NoneType' object has no attribute 'coaching_type'
    """
    self.assertDoesNotExist(Client,id=23633)
    process_line(POST_GEORGES)
    georges = Client.objects.get(id=23633)
    self.assertEqual(georges.first_name,"Georges")
    georges.first_name = "Peter"
    georges.save()
    process_line(POST_GEORGES)
    georges = Client.objects.get(id=23633)
    self.assertEqual(georges.first_name,"Georges")

def test02(self):
    """
    Company becomes Client
    
    ValidationError([u'A Partner cannot be parent for a Client']) (201302-22 12:42:07)
    A Partner in TIM has both `PAR->NoTva` and `PAR->IdUsr` filled. 
    It currently exists in Lino as a Company but not as a Client.
    `watch_tim` then must create a Client after creating also the intermediate Person.
    The Company child remains.
    """
    
    Company(name="Müller Max Moritz",id=5088).save()
    global PUT_MAX_MORITZ
    process_line(PUT_MAX_MORITZ)
    self.assertDoesNotExist(Company,id=5088)
    #~ company = Company.objects.get(id=5088) # has not been deleted
    person = Person.objects.get(id=5088) # has been created
    client = Client.objects.get(id=5088) # has been created
    coaching = Coaching.objects.get(client=client) # one coaching has been created
    self.assertEqual(person.first_name,"Max Moritz")
    self.assertEqual(client.first_name,"Max Moritz")
    self.assertEqual(coaching.user.username,'alicia')
    self.assertEqual(coaching.primary,True)
    self.assertEqual(coaching.start_date,i2d(19910812))
    
    """
    Client becomes Company
    """
    PUT_MAX_MORITZ = PUT_MAX_MORITZ.replace('"IDUSR":"ALICIA"','"IDUSR":""')
    process_line(PUT_MAX_MORITZ)
    company = Company.objects.get(id=5088) 
    self.assertDoesNotExist(Client,id=5088) # has been deleted
    self.assertDoesNotExist(Coaching,client_id=5088)
    

def test03(self):
    """
    Test whether watch_tim raises Exception 
    'Cannot create Client ... from PXS' when necessary.
    """
    self.assertDoesNotExist(Client,id=23635)
    try:
        process_line(POST_PXS)
        self.fail("Expected an exception")
    except Exception as e:
        self.assertEqual(str(e),"Cannot create Client 0000023635 from PXS")
    self.assertDoesNotExist(Client,id=23635)

def test04(self):
    """
    Household becomes Client
    """
    Household(name="Voldemort-Potter Harald",id=4260).save()
    process_line(PUT_PAR_POTTER)
    client = Client.objects.get(id=4260) # has been created
    self.assertDoesNotExist(Household,id=4260)
    coaching = Coaching.objects.get(client=client) # one coaching has been created
    self.assertEqual(client.first_name,"Harald")
    self.assertEqual(coaching.primary,True)
    self.assertEqual(coaching.user.username,'alicia')
    self.assertEqual(coaching.start_date,i2d(19850723))

def test05(self):
    """
    Person becomes Household 
    """
    Person(id=6283,first_name="Paul",last_name="Willekens-Delanuit").save()
    process_line(PUT_PAR_6283)
    household = Household.objects.get(id=6283) # has been created
    self.assertDoesNotExist(Person,id=6283)
      
def test06(self):
    """
    ValidationError {'first_name': [u'This field cannot be blank.']}
    """
    ln = """{"method":"PUT","alias":"PAR","id":"0000001334","time":"20121029 09:00:00",
    "user":"","data":{"IDPAR":"0000001334","FIRME":"Belgacom",
    "NAME2":"","RUE":"","CP":"1030","IDPRT":"V","PAYS":"B","TEL":"0800-44500",
    "FAX":"0800-11333","COMPTE1":"","NOTVA":"","COMPTE3":"","IDPGP":"",
    "DEBIT":"  2242.31","CREDIT":"","ATTRIB":"","IDMFC":"60","LANGUE":"F",
    "IDBUD":"","PROF":"30","CODE1":"","CODE2":"","CODE3":"",
    "DATCREA":{"__date__":{"year":1992,"month":10,"day":6}},"ALLO":"","NB1":"",
    "NB2":"","IDDEV":"","MEMO":"Foo bar","COMPTE2":"","RUENUM":"","RUEBTE":"",
    "DEBIT2":"   2242.31","CREDIT2":"",
    "IMPDATE":{"__date__":{"year":2012,"month":10,"day":24}},
    "ATTRIB2":"","CPTSYSI":"","EMAIL":"info@example.com",
    "MVIDATE":{"__date__":{"year":2012,"month":9,"day":9}},"IDUSR":"","DOMI1":""}}
    """
    self.assertDoesNotExist(Partner,id=1334)
    translation.deactivate_all()
    try:
        process_line(ln)
        self.fail("Expected a ValidationError")
    except ValidationError as e:
        self.assertEqual(str(e),"{'first_name': [u'This field cannot be blank.']}")
    self.assertDoesNotExist(Partner,id=1334)
    ln = ln.replace('"NOTVA":""','"NOTVA":"BE-0999.999.999"')
    process_line(ln)
    company = Company.objects.get(id=1334) 

def test07(self):
    """
    2013-02-28 10:05:41 ValueError('Cannot assign "u\'\'": "City.country" must be a "Country" instance.',)
    """
    ln = """{"method":"PUT","alias":"PAR","id":"0000023649","time":"20130228 10:05:41","user":"MELANIEL",
    "data":{"IDPAR":"0000023649","FIRME":"Reinders Denis","NAME2":"","RUE":"Sch<94>nefelderweg",
    "CP":"4700","IDPRT":"S","PAYS":"","TEL":"","FAX":"","COMPTE1":"","NOTVA":"","COMPTE3":"",
    "IDPGP":"","DEBIT":"","CREDIT":"","ATTRIB":"N","IDMFC":"30","LANGUE":"D","IDBUD":"",
    "PROF":"80","CODE1":"","CODE2":"","CODE3":"",
    "DATCREA":{"__date__":{"year":2013,"month":2,"day":28}},
    "ALLO":"Herr","NB1":"","NB2":"791228 123-35","IDDEV":"","MEMO":"","COMPTE2":"",
    "RUENUM":" 123","RUEBTE":"a","DEBIT2":"","CREDIT2":"",
    "IMPDATE":{"__date__":{"year":0,"month":0,"day":0}},"ATTRIB2":"","CPTSYSI":"","EMAIL":"",
    "MVIDATE":{"__date__":{"year":0,"month":0,"day":0}},"IDUSR":"","DOMI1":""}}
    """
    self.assertDoesNotExist(Client,id=23649)
    process_line(ln)
    obj = Client.objects.get(id=23649)
    self.assertEqual(obj.first_name,"Denis")