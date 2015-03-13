# -*- coding: UTF-8 -*-
# Copyright 2013-2015 Luc Saffre
# License: BSD (see file COPYING for details)

from lino.modlib.cal.fixtures.demo2 import objects as lino_objects
from lino.api import rt
from lino.utils import Cycler


def objects():
    ses = rt.login()
    Client = rt.modules.pcsw.Client
    CLIENTS = Cycler(Client.objects.all())
    for obj in lino_objects():
        if obj.__class__.__name__ == 'Event':
            if obj.event_type.invite_client:
                obj.project = CLIENTS.pop()
        yield obj
        obj.update_guests.run_from_code(ses)
