#	listenwicht - Flexible Python-based mailing list daemon
#	Copyright (C) 2025-2025 Johannes Bauer
#
#	This file is part of listenwicht.
#
#	listenwicht is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	listenwicht is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with listenwicht; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#	Johannes Bauer <JohannesBauer@gmx.de>

import os
import sys
import contextlib
import subprocess
from .LWBaseAction import LWBaseAction

_SYSTEMD_TEMPLATE = """\
[Unit]
Description=listenwicht mailing list service
After=network-online.target

[Service]
Type=simple
Restart=always
StartLimitInterval=30
StartLimitBurst=3
ExecStart="${binary}" daemon --config-file "${config-file}" "${maildir}"
WorkingDirectory=${home}

[Install]
WantedBy=default.target
"""

class ActionSystemd(LWBaseAction):
	def run(self):
		systemd_unit_filename = os.path.expanduser("~/.local/share/systemd/user/listenwicht.service")

		if self.args.uninstall:
			subprocess.call([ "systemctl", "--user", "stop", "listenwicht" ])
			subprocess.call([ "systemctl", "--user", "disable", "listenwicht" ])
			with contextlib.suppress(FileNotFoundError):
				os.unlink(systemd_unit_filename)
			subprocess.call([ "systemctl", "--user", "daemon-reload" ])
		elif self.args.install:
			systemd_unit = _SYSTEMD_TEMPLATE
			replacements = {
				"binary": os.path.realpath(sys.argv[0]),
				"home": os.environ["HOME"],
				"config-file": os.path.realpath(self.args.config_file),
				"maildir": os.path.realpath(self.args.maildir),
			}
			for (repl_from, repl_to) in replacements.items():
				systemd_unit = systemd_unit.replace(f"${{{repl_from}}}", repl_to)
			with contextlib.suppress(FileExistsError):
				os.makedirs(os.path.dirname(systemd_unit_filename))
			with open(systemd_unit_filename, "w") as f:
				f.write(systemd_unit)
			subprocess.call([ "systemctl", "--user", "daemon-reload" ])
			subprocess.call([ "systemctl", "--user", "enable", "listenwicht" ])
			subprocess.call([ "systemctl", "--user", "start", "listenwicht" ])
