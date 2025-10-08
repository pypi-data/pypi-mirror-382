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
import mailcoil
from .LWBaseAction import LWBaseAction
from .ReceivedMail import ReceivedMail
from .Enums import Processing

class ActionDaemon(LWBaseAction):
	@property
	def curdir(self):
		return os.path.realpath(self.args.maildir) + "/cur"

	@property
	def newdir(self):
		return os.path.realpath(self.args.maildir) + "/new"

	def _process(self, filename: str):
		rxmail = ReceivedMail.from_filename(filename)
		for rule in self._mailproc.rules:
			rxmail.reset()
			for (procmail, via) in rule.execute_if_matched(rxmail):
				print(f"Rule match {rule} for {filename} delivery via {via}")
				serialized_mail = mailcoil.Email.serialize_from_email_message(procmail.mail)
				dropoff = mailcoil.MailDropoff.parse_uri(via)
				try:
					dropoff.post(serialized_mail)
					print(f"Successfully delivered via {via}")
				except ConnectionRefusedError as e:
					print(f"Unable to deliver mail via {via} -- {e.__class__.__name__}: {str(e)}")

	def _process_spool_dir(self):
		for filename in os.listdir(self.newdir):
			new_filename = f"{self.newdir}/{filename}"
			if not os.path.isfile(new_filename):
				continue
			cur_filename = f"{self.curdir}/{filename}"
			self._process(new_filename)
			os.rename(new_filename, cur_filename)

	def run(self):
		if not os.path.isdir(self.newdir):
			raise NotADirectoryError(self.newdir)
		if not os.path.isdir(self.curdir):
			raise NotADirectoryError(self.curdir)

		self._process_spool_dir()
		while True:
			subprocess.run([ "inotifywait", "--event", "CREATE,MOVED_TO", self.newdir ], check = False, stderr = subprocess.DEVNULL, stdout = subprocess.DEVNULL)
			self._process_spool_dir()
