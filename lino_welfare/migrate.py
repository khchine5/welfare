# -*- coding: UTF-8 -*-
# Copyright 2011-2015 Luc Saffre
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
This is a real-world example of how the application developer
can provide automatic data migrations for :ref:`dpy`.

This module is used because a :ref:`welfare`
Site has :setting:`migration_class` set to
``"lino_welfare.migrate.Migrator"``.

"""

import logging
logger = logging.getLogger(__name__)


import os
import datetime
from decimal import Decimal
from django.conf import settings
from lino.utils.dpy import Migrator
from lino.core.utils import resolve_model
from lino.api import dd, rt
from lino_cosi.lib.sepa.utils import belgian_nban_to_iban_bic
from lino_xl.lib.cal.choicelists import WORKDAYS


SINCE_ALWAYS = datetime.date(1990, 1, 1)


def noop(*args):
    return None


class Migrator(Migrator):
    "The standard migrator for :ref:`welfare`."
    def migrate_from_1_1_22(self, globals_dict):
        """- contenttypes.HelpText renamed to gfks.HelpText 

- Fields Partner.bic and Partner.iban no longer exist. Check whether
  sepa.Account exists.

        """

        globals_dict.update(contenttypes_HelpText=rt.modules.gfks.HelpText)

        if dd.is_installed('sepa'):
            self.sepa_accounts = []
            contacts_Partner = rt.modules.contacts.Partner

            def create_contacts_partner(id, modified, created, country_id, city_id, zip_code, region_id, addr1, street_prefix, street, street_no, street_box, addr2, name, language, email, url, phone, gsm, fax, remarks, is_obsolete, activity_id, client_contact_type_id, iban, bic):

                kw = dict()
                kw.update(id=id)
                kw.update(modified=modified)
                kw.update(created=created)
                kw.update(country_id=country_id)
                kw.update(city_id=city_id)
                kw.update(zip_code=zip_code)
                kw.update(region_id=region_id)
                kw.update(addr1=addr1)
                kw.update(street_prefix=street_prefix)
                kw.update(street=street)
                kw.update(street_no=street_no)
                kw.update(street_box=street_box)
                kw.update(addr2=addr2)
                kw.update(name=name)
                kw.update(language=language)
                kw.update(email=email)
                kw.update(url=url)
                kw.update(phone=phone)
                kw.update(gsm=gsm)
                kw.update(fax=fax)
                kw.update(remarks=remarks)
                kw.update(is_obsolete=is_obsolete)
                kw.update(activity_id=activity_id)
                kw.update(client_contact_type_id=client_contact_type_id)
                # kw.update(iban=iban)
                # kw.update(bic=bic)
                if iban:
                    self.sepa_accounts.append((id, bic, iban))
                return contacts_Partner(**kw)

            globals_dict.update(create_contacts_partner=create_contacts_partner)

            def check_sepa_accounts(loader):
                Account = rt.modules.sepa.Account
                for pk, bic, iban in self.sepa_accounts:
                    try:
                        Account.objects.get(partner_id=pk, bic=bic, iban=iban)
                    except Account.MultipleObjectsReturned:
                        pass
                    except Account.DoesNotExist:
                        obj = Account(partner_id=pk, bic=bic, iban=iban)
                        obj.full_clean()
                        obj.save()
                        logger.info("20150825 created %s for partner #%s",
                                    obj, pk)
            self.after_load(check_sepa_accounts)
        return '1.1.23'

    def migrate_from_1_1_24(self, globals_dict):
        """
