#!/usr/bin/env python


"""
HiFi IRC bot.
"""

import sys, time, csv
from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower
import botcommon

class HifiBot(SingleServerIRCBot):
  def __init__(self, channel, nickname, server, port):
    SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
    self.command_count = 0
    self.channel = channel
    self.nickname = nickname

    self.queue = botcommon.OutputManager(self.connection)
    self.queue.start()

    self.init_whitelist()
    self.start()

  def on_nicknameinuse(self, c, e):
    self.nickname = c.get_nickname() + "_"
    c.nick(self.nickname)

  def on_welcome(self, c, e):
    c.join(self.channel)

  def on_privmsg(self, c, e):
    from_nick = nm_to_n(e.source())
    self.do_command(e, e.arguments()[0], from_nick)

  def on_pubmsg(self, c, e):
    from_nick = nm_to_n(e.source())
    self.do_command(e, e.arguments()[0], from_nick)

  def say_public(self, text):
    self.queue.send(text, self.channel)

  def say_private(self, nick, text):
    self.queue.send(text,nick)

  def reply(self, text, to_private=None):
    if to_private is not None:
      self.say_private(to_private, text)
    else:
      self.say_public(text)

  def say_whitelist(self):
    self.say_public("Available sounds are: '" + "', '".join(self.whitelist) + "'")

  def init_whitelist(self):
      self.whitelist = []
      fh = None
      try:
          fh = open('./whitelist.txt', 'r')
      except IOError:
          return

      self.whitelist = [line.strip() for line in fh.readlines()]
      self.say_whitelist()

  def clear_queue(self):
    fh = open('/path/to/hifi/php/queue.csv', 'w')
    writer = csv.writer(fh, delimiter = ',')
    writer.writerow(['file', 'timestamp'])
    fh.close()
    self.command_count = 0

  def do_command(self, e, cmd, from_private):
    if '.reload-whitelist' == cmd:
        self.init_whitelist()
        return

    if '.list-sounds' == cmd:
        self.say_whitelist()
        return

    if '!' == cmd[0]:
        cmd = cmd[1:]
        if cmd in self.whitelist:
            if (self.command_count >= 32):
                self.clear_queue()
            self.command_count += 1

            fh = None
            try:
                fh = open('/path/to/hifi/php/queue.csv', 'a')
            except IOError:
                return

            writer = csv.writer(fh, delimiter = ',')
            writer.writerow([cmd, round(time.time() * 1000)])
            fh.close()

if __name__ == "__main__":
  try:
    botcommon.trivial_bot_main(HifiBot)
  except KeyboardInterrupt:
    print "Shutting down."

