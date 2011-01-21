###
# Copyright (c) 2011, tcatm
# All rights reserved.
#
#
###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.ircmsgs as ircmsgs

import bitcoin
from deserialize import *
import math

def formatBTC(n, addSign = False):
	s = "%0.2f BTC" % (math.ceil(n * 100) / 100.,)
	if addSign and n >= 0:
		s = "+" + s
	return s

def Bitcoin2BTC(n):
	return n / 100000000.

toTonalDict = dict(((57, u'\ue9d9'), (65, u'\ue9da'), (66, u'\ue9db'), (67, u'\ue9dc'), (68, u'\ue9dd'), (69, u'\ue9de'), (70, u'\ue9df'), (97, u'\ue9da'), (98, u'\ue9db'), (99, u'\ue9dc'), (100, u'\ue9dd'), (101, u'\ue9de'), (102, u'\ue9df')))

def formatTBC(n, addSign = False):
	s = "%x" % n
	n %= 1
	if n:
		s += '.'
		while n:
			n *= 16
			s += "%x" % n
			n %= 1
	s = unicode(s).translate(toTonalDict)
	s += " TBC"
	if addSign and n > 0:
		s = "+" + s
	return s

def Bitcoin2TBC(n):
	return n / 65536.

def formatBitcoin(n, addSign = False):
	if not n % 0x10000:
		return formatTBC(Bitcoin2TBC(n), addSign);
	if not n % 1000000:
		return formatBTC(Bitcoin2BTC(n), addSign);
	if not n % 0x100:
		return formatTBC(Bitcoin2TBC(n), addSign);
	s = "%d uBTCents" % (n,);
	if addSign and n > 0:
		s = "+" + s;
	return s;

class BTCMonitor(callbacks.Plugin):
	"""Add the help for "@plugin help BTCMonitor" here
	This should describe *how* to use this plugin."""
	threaded = True

	def __init__(self, irc):
		self.__parent = super(BTCMonitor, self)
		self.__parent.__init__(irc)

		self.channel = '#bitcoin-monitor'
		self.node = Node("192.168.42.3", 8333, irc, self)

		self.node.start()

	def die(self):
		self.node.stop()
		self.node.join()

class Node(bitcoin.BitcoinNode):
	def __init__(self, dstaddr, dstport, irc, plugin):
		self.__parent = super(Node, self)
		self.__parent.__init__(dstaddr, dstport)
		print "Node init"
		
		self.plugin = plugin
		self.irc = irc

	def irc_msg(self, msg):
		self.irc.queueMsg(ircmsgs.privmsg(self.plugin.channel, msg.encode('utf-8')))

	def do_tx(self, message):
		tx = message.tx
		tx.calc_sha256()

		outs = map(lambda x: "%s \x0309,01%s\x03" % (extract_public_key(x.scriptPubKey), formatBitcoin(x.nValue)), tx.vout) 

		msg = "TX %s %064x" % (" ".join(outs), tx.sha256)

		self.irc_msg(msg)

	def do_block(self, message):
		block = message.block
		block.calc_sha256()
		msg = "block %064x" % block.sha256

		self.irc_msg(msg)

Class = BTCMonitor
