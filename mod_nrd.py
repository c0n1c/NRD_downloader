#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from datetime import datetime,timedelta
from modules.file_downloader import file_downloader

path_file = "Data/temp/"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:36.0) Gecko/20100101 Firefox/36.0",
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
			"Accept-Language": "en-US,en;q=0.5",
			"Accept-Encoding": "gzip, deflate"}

class mod_nrd(object):
	def __init__(self, db, logger):
		self.db = db
		self.logger = logger

	def run(self):
		try:
			self.logger.info("Launching NRD module")
			day = 1
			while True:
				yesterday = (datetime.now() - timedelta(days=day)).strftime('%Y-%m-%d')
				if self.db.nrd.find({"Date": yesterday}).count() == 0:
					url_nrd = "https://whoisds.com/whois-database/newly-registered-domains/" + yesterday + ".zip/nrd"
					name_nrd_file = "newly-registered-domains-" + yesterday + ".zip"
					fd = file_downloader(self.logger)
					fd.run(url_nrd, path_file, name_nrd_file)
					domain_list = open(path_file + yesterday + ".txt")
					self.logger.info("%s file is inserting in MongoDb", yesterday)
					for domain in domain_list:
						domain = domain[:-1]
						self.db.nrd.insert({"Date": yesterday, "domain_name": domain})
					os.remove(path_file + yesterday + ".txt")
					day += 1
				else:
					break
		except Exception as e:
			self.logger.warning(e)
			pass