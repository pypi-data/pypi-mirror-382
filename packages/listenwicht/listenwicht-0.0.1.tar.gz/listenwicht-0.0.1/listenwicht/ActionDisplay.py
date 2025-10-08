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

import mailcoil
from .LWBaseAction import LWBaseAction
from .ReceivedMail import ReceivedMail
from .Enums import Processing

class ActionDisplay(LWBaseAction):
	def _process(self, filename: str):
		rxmail = ReceivedMail.from_filename(filename)
		print(f"Processing mail in {filename}")
		for rule in self._mailproc.rules:
			rxmail.reset()
			is_match = rule.matches(rxmail, verbose = True)
			print(f"Condition result: {'matched' if is_match else 'NOT matched'} for rule {rule}")
			if is_match:
				for (procmail, via) in rule.execute_actions(rxmail):
					serialized_mail = mailcoil.Email.serialize_from_email_message(procmail.mail)
					if self.args.deliver_mail:
						print(f"Rule match requests delivery, actually trying to deliver mail via {via}")
						dropoff = mailcoil.MailDropoff.parse_uri(via)
						dropoff.post(serialized_mail)
					else:
						print("Rule match requests delivery, but only printing mail:")
						print(serialized_mail.content)

	def run(self):
		for mailfile in self.args.mailfile:
			self._process(mailfile)
