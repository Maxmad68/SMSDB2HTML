#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime
import re
import os


dateEpoch2001 = lambda ts: datetime.utcfromtimestamp(978307200 + ts)

class Handle(object):
	'''
	Represents a Handle (a specific email address or phone number)
	Shouldn't be invoked.
	
	Arguments:
		rowid (int) : The in-database identifier for this handle
		id (str) : The email address or phone number
		service (str) : "iMessage" or "SMS"
	'''
	def __init__(self, rowid, id, service, name = None):
		self.rowid = rowid
		self.id = id
		self.service = service
		self.name = name
		
	def __repr__(self):
		return ("<Handle '{id}' service '{service}'>".format(**self.__dict__))
		
UNKNOWN = Handle(rowid = 0, id = '0', service = None, name = 'Unknown')
		
class Message(object):
	'''
	Represents a Message.
	Shouldn't be invoked.
	
	Arguments:
		rowid (int) : The in-database identifier for this message.
		message (str) : The text sent in the message.
		handle (str) : The handles associated to this message. If I sent the message, it's the recipient. If I recieved the message, it's the sender.
		account (str) : My email address or phone number used to recieve/send the message.
		date (datetime) : The date and time the message was sent.
		service (str) : "SMS" or "iMessage"
		from_me (bool) : True if I sent the message, False if I recieved the message.
		read (bool) : True if the message was read, False otherwise.
		delivered (bool) : True if the message was delivered, False otherwise.
		audio (bool) : True if the message is an audio message. False otherwise. If True, the audio file corresponds to message.attachment
		attachment ( tuple( path, mime) ) : None if the message doesn't contains any attachment (image, video, file,...). If it does, returns a tuple containing the path of the file and the mimetype of the file.
	'''
	def __init__(self, SMSDB, rowid, message, handle, account, date, service, subject = None, from_me = False, read = False, delivered = False, audio_message = False, *args, **kwargs):
		self.SMSDB = SMSDB
		self.rowid = rowid
		self.message = message
		self.handle = handle
		self.account = account
		self.date = date
		self.service = service
		self.subject = subject
		self.from_me = from_me
		self.read = read
		self.delivered = delivered
		self.audio = audio_message
		
		self.__dict__.update(kwargs)
		
	def getAttachment(self):
		paths = self.SMSDB.execute('''SELECT filename, mime_type FROM attachment WHERE ROWID IS (SELECT attachment_id from message_attachment_join WHERE message_id IS %i)'''%self.rowid)
		if paths:
			return paths[0]
		
	attachment = property(getAttachment)
		
	def __repr__(self):
		return ("<Message {rowid}>".format(**self.__dict__))
		

class SMSDB(object):
	'''
	Represents the SMS Database (sms.db or chat.db)
	Parameters:
		path (str) : The path of the sms.db
		
	Arguments:
		messages ( [Message] ) : All the messages contained in the database
		handles ( [Handle] ) : All the handles contained in the database
	'''
	def __init__(self, path):
		self.path = path
		self.conn = sqlite3.connect(path)
		self.cursor = self.conn.cursor()
		self.retrieveHandles()
		self.retrieveMessages()
		
	def retrieveHandles(self):
		self.handles = {}
		query = "SELECT ROWID, id, service, uncanonicalized_id FROM handle"
		for rowid, id, service, name in self.execute(query):
			self.handles[rowid] = Handle(rowid, id, service, name)
			
	def retrieveMessages(self):
		self.messages = []
		query = '''SELECT ROWID, text, handle_id, subject, service, account, "date", is_delivered, is_from_me, is_read, is_audio_message FROM message'''
		result = self.execute(query)
		for (rowid, text, handle_id, subject, service, account, date, is_delivered, is_from_me, is_read, audio) in result:
			account = (account.split(':')[1]) if account else None
			message = Message(
				self,
				rowid,
				text,
				self.handles.get(handle_id, UNKNOWN),
				account,
				dateEpoch2001(date/10e8),
				service,
				subject,
				bool(is_from_me),
				bool(is_read),
				bool(is_delivered),
				bool(audio),
				dateRaw = date
				
			)
			self.messages.append(message)         
			
		
	def execute(self, query):
		return self.cursor.execute(query).fetchall()

if __name__ == '__main__':
	db = SMSDB('/Users/maxime/sms2.db')
	print (db.messages[0].message)