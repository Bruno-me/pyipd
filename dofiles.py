#!/bin/env python

#Copyright 2010, Logan Rojas
#License: Simplified BSD

import reader
import sys
from optparse import OptionParser

import pymongo

#set up the mongodb stuff
conn = pymongo.Connection()
db = conn.pyipd
sms_collection = db.sms
sms_collection.ensure_index('uid', unique=True, drop_dups=True)

parser = OptionParser(usage='Usage: %prog [options] file')

parser.add_option('-p', '--progress', action='store_true', dest='progress', help='Render a progress bar showing file position and current database')

(options, args) = parser.parse_args()

readers = []

for file in args:
	fileobj = open(file, 'rb')
	readers.append(reader.Reader(fileobj, options.progress))

for reader in readers:
	for sms in reader.SMSs:
		 sms_collection.insert(sms.as_dict())
