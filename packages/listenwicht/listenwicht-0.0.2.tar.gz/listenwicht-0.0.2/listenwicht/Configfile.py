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

import json

class Configfile():
	def __init__(self, filename: str):
		with open(filename) as f:
			self._config = json.load(f)

	@property
	def burst(self):
		return self._config.get("burst", {
			"event_count": 20,
			"window_secs": 1200,
		})

	@property
	def dropoff(self):
		return self._config["dropoff"]

	@property
	def bounces(self):
		return self._config["bounces"]

	@property
	def mailing_lists(self):
		return self._config.get("mailing_lists", [ ])
