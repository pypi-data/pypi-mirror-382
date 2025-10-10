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

import time
import math

class BurstLimiter():
	def __init__(self, event_count: int, window_secs: float):
		self._event_count = event_count
		self._window_secs = window_secs
		self._bucket_fill = self._event_count
		self._last_fill = time.monotonic()
		self._events = [ ]

	@property
	def avg_secs_per_event(self):
		return self._window_secs / self._event_count

	@staticmethod
	def _sleep_until(end_ts: float):
		while True:
			diff = end_ts - time.monotonic()
			if diff < 0:
				break

			if diff > 60:
				diff = 60
			elif diff > 5:
				diff = 5
			time.sleep(diff)

	def _fill_bucket(self):
		now = time.monotonic()
		tdiff = now - self._last_fill
		token_count = math.floor(tdiff / self.avg_secs_per_event)
		if token_count > 0:
			self._bucket_fill += token_count
			if self._bucket_fill > self._event_count:
				self._bucket_fill = self._event_count
				self._last_fill = now
			else:
				self._last_fill = self._last_fill + (token_count * self.avg_secs_per_event)
		else:
			expected_ts_for_next_token = self._last_fill + self.avg_secs_per_event
			self._sleep_until(expected_ts_for_next_token)

	def trigger(self):
		while self._bucket_fill == 0:
			self._fill_bucket()
		self._bucket_fill -= 1

if __name__ == "__main__":
	import random
	bl = BurstLimiter(10, 1)
	t0 = time.monotonic()
	last = t0
	for i in range(1, 1000):
		bl.trigger()
		now = time.monotonic()
		absdiff = now - t0
		reldiff = now - last
		print(i, i / absdiff, reldiff)
		last = now
		if i < 50:
			time.sleep(random.random() / 20)
		elif i == 50:
			time.sleep(3)
