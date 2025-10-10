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

import sys
import listenwicht
from .MultiCommand import MultiCommand
from .ActionDisplay import ActionDisplay
from .ActionDaemon import ActionDaemon
from .ActionSystemd import ActionSystemd

def main(argv = None):
	if argv is None:
		argv = sys.argv

	mc = MultiCommand(description = "Mailing list daemon", trailing_text = f"listenwicht v{listenwicht.VERSION}")

	def genparser(parser):
		parser.add_argument("-d", "--deliver-mail", action = "store_true", help = "If all checks pass, actually devlier the mail.")
		parser.add_argument("-c", "--config-file", metavar = "filename", default = "listenwicht.json", help = "Configuration file to use. Defaults to %(default)s.")
		parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increase verbosity. Can be given multiple times.")
		parser.add_argument("mailfile", nargs = "+", help = "File(s) to parse and show how they would be processed")
	mc.register("display", "Display how a particular mail would be processed", genparser, action = ActionDisplay)

	def genparser(parser):
		parser.add_argument("-c", "--config-file", metavar = "filename", default = "listenwicht.json", help = "Configuration file to use. Defaults to %(default)s.")
		parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increase verbosity. Can be given multiple times.")
		parser.add_argument("maildir", help = "Maildir directory to watch")
	mc.register("daemon", "Watch a maildir and auto-deliver according to the set rules", genparser, action = ActionDaemon)

	def genparser(parser):
		parser.add_argument("-c", "--config-file", metavar = "filename", default = "listenwicht.json", help = "Configuration file to use. Defaults to %(default)s.")
		parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increase verbosity. Can be given multiple times.")
		mutex = parser.add_mutually_exclusive_group(required = True)
		mutex.add_argument("-i", "--install", action = "store_true", help = "Install a systemd unit.")
		mutex.add_argument("-u", "--uninstall", action = "store_true", help = "Uninstall the systemd unit.")
		parser.add_argument("maildir", help = "Maildir directory to watch")
	mc.register("systemd", "Install or uninstall listenwicht as a user-mode systemd unit", genparser, action = ActionSystemd)

	return mc.run(argv[1:])

if __name__ == "__main__":
	sys.exit(main(sys.argv))

