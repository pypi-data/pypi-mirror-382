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

import socket
import textwrap
import mailcoil
import listenwicht
from .ReceivedMail import ReceivedMail
from .MultiCommand import BaseAction
from .Configfile import Configfile
from .Mailprocessor import Mailprocessor

class LWBaseAction(BaseAction):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._config = Configfile(self.args.config_file)
		self._mailproc = Mailprocessor(self._config.mailing_lists)
		self._received_mail_parsing_loglvl = 1
		self._deliver_processed_mail = False

	def _debug_print(self, level: int, msg: str = ""):
		if self._received_mail_parsing_loglvl >= level:
			print(msg)

	def _process_received_mail(self, filename: str):
		rxmail = ReceivedMail.from_filename(filename)
		original_msg = mailcoil.Email.serialize_from_email_message(rxmail.mail)
		self._debug_print(1, f"Processing mail in {filename}")
		errors = [ ]
		successful_delivery_count = 0
		for mailing_list in self._mailproc.mailing_lists:
			rxmail.reset()
			match_result = mailing_list.matches(rxmail, verbose = (self._received_mail_parsing_loglvl >= 2))
			if match_result.all_conditions_pass:
				self._debug_print(2, "Condition result: All conditions pass.")
				for (procmail, via) in mailing_list.execute_actions(rxmail):
					serialized_mail = mailcoil.Email.serialize_from_email_message(procmail.mail)
					successful_delivery_count += 1
					if self._deliver_processed_mail:
						self._debug_print(1, f"Mailing list {mailing_list.name} action requires delivery for message from {original_msg.from_addr[1]} (\"{original_msg.subject}\"), attempting delivery via {via}")
						dropoff = mailcoil.MailDropoff.parse_uri(via)
						dropoff.post(serialized_mail)
					else:
						self._debug_print(2, f"Mailing list {mailing_list.name} action requires delivery for message from {original_msg.from_addr[1]} (\"{original_msg.subject}\"), but only printing:")
						self._debug_print(2, serialized_mail.content)
			elif match_result.match_error is not None:
				self._debug_print(1, f"Condition result in mailing list {mailing_list.name} from {original_msg.from_addr[1]} (\"{original_msg.subject}\"): condition verification error, bouncing \"{match_result.match_error}\"")
				errors.append(match_result.match_error)
			else:
				self._debug_print(2, f"Condition result in mailing list {mailing_list.name}: condition verification failed, silently discarding")
			self._debug_print(2)

		if len(errors) > 0:
			rxmail.reset()
			bounce_mail = self._create_bounce(errors, successful_delivery_count, original_msg)
			if self._deliver_processed_mail:
				dropoff = mailcoil.MailDropoff.parse_uri(self._config.bounces["via"])
				dropoff.post(bounce_mail.serialize())
			else:
				self._debug_print(2, "Would send the following bounce mail:")
				self._debug_print(2, bounce_mail.serialize().content)
		self._debug_print(2, "=" * 120)


	def _create_bounce(self, errors: list[str], successful_delivery_count: int, original_msg: "SerializedMessage"):
		hostname = socket.gethostname()
		text = textwrap.dedent(f"""\
		Hello, this is listenwicht v{listenwicht.VERSION} running on {hostname}.

		Unfortunately, your email with subject "{original_msg.subject or 'N/A'}" led to {len(errors)} error{"s" if (len(errors) != 1) else ""}:
		""")
		text += "\n".join(f" - {error}" for error in errors)
		text += "\n\n"
		if successful_delivery_count == 0:
			text += "Your message was NOT delivered to any recipient."
		else:
			text += "Your message was regardless delivered to {successful_delivery_count} mailing list{'s' if (successful_delivery_count != 1) else ''}."
		text += "\n\nIf you believe this message was created in error, please contact the administrator of this mailing list"
		if "admin_email" in self._config.bounces:
			text += f" at {self._config.bounces['admin_email']}"
		text += "."

		bounce = mailcoil.Email(from_address = mailcoil.MailAddress(name = self._config.bounces["from"][0], mail = self._config.bounces["from"][1]), subject = "Mailing list delivery failed", text = text)
		bounce.to(mailcoil.MailAddress(name = original_msg.from_addr[0], mail = original_msg.from_addr[1]))
		return bounce
