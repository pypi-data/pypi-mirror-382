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
import subprocess
from .LWBaseAction import LWBaseAction
from .BurstLimiter import BurstLimiter

class ActionDaemon(LWBaseAction):
	@property
	def curdir(self):
		return os.path.realpath(self.args.maildir) + "/cur"

	@property
	def newdir(self):
		return os.path.realpath(self.args.maildir) + "/new"

	def _process_spool_dir(self):
		for filename in os.listdir(self.newdir):
			new_filename = f"{self.newdir}/{filename}"
			if not os.path.isfile(new_filename):
				continue
			cur_filename = f"{self.curdir}/{filename}"
			try:
				self._process_received_mail(new_filename)
			finally:
				os.rename(new_filename, cur_filename)

	def run(self):
		self._deliver_processed_mail = True
		self._burst_limiter = BurstLimiter(event_count = self._config.burst["event_count"], window_secs = self._config.burst["window_secs"])

		if not os.path.isdir(self.newdir):
			raise NotADirectoryError(self.newdir)
		if not os.path.isdir(self.curdir):
			raise NotADirectoryError(self.curdir)

		print(f"Started listenwicht daemon, watching spool directory {self.newdir} for incoming messages")
		self._process_spool_dir()
		while True:
			subprocess.run([ "inotifywait", "--event", "CREATE,MOVED_TO", self.newdir ], check = False, stderr = subprocess.DEVNULL, stdout = subprocess.DEVNULL)
			self._process_spool_dir()
