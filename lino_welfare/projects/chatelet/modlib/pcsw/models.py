# -*- coding: UTF-8 -*-
# Copyright 2014 Luc Saffre
# This file is part of the Lino Welfare project.
# Lino Welfare is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
# Lino Welfare is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with Lino Welfare; if not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals
from __future__ import print_function

import logging
logger = logging.getLogger(__name__)

from django.utils.translation import ugettext_lazy as _

from lino import dd

from lino_welfare.modlib.pcsw.models import *


class ClientDetail(dd.FormLayout):

    main = "general contact coaching aids_tab \
    work_tab career languages \
    competences contracts history calendar misc"

    general = dd.Panel("""
    overview:30 general2:40 general3:20 image:15
    reception.AppointmentsByPartner reception.CoachingsByClient courses.EnrolmentsByPupil
    """, label=_("Person"))

    general2 = """
    gender:10 id:10 nationality:15
    last_name declared_name
    first_name middle_name
    birth_date age:10 national_id:15
    civil_state birth_country birth_place
    """

    general3 = """
    language
    email
    phone
    fax
    gsm
    """

    contact = dd.Panel("""
    humanlinks.LinksByHuman:30
    households.MembersByPerson:20 households.SiblingsByPerson:50
    """, label=_("Family situation"))

    coaching = dd.Panel("""
    newcomers_left:20 newcomers.AvailableCoachesByClient:40
    pcsw.ContactsByClient:20 pcsw.CoachingsByClient:40
    """, label=_("Intervening parties"))

    suche = dd.Panel("""
    # job_office_contact job_agents
    pcsw.DispensesByClient:50x3
    pcsw.ExclusionsByClient:50x3
    """)

    papers = dd.Panel("""
    is_seeking unemployed_since work_permit_suspended_until
    needs_residence_permit needs_work_permit
    uploads.JobSearchUploadsByClient
    """)

    work_tab = dd.Panel("""
    suche:40  papers:40
    """, label=_("Job search"))

    aids_tab = dd.Panel("""
    in_belgium_since:15 residence_type residence_until group:16
    sepa.AccountsByClient uploads.MedicalUploadsByClient
    aids.GrantingsByClient
    """, label=_("Aids"))

    newcomers_left = dd.Panel("""
    workflow_buttons
    broker:12
    faculty:12
    refusal_reason
    """, required=dict(user_groups='newcomers'))

    #~ coaching_left = """
    #~ """
    history = dd.Panel("""
    # reception.CreateNoteActionsByClient:20
    notes.NotesByProject
    excerpts.ExcerptsByProject
    # lino.ChangesByMaster
    """, label=_("History"))

    calendar = dd.Panel("""
    # find_appointment
    # cal.EventsByProject
    cal.EventsByClient
    cal.TasksByProject
    """, label=_("Calendar"))

    misc = dd.Panel("""
    activity client_state noble_condition \
    unavailable_until:15 unavailable_why:30
    is_obsolete
    created modified
    remarks:30 contacts.RolesByPerson
    """, label=_("Miscellaneous"), required=dict(user_level='manager'))

    contracts = dd.Panel("""
    isip.ContractsByPerson
    jobs.CandidaturesByPerson
    jobs.ContractsByPerson
    """, label=_("Contracts"))

    languages = dd.Panel("""
    cv.LanguageKnowledgesByPerson
    """, label=_("Languages"))

    career = dd.Panel("career1 uploads.CareerUploadsByClient", label=_("Career"))
    career1 = """
    jobs.StudiesByPerson
    jobs.TrainingsByPerson
    jobs.ExperiencesByPerson:40
    """

    competences = dd.Panel(
        "good_panel bad_panel",
        label=_("Competences"),
        required=dict(user_groups='integ'))

    good_panel = """
    cv.SkillsByPerson cv.SoftSkillsByPerson
    badges.AwardsByHolder skills
    """

    bad_panel = """
    cv.ObstaclesByPerson
    obstacles
    """

Clients.detail_layout = ClientDetail()

cv = dd.resolve_app('cv')
cv.LanguageKnowledgesByPerson.column_names = "language native spoken \
written spoken_passively written_passively cef_level"

courses = dd.resolve_app('courses')
courses.EnrolmentsByPupil.column_names = 'request_date course remark \
workflow_buttons *'
