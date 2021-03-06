### Copyright (C) 2006-2009 Manuel Ospina <ospina.manuel@gmail.com>

# This file is part of rayuela.
#
# rayuela is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# rayuela is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with rayuela; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import sys

RAYUELA_DATA_DIR = os.path.join(sys.prefix, 'share')
# RAYUELA_GLADE_PATH = os.path.dirname(os.path.abspath(__file__))
RAYUELA_GLADE_PATH = os.path.join(RAYUELA_DATA_DIR, 'rayuela')
RAYUELA_GLADE_FILE = os.path.join(RAYUELA_GLADE_PATH, 'rayuela.glade')
