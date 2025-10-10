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

import uuid
import email.parser

class ReceivedMail():
	def __init__(self, content: bytes):
		self._content = content
		self._mail = None

	@property
	def mail(self):
		if self._mail is None:
			self._mail = email.parser.BytesParser().parsebytes(self._content)
		return self._mail

	def reset(self):
		self._mail = None

	def randomize_message_id(self):
		self.set_header("Message-ID", f"<{str(uuid.uuid4())}@listenwicht>")

	def rename_header(self, old_key: str, new_key: str):
		for value in self.mail.get_all(old_key, failobj = [ ]):
			self.add_header(new_key, value)
		self.remove_header(old_key)

	def remove_headers(self, keys: list[str]):
		for key in keys:
			self.remove_header(key)

	def remove_header(self, key: str):
		del self.mail[key]

	def add_header(self, key: str, value: str):
		self.mail[key] = value

	def set_header(self, key: str, value: str):
		self.remove_header(key)
		self.mail[key] = value

	def __getitem__(self, key: str):
		return self.mail[key]

	@classmethod
	def from_filename(cls, filename: str):
		with open(filename, "rb") as f:
			return cls(f.read())
