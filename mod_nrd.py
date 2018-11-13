#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Crontab -e
# 0 0 * * * cd /root/Documents/TGS/Snout/ && /usr/bin/python3.6 /root/Documents/TGS/Snout/nrd_launcher.py

import logging
import sys
import pymongo
from configparser import ConfigParser
import os
from datetime import datetime,timedelta
from modules.mod_retriever import Retriever
import whois

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('logs_snout.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
scrlog = logging.StreamHandler()
scrlog.setFormatter(logging.Formatter("[%(levelname)s] - %(message)s"))
logger.addHandler(scrlog)

if (sys.version_info < (3, 0)):
	logger.warning("ERROR: Please, use Python3.X")
	sys.exit()

def read_config(option ,section='scheduler', filename='config.ini'):
	parser = ConfigParser()
	parser.read(filename)
	if parser.has_section(section):
		if parser.has_option(section, option):
			value = parser.get(section, option)
		else:
			raise Exception('{0} option not found in the {1} section'.format(option, section))
	else:
		raise Exception('{0} section not found in the {1} file'.format(section, filename))
	return value

if __name__ == "__main__":

	# Connect to DB
	try:
		mongohost = read_config('host', 'mongodb')
		mongoport = read_config('port', 'mongodb')
		dbname = read_config('database', 'mongodb')

		connection = pymongo.MongoClient(mongohost, int(mongoport), serverSelectionTimeoutMS=1)
		connection.server_info()
		db = connection[dbname]
		logger.info('Connected to MongoDB')
	except pymongo.errors.ServerSelectionTimeoutError as e:
		logger.warning("Mongod is not started. Tape \"sudo mongod\" in a terminal")
		if not os.path.exists("/data/db"):
			os.makedirs("/data/db")
			logger.info('database created')
		logger.warning("Error %s", e)
		sys.exit()

	if not os.path.exists("Data/"):
		os.makedirs("Data/")
		logger.info('Data Dir created')
	if not os.path.exists("Data/nrd"):
		os.makedirs("Data/nrd")
		logger.info('nrd Dir created')

	logger.info("Launching NRD module...")
	day = 1
	while True:
		try:
			yesterday = (datetime.now() - timedelta(days=day)).strftime('%Y-%m-%d')
			if not os.path.exists("Data/nrd/" + (datetime.now() - timedelta(days=day + 1)).strftime('%Y-%m-%d') + '.txt'):
				rt = Retriever(db, logger)
				url_nrd ="https://whoisds.com/whois-database/newly-registered-domains/" + yesterday + ".zip/nrd"
				print("Downloading", yesterday + ".zip")
				rt.downloader(url_nrd, "Data/nrd/" + "newly-registered-domains-" + yesterday + ".zip")
				print("Unzipping", yesterday + ".zip")
				rt.unzip("Data/nrd/" + "newly-registered-domains-" + yesterday + ".zip")
				day += 1
			else:
				print((datetime.now() - timedelta(days=day + 1)).strftime('%Y-%m-%d'))
				break
		except Exception as e:
			logger.warning(e)
