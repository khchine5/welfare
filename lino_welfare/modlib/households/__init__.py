# Copyright 2012-2014 Luc Saffre
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

# import datetime

from lino_xl.lib.households import Plugin


class Plugin(Plugin):

    extends_models = ['Household', 'Member']
    adult_age = 18
    """The age (in years) a person needs to have in order to be considered
    adult."""
    # adult_age = datetime.timedelta(days=18*365)