- ignore ledger, finan, vatless and sepa
- migrate Client.is_seeking to Client.seeking_since
- separate ledger accounts from debts accounts
"""
        
        # no need to convert civil_state to new codification here (see
        # 20151013)

        # CivilState = rt.modules.pcsw.CivilState
        pcsw_Client = globals_dict['pcsw_Client']
        contacts_Person = globals_dict['contacts_Person']
        create_mti_child = globals_dict['create_mti_child']

        def create_pcsw_client(person_ptr_id, national_id,
                               nationality_id, card_number, card_valid_from,
                               card_valid_until, card_type, card_issuer, noble_condition,
                               group_id, birth_place, birth_country_id, civil_state,
                               residence_type, in_belgium_since, residence_until,
                               unemployed_since, needs_residence_permit, needs_work_permit,
                               work_permit_suspended_until, aid_type_id, declared_name,
                               is_seeking, unavailable_until, unavailable_why, obstacles,
                               skills, job_office_contact_id, client_state, refusal_reason,
                               remarks2, gesdos_id, tim_id, is_cpas, is_senior,
                               health_insurance_id, pharmacy_id, income_ag, income_wg,
                               income_kg, income_rente, income_misc, job_agents, broker_id,
                               faculty_id):

            if is_seeking:
                seeking_since = unemployed_since or settings.SITE.today()
            else:
                seeking_since = None

            return create_mti_child(contacts_Person, person_ptr_id,
                                    pcsw_Client,person_ptr_id=person_ptr_id,national_id=national_id,nationality_id=nationality_id,card_number=card_number,card_valid_from=card_valid_from,card_valid_until=card_valid_until,card_type=card_type,card_issuer=card_issuer,noble_condition=noble_condition,group_id=group_id,birth_place=birth_place,birth_country_id=birth_country_id,civil_state=civil_state,residence_type=residence_type,in_belgium_since=in_belgium_since,residence_until=residence_until,unemployed_since=unemployed_since,needs_residence_permit=needs_residence_permit,needs_work_permit=needs_work_permit,work_permit_suspended_until=work_permit_suspended_until,aid_type_id=aid_type_id,declared_name=declared_name,is_seeking=is_seeking,unavailable_until=unavailable_until,unavailable_why=unavailable_why,obstacles=obstacles,skills=skills,job_office_contact_id=job_office_contact_id,client_state=client_state,refusal_reason=refusal_reason,remarks2=remarks2,gesdos_id=gesdos_id,tim_id=tim_id,is_cpas=is_cpas,is_senior=is_senior,health_insurance_id=health_insurance_id,pharmacy_id=pharmacy_id,income_ag=income_ag,income_wg=income_wg,income_kg=income_kg,income_rente=income_rente,income_misc=income_misc,job_agents=job_agents,broker_id=broker_id,faculty_id=faculty_id, seeking_since=seeking_since)


        # def create_pcsw_client(person_ptr_id, national_id,
        #                        nationality_id, card_number, card_valid_from,
        #                        card_valid_until, card_type, card_issuer, noble_condition,
        #                        group_id, birth_place, birth_country_id, civil_state,
        #                        residence_type, in_belgium_since, residence_until,
        #                        unemployed_since, needs_residence_permit, needs_work_permit,
        #                        work_permit_suspended_until, aid_type_id, declared_name,
        #                        is_seeking, unavailable_until, unavailable_why, obstacles,
        #                        skills, job_office_contact_id, client_state, refusal_reason,
        #                        remarks2, gesdos_id, tim_id, is_cpas, is_senior,
        #                        health_insurance_id, pharmacy_id, income_ag, income_wg,
        #                        income_kg, income_rente, income_misc, job_agents, broker_id,
        #                        faculty_id):
        #     if civil_state:
        #         civil_state = CivilState.old2new(civil_state)
        #     return create_mti_child(contacts_Person,person_ptr_id,pcsw_Client,person_ptr_id=person_ptr_id,national_id=national_id,nationality_id=nationality_id,card_number=card_number,card_valid_from=card_valid_from,card_valid_until=card_valid_until,card_type=card_type,card_issuer=card_issuer,noble_condition=noble_condition,group_id=group_id,birth_place=birth_place,birth_country_id=birth_country_id,civil_state=civil_state,residence_type=residence_type,in_belgium_since=in_belgium_since,residence_until=residence_until,unemployed_since=unemployed_since,needs_residence_permit=needs_residence_permit,needs_work_permit=needs_work_permit,work_permit_suspended_until=work_permit_suspended_until,aid_type_id=aid_type_id,declared_name=declared_name,is_seeking=is_seeking,unavailable_until=unavailable_until,unavailable_why=unavailable_why,obstacles=obstacles,skills=skills,job_office_contact_id=job_office_contact_id,client_state=client_state,refusal_reason=refusal_reason,remarks2=remarks2,gesdos_id=gesdos_id,tim_id=tim_id,is_cpas=is_cpas,is_senior=is_senior,health_insurance_id=health_insurance_id,pharmacy_id=pharmacy_id,income_ag=income_ag,income_wg=income_wg,income_kg=income_kg,income_rente=income_rente,income_misc=income_misc,job_agents=job_agents,broker_id=broker_id,faculty_id=faculty_id)
        # globals_dict.update(create_mti_child=create_mti_child)

        globals_dict.update(create_ledger_movement=noop)
        globals_dict.update(create_vatless_accountinvoice=noop)
        globals_dict.update(create_vatless_invoiceitem=noop)
        globals_dict.update(create_finan_paymentorder=noop)
        globals_dict.update(create_finan_paymentorderitem=noop)
        globals_dict.update(create_finan_bankstatement=noop)
        globals_dict.update(create_finan_bankstatementitem=noop)
        globals_dict.update(create_finan_grouper=noop)
        globals_dict.update(create_finan_grouperitem=noop)
        globals_dict.update(create_finan_journalentry=noop)
        globals_dict.update(create_finan_journalentryitem=noop)
        globals_dict.update(create_sepa_movement=noop)
        globals_dict.update(create_sepa_statement=noop)
        globals_dict.update(create_ledger_voucher=noop)
        globals_dict.update(create_ledger_journal=noop)
        globals_dict.update(create_ledger_matchrule=noop)

        from lino_welfare.modlib.ledger.fixtures.std_journals import objects \
            as std_journals
        
        def after_load(loader):
            loader.save(std_journals())
        self.after_load(after_load)


        bv2kw = globals_dict['bv2kw']
        accounts_Group = rt.modules.accounts.Group
        accounts_Account = rt.modules.accounts.Account
        debts_Group = rt.modules.debts.Group
        debts_Account = rt.modules.debts.Account

        def create_accounts_group(id, name, chart, ref, account_type, entries_layout):
            kw = dict()
            kw.update(id=id)
            if name is not None: kw.update(bv2kw('name',name))
            kw.update(ref=ref)
            kw.update(account_type=account_type)
            if chart == 'debts':
                kw.update(entries_layout=entries_layout)
                return debts_Group(**kw)
            else:
                return accounts_Group(**kw)
        globals_dict.update(create_accounts_group=create_accounts_group)


        def create_accounts_account(id, ref, seqno, name, chart, group_id, type, sales_allowed, purchases_allowed, wages_allowed, clearings_allowed, clearable, required_for_household, required_for_person, periods, default_amount):

            kw = dict()
            kw.update(id=id)
            kw.update(ref=ref)
            kw.update(seqno=seqno)
            if name is not None: kw.update(bv2kw('name',name))
            # kw.update(chart=chart)
            kw.update(group_id=group_id)
            kw.update(type=type)
            if chart == 'debts':
                if periods is not None: periods = Decimal(periods)
                kw.update(periods=periods)
                if default_amount is not None: default_amount = Decimal(default_amount)
                kw.update(default_amount=default_amount)
                kw.update(required_for_household=required_for_household)
                kw.update(required_for_person=required_for_person)
                return debts_Account(**kw)
            else:
                kw.update(sales_allowed=sales_allowed)
                kw.update(purchases_allowed=purchases_allowed)
                kw.update(wages_allowed=wages_allowed)
                kw.update(clearings_allowed=clearings_allowed)
                kw.update(clearable=clearable)
                return accounts_Account(**kw)
        globals_dict.update(create_accounts_account=create_accounts_account)

        return '1.1.25'


    def migrate_from_1_1_25(self, globals_dict):
        """
