#!/bin/env python

import sys

file = sys.argv[1]

file = open(file, "rb")

#find number of databases
file.seek(39)
numdb = ord(file.read(1))
numdb = numdb + ord(file.read(1))

file.seek(file.tell() + 1)

databases = []

#find database names
for i in range(0,numdb):
	namelen = ord(file.read(1)) + ord(file.read(1))
	databases += [[i, file.read(namelen)[:-1]],]

print databases
