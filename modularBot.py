#!/user/bin/env python

from __future__ import print_function

from glob import glob
import praw
import dataset
import re
import time
import importlib
import functools
import os.path
import sys
import yaml
from datetime import datetime
from ftplib import FTP
global message # I'm not sure why this needs to be here, but it does in order to work. Declaring it global elsewhere doesn't, either.

class modularFatalError(Exception):
	pass
	
class modularNonFatalError(Exception):
	pass

class Config(object):
    config = {}

    def __init__(self, file_):
        self.file = file_
        f = open(file_, 'r')
        y = yaml.load(f)
        f.close()
        self.__dict__.update(y)
		
		
class modularBot(object):

	commands = []
	listeners = []
	users = []
	catchalls = []


	def __init__(self, config_file):
		self.config = Config(config_file)
		self.username = self.config.modularBot['botname']
		self.password = self.config.modularBot['botpass']
		self.plugins = self.config.modularBot['plugins']
		self.sleep = self.config.modularBot['sleeptime']
		self.subreddits = self.config.modularBot['subreddits']
		self.postlimit = self.config.modularBot['postlimit']
		
	def reply(self, message):
		comment.reply(message)
	
	def _import_plugins(self):
		self._set_import_path()
		plugin_prefix = os.path.split(self.plugins)[-1]
		
		importlib.import_module(plugin_prefix)
		sys.modules[plugin_prefix].bot = self
		
		for plugin in glob('{}/[!_]*.py'.format(self._get_plugin_path())):
			module = '.'.join((plugin_prefix, os.path.split(plugin)[-1][:-3]))
			try:
				importlib.import_module(module)
			except Exception as e:
				print('Failed to import {0}: {1}'.format(module, e))
	
	def _get_plugin_path(self):
		path = self.plugins
		cf = self.config.file
		if path[0] != '/':
			path = os.path.join(os.path.dirname(os.path.realpath(cf)), path)
		return path
	
	def _set_import_path(self):
		path = self._get_plugin_path()
		path = os.path.dirname(path)
		if path not in sys.path:
			sys.path = [path] + sys.path
			
			
	def run(self):
		try:
			r = praw.Reddit('modularBot, the modular reddit bot, by /u/venn177, v0.1')
			r.login(self.username, self.password, disable_warning = True)
			already_done = set()
			subreddits = r.get_subreddit(self.subreddits)
			print('Login successful!')
			print('Monitoring these subs: ' + str(subreddits))
		except Exception as e:
			raise modularFatalError(e)
			
		self._import_plugins()
		
		while True:
			comments = subreddits.get_comments(sort = 'new', limit = self.postlimit)
			global comment
			for comment in comments:
				for (f, matcher) in self.listeners:
					if matcher.search(comment.body):
						f(message)
						already_done.add(comment.id)
					print('Replying')
					

			time.sleep(self.sleep)
			print('Sleeping for ' + str(self.sleep) + ' seconds.')
	
	def listen(self, pattern):
		if hasattr(pattern, '__call__'):
			raise TypeError('Need something to reply to')
			
		def real_listen(wrapped):
			@functools.wraps(wrapped)
			def _f(*args, **kwargs):
				return wrapped(*args, **kwargs)
				
			try:
				matcher = re.compile(pattern, re.IGNORECASE)
				self.listeners.append((_f, matcher))
			except:
				print('Failed to compile matcher for {0}'.format(wrapped))
			return _f
			
		return real_listen
		
	def catchall(self, wrapped):
		@functools.wraps(wrapped)
		def _f(*args, **kwargs):
			return wrapped(*args, **kwargs)

		self.catchalls.append(_f)
		return _f
		
	
def usage():
	yaml_template = """
	modularBot:
		botname: modularBot
		botpass: modularpass
		plugins: plugins
		sleeptime: 300 #time in seconds before reloading
		subreddits: programming+learnprogramming
		postlimit: 50 #number of posts back the bot goes
	"""
	print('Usage: modularBot <config.yaml>')
	print('\nExample YAML\n{}'.format(yaml_template))
	
def main():
	config_file = None
	try:
		config_file = sys.argv[1]
	except IndexError:
		pass
		
	if config_file is None:
		usage()
		sys.exit(1)
	
	if not os.path.isfile(config_file):
		print('Config file "{}" not found.'.format(config_file))
		sys.exit(1)
		
	try:
		bot = modularBot(config_file)
	except Exception as e:
		print('Encountered error: {}'.format(e))
		sys.exit(1)
		
	while True:
		try:
			bot.run()
		except modularFatalError as e:
			print('Fatal error: {}'.format(e))
			sys.exit(1)
		except modularNonFatalError as e:
			print('Non-fatal error: {}'.format(e))
			delay = 5
			print('Delaying for {} seconds...'.format(delay))
			time.sleep(delay)
			bot._init_connection()
		except Exception as e:
			print('Unhandled exception: {}'.format(e))
			sys.exit(1)
			
if __name__ == '__main__':
	main()
		
