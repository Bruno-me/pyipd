import addressbook
import message
import phonecall
import sms
import memo
import browserhistory

def find_key(dic, val):
	try:
		return [k for k, v in dic.iteritems() if v == val][0]
	except IndexError:
		return False

def dbid2dbclass(databases):
	dbrelations = {}
	#TODO: make this magic
	for mod in [addressbook, message, phonecall, sms, memo, browserhistory]:
		dbrelations[find_key(databases, mod.DBRELATION[0])] = mod.DBRELATION[1]
	return dbrelations
