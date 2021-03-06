# Copyright (C) 2016-2017 Teclib'

# This file is part of Armadito indicator.

# Armadito indicator is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Armadito indicator is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Armadito indicator.  If not, see <http://www.gnu.org/licenses/>.

from armadito import notifier, jrpc
from gi.repository import GObject as gobject
import enum
import sys
import random

class AntivirusState(enum.Enum):
    absent = 1
    not_working = 2
    not_up_to_date = 3
    working_and_up_to_date = 4
    
class AntivirusModel(notifier.Notifier):
    def __init__(self):
        super().__init__()
        self.state = AntivirusState.absent
        self.version = '<unknown>'
        self.update_timestamp = 0
        self._timeout_id = None
        self._error_count = 0
        self._conn = jrpc.Connection('\0/tmp/.armadito-daemon')
        self._conn.notify_property('connected', self._connection_listener)
        self._conn.map('notify_event', self._notify_event)

    def _on_timeout(self):
        try:
            self._conn.connect()
        except OSError as e:
            if self._error_count == 0:
                print(str(e))
            self._error_count += 1
            return True
        self._timeout_id = None
        return False

    def _start_timeout(self):
            self._timeout_id = gobject.timeout_add(1000, self._on_timeout)

    def _connection_listener(self, old_connected, connected):
        print("connected:", connected)
        if connected:
            self._conn.call("status", callback = self._status_cb)
            self.state = AntivirusState.not_working
        else:
            self.state = AntivirusState.absent
            if old_connected is True:
                self._error_count = 0
                self._start_timeout()
        
    def connect(self):
        try:
            self._conn.connect()
        except OSError as e:
            print(str(e))
            self._error_count = 0
            self._start_timeout()

    def _status_cb(self, info):
        self.version = info.antivirus_version
        self.update_timestamp = info.global_update_ts
        if info.global_status == 'A6O_UPDATE_OK':
            self.state = AntivirusState.working_and_up_to_date
        elif info.global_status == 'A6O_UPDATE_CRITICAL':
            self.state = AntivirusState.not_up_to_date

    def _notify_event(self, event):
        pass

    def _create_scan_id(self):
        random.seed()
        return random.randrange(sys.maxsize)
        
    def scan(self, path):
        scan_params = jrpc.MarshallObject()
        scan_params.root_path = path
        scan_params.recursive = 1
        scan_params.threaded = 1
        scan_params.send_progress = 1
        scan_params.scan_id = self._create_scan_id()
        print(scan_params.scan_id)
        self._conn.call('scan', params = scan_params)

