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
import dataclasses
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

	def _matches(self, mail: "ReceivedMail", verbose: bool = False):
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

	def matches(self, mail: "ReceivedMail", verbose: bool = False):
		does_match = self._matches(mail, verbose = verbose)
		if (not does_match) and ("error" in self._cond):
			return (does_match, self._cond["error"])
		else:
			return (does_match, None)

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

@dataclasses.dataclass
class ConditionMatchResult():
	all_conditions_pass: bool
	match_error: str | None = None

class MailingList():
	def __init__(self, mailing_list: dict):
		self._name = mailing_list["name"]
		self._variables = {
			"mailing_list_name": self._name,
		}
		self._variables.update(mailing_list.get("variables", { }))
		mailing_list = self._substitute(mailing_list, self._variables)
		self._conditions = [ MatchCondition(cond) for cond in mailing_list.get("conditions", [ ]) ]
		self._actions = [ RuleAction(action) for action in mailing_list.get("actions", [ ]) ]

	def _substitute(self, obj, replacements: dict):
		if isinstance(obj, str):
			for (repl_from, repl_to) in sorted(replacements.items()):
				obj = obj.replace(f"${{{repl_from}}}", repl_to)
			return obj
		elif isinstance(obj, list):
			return [ self._substitute(item, replacements) for item in obj ]
		elif isinstance(obj, dict):
			return { self._substitute(key, replacements): self._substitute(value, replacements) for (key, value) in obj.items() }
		else:
			return obj

	@property
	def name(self):
		return self._name

	def matches(self, mail: "ReceivedMail", verbose: bool = False) -> ConditionMatchResult:
		condition_match_result = ConditionMatchResult(all_conditions_pass = True)

		for condition in self._conditions:
			(match_result, match_error) = condition.matches(mail, verbose = verbose)
			condition_match_result.all_conditions_pass = condition_match_result.all_conditions_pass and match_result
			condition_match_result.match_error = match_error
			if not match_result:
				break
		return condition_match_result

	def execute_actions(self, mail: "ReceivedMail") -> tuple["ReceivedMail", str]:
		for action in self._actions:
			action_result = action.execute(mail)
			if action_result == Processing.Continue:
				continue
			elif action_result == Processing.Deliver:
				yield (mail, action.via)

	def __str__(self):
		return f"Cond={' && '.join(f'({cond})' for cond in self._conditions)} Act={str(self._actions)}"

class Mailprocessor():
	def __init__(self, mailing_lists: list[dict]):
		self._mailing_lists = [ MailingList(mailing_list) for mailing_list in mailing_lists ]

	@property
	def mailing_lists(self):
		return iter(self._mailing_lists)

	def __str__(self):
		return f"{len(self._mailing_lists)} mailing_lists: {', '.join(str(mailing_list) for mailing_list in self._mailing_lists)}"
