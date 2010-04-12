"""Handles 'Messages' database"""

#Copyright 2010, Logan Rojas
#License: Simplified BSD

import struct
from datetime import datetime

class Message(object):
	def __init__(self, fields, uid, handle):
		#Generic data
		self.uid = uid
		self.handle = handle
		self.fields = fields

		#Messages specific things that might appear multiple times
		self.to = []
		self.cc = []
		self.bcc = []
		self.attachmentref = []
		self.attachment = []
		self.decode()

	def __repr__(self):
		return '<Message: "%s">' % self.subject

	def decode(self):
		for field in self.fields:
			if field['type'] == 1:
				#To: Header(s), RFC 2822 address '<name> address', separated by a null
				self.to.append(field['data'][8:-1].strip("\x00").split("\x00"))
			if field['type'] == 2:
				#CC: Header(s)
				self.cc.append(field['data'][8:-1].strip("\x00").split("\x00"))
			if field['type'] == 3:
				#BCC: Header(s)
				self.bcc.append(field['data'][8:-1].strip("\x00").split("\x00"))
			if field['type'] == 4:
				#Return-Path: header
				self.returnpath = field['data'][8:-1].strip("\x00").split("\x00")
			if field['type'] == 5:
				#From: header
				self.fromaddr = field['data'][8:-1].strip("\x00").split("\x00")
			if field['type'] == 6:
				#Reply-To: header
				self.replyto = field['data'][8:-1].strip("\x00").split("\x00")
			if field['type'] == 11:
				#subject, with null at the end
				self.subject = field['data'][:-1]
			if field['type'] == 12:
				#plaintext body of the message
				self.body = field['data'].strip("\x00")
			if field['type'] == 24:
				#HTML body of message, with garbage at the beginning
				self.bodyhtml = field['data'][97:]
			if field['type'] == 22:
				#attachment reference, this really isn't of much use
				self.attachmentref.append(field['data'])
			if field['type'] == 25:
				#attachment data, plus garbage
				self.attachment.append(field['data'])
