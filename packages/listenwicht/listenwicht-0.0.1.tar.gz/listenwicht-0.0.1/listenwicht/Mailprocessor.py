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

import re
import email.utils
from .Enums import ConditionType, Action, Processing

class MatchCondition():
	def __init__(self, cond: dict):
		self._cond_type = ConditionType(cond["condtype"])
		self._cond = cond
		match self._cond_type:
			case ConditionType.MatchHeader | ConditionType.MatchAddress:
				self._regex = re.compile(self._cond["regex"], flags = re.IGNORECASE)

	@property
	def invert(self):
		return self._cond.get("invert", False)

	def _boolean(self, value: bool):
		return value ^ self.invert

	def matches(self, mail: "ReceivedMail", verbose: bool = False):
		if verbose:
			print(f"Matching condition: {self}")
		match self._cond_type:
			case ConditionType.MatchHeader:
				value = mail[self._cond["key"]]
				return self._boolean(self._regex.fullmatch(value) is not None)

			case ConditionType.MatchAddress:
				mail_addrs = [ mail_addr for (mail_name, mail_addr) in email.utils.getaddresses([ mail[self._cond["key"]] ]) ]
				for mail_addr in mail_addrs:
					if self._regex.fullmatch(mail_addr) is not None:
						return self._boolean(True)
				return self._boolean(False)

			case _:
				raise NotImplementedError(self._cond_type)

	def __repr__(self):
		return f"{self._cond_type.name} field \"{self._cond['key']}\" {'does NOT match' if self.invert else 'matches'} regex \"{self._cond['regex']}\""

class RuleAction():
	def __init__(self, action: dict):
		self._action_type = Action(action["action"])
		self._action = action

	@property
	def via(self):
		return self._action["via"]

	def execute(self, mail: "ReceivedMail"):
		match self._action_type:
			case Action.RemoveHeader:
				key = self._action["key"]
				if isinstance(key, list):
					mail.remove_headers(key)
				else:
					mail.remove_header(key)
				return Processing.Continue

			case Action.RenameHeader:
				mail.rename_header(self._action["old"], self._action["new"])
				return Processing.Continue

			case Action.SetHeader:
				assert(isinstance(self._action["value"], str))
				mail.set_header(self._action["key"], self._action["value"])
				return Processing.Continue

			case Action.SetAddress:
				assert(isinstance(self._action["value"], list))
				assert(len(self._action["value"]) > 0)
				value = ", ".join(email.utils.formataddr((addr_name, addr_mail)) for (addr_name, addr_mail) in self._action["value"])
				mail.set_header(self._action["key"], value)
				return Processing.Continue

			case Action.Deliver:
				mail.randomize_message_id()
				return Processing.Deliver

			case _:
				raise NotImplementedError(self._action_type)

	def __repr__(self):
		return f"{self._action_type.name}"

class Rule():
	def __init__(self, rule: dict):
		self._conditions = [ MatchCondition(cond) for cond in rule.get("conditions", [ ]) ]
		self._actions = [ RuleAction(action) for action in rule.get("actions", [ ]) ]

	def matches(self, mail: "ReceivedMail", verbose: bool = False):
		return all(condition.matches(mail, verbose = verbose) for condition in self._conditions)

	def execute_actions(self, mail: "ReceivedMail"):
		for action in self._actions:
			action_result = action.execute(mail)
			if action_result == Processing.Continue:
				continue
			elif action_result == Processing.Deliver:
				yield (mail, action.via)

	def execute_if_matched(self, mail: "ReceivedMail"):
		if not self.matches(mail):
			return False
		yield from self.execute_actions(mail)

	def __str__(self):
		return f"Cond={' && '.join(f'({cond})' for cond in self._conditions)} Act={str(self._actions)}"

class Mailprocessor():
	def __init__(self, rules: list):
		self._rules = [ Rule(rule) for rule in rules ]

	@property
	def rules(self):
		return iter(self._rules)

	def __str__(self):
		return f"{len(self._rules)} rules: {', '.join(str(rule) for rule in self._rules)}"
