import os
import re
import sys

def find_keys(dic, val):
	return [k for k, v in dic.iteritems() if v == val]

def dbid2dbclass(databases):
	dbrelations = {}
	for mod in modules:
		try:
			for relation in mod.DBRELATIONS:
				keys = find_keys(databases, relation[0])
				for key in keys:
					dbrelations[key] = relation[1]
		except AttributeError:
			#base.py probably
			pass
	return dbrelations

try:
	os.chdir('models')
except:
	#I know this is bad practice, sue me
	print "aaaaaaaaaa, couldn't chdir to models"
else:
	files = os.listdir('.')
	damnregex = re.compile('.*(?<!__init__)\.py$')
	files = filter(damnregex.search, files)
	filenameToModuleName = lambda f: os.path.splitext(f)[0]
	moduleNames = map(filenameToModuleName, files)
	modules = map(__import__, moduleNames)
	os.chdir('..')