- renamed PaymentInstruction to DisbursementOrder
"""
        
        ledger_Journal = rt.modules.ledger.Journal


        def create_ledger_journal(id, ref, build_method, template, seqno, name, trade_type, voucher_type, journal_group, auto_check_clearings, force_sequence, account_id, printed_name, dc):
            kw = dict()
            kw.update(id=id)
            kw.update(ref=ref)
            kw.update(build_method=build_method)
            kw.update(template=template)
            kw.update(seqno=seqno)
            if name is not None: kw.update(bv2kw('name',name))
            kw.update(trade_type=trade_type)
            if voucher_type == 'finan.PaymentInstructionsByJournal':
                voucher_type = 'finan.DisbursementOrdersByJournal'
            kw.update(voucher_type=voucher_type)
            kw.update(journal_group=journal_group)
            kw.update(auto_check_clearings=auto_check_clearings)
            kw.update(force_sequence=force_sequence)
            kw.update(account_id=account_id)
            if printed_name is not None: kw.update(bv2kw('printed_name',printed_name))
            kw.update(dc=dc)
            return ledger_Journal(**kw)
        globals_dict.update(create_ledger_journal=create_ledger_journal)

        globals_dict.update(create_ledger_voucher=noop)
        globals_dict.update(create_finan_bankstatement=noop)
        globals_dict.update(create_finan_journalentry=noop)
        globals_dict.update(create_finan_paymentorder=noop)
        globals_dict.update(create_vatless_accountinvoice=noop)

        return '1.1.26'
