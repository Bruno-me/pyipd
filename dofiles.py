#!/bin/env python

#Copyright 2010, Logan Rojas
#License: Simplified BSD

import reader

from optparse import OptionParser

parser = OptionParser(usage='Usage: %prog [options] file')

parser.add_option('-p', '--progress', action='store_true', dest='progress', help='Render a progress bar showing file position and current database')

(options, args) = parser.parse_args()

readers = []

for file in args:
	fileobj = open(file, 'rb')
	readers.append(reader.Reader(fileobj, options.progress))
