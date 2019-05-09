#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime
import re
import os
import sys
import shutil
import tempfile

if sys.version_info >= (3, 0):
   import urllib.request as urllib
else:
   import urllib



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
      

def makeConv(messages):
   global attachment_path
   content = str()
   
   date = None
   for msg in messages:
      message_html = ''
      
      service = msg.service.lower()
      
      if msg.date.date() != date:
         message_html += '<p class="date">{}</p>'.format(msg.date.date().strftime(r'%a %d %b %Y'))
         date = msg.date.date()
         
      messageText = msg.message
      
      if msg.attachment:
         if attachment_path:
            path, mime = msg.attachment
            if path == None:
               messageText = '<i>Unknown attachent</i>'
               abspath = None
            elif 'Attachments' in path:
               abspath = path.split('/')
               del abspath[:abspath.index('Attachments')+1]
               abspath = os.path.join(attachment_path ,'/'.join(abspath))
            else:
               abspath = path
            
            try:
               attachment_filepath = os.path.realpath(abspath)
            except TypeError:
               messageText = '<i>Attachment not found</i>'
            else:
               if mime != None and mime.startswith('image/'):
                  messageText = '<a href="{path}" target="_blank"> <img class="sent_image" src="{path}"/> </a>'.format(path = attachment_filepath )
               elif mime != None and mime.startswith('audio/'):
                  messageText = '<audio controls src="{path}"> Your browser does not support the <code>audio</code> element. </audio>'.format(path = attachment_filepath )
               elif mime != None and mime.startswith('video/'):
                  messageText = '<video controls class="sent_video"><source src="{path}"></source>Your browser does not support the <code>video</code> element.</video>'.format(path = attachment_filepath )
                     
               else:
                  if abspath:
                     messageText = '<a href="{path}" target="_blank"><i>Attachment</i></a>'.format(path = os.path.realpath(abspath) )
                  
         else:
            messageText = '<i>Attachment</i>'
               

            
            
            
            
            
            
      if msg.from_me:
         message_html += '<p class="{svc}-from-me last">{msg}</p>'.format(svc = service, msg = messageText)
      else:
         message_html += '<p class="{svc}-to-me last">{msg}</p>'.format(svc = service, msg = messageText)
         
      content += message_html		
            
                  
   return content
   
def makeChoice(handles, last_messages):
   content = str()
   for handle in handles.values():
      msg = last_messages[handle.rowid]
      if msg == None:
         msg = '<i>No Messages</i>'
         
      if len(msg) > 50:
         msg = msg.replace('\n','')[:50]+'...'
      
      handle_html = '''
<li>
            <a href="chat-{rowid}.html" role="button" style="color: black">
               <h3>{id} - {svc}</h3>
               <p>{msg}</p>
            </a>
         </li>'''.format(rowid = handle.rowid, id = handle.id, svc = handle.service, msg = msg)
      
      content += handle_html
   return content
      
      
global attachment_path


def man():
   print ('SMSDB2HTML 1.0, by Maxime MADRAU')
   print ('usage: smsdb2html <sms.db path> <output path> [-a <attachments path> [--copy-attachments]] ')
   print ('')
   exit()

if __name__ == '__main__':

   args = sys.argv[1:]

   try:
         
      if '-a' in args:
         attachment_path_index = args.index('-a') + 1
         attachment_path = args[attachment_path_index]
         del args[attachment_path_index]
         args.remove('-a')
      else:
         attachment_path = None
         
      if '--copy-attachments' in args:
         copy_attachments = True
         if attachment_path == None:
            man()
         args.remove('--copy-attachments')
      else:
         copy_attachments = False
         
      database_path = args[0]
      output_path = args[1]
   except:
      man()

   if attachment_path and os.path.split(attachment_path)[-1] not in  ('Attachments', 'Attachments/'):
      print ('Must specified the attachment directory\'s full path.')
      exit()
      
   ressources_path = './Content'
   if not os.path.isdir(ressources_path):
      ressources_path = '/usr/share/smsdb2html/Ressources'
      if not os.path.isdir(ressources_path):
         print ('Ressources not found, downloading them from the Internet...')
         # Download ressources
         ressources_path = tempfile.mkdtemp(suffix='-smsdb2html')
         files = ['chat.html','glyphs.ttf','index.html','ios7.min.css','style.css']
         for filepath in files:
            try:
               urllib.urlretrieve('https://raw.githubusercontent.com/Maxmad68/SMSDB2HTML/master/Content/%s'%filepath ,os.path.join(ressources_path, filepath))
            except:
               print ("Can\'t download files. Please check your internet connexion or download ressources from my Github: https://github.com/Maxmad68/SMSDB2HTML")
               exit()
         
         

   db = SMSDB(database_path)

   if os.path.isdir(output_path):
      print ('Output path already exists. Please specify an unexisting path.')
      print ('')
      exit()
   os.makedirs(output_path)
   shutil.copy(os.path.join(ressources_path, 'ios7.min.css'), os.path.join(output_path,'ios7.min.css'))
   shutil.copy(os.path.join(ressources_path, 'style.css'), os.path.join(output_path,'style.css'))
   shutil.copy(os.path.join(ressources_path, 'glyphs.ttf'), os.path.join(output_path,'glyphs.ttf'))
   
   if copy_attachments:
      print ('Copying Attachments directory. This may take a while...')
      shutil.copytree(attachment_path, os.path.join(output_path, 'Attachments'), symlinks=True)
      print ('Attachments directory copied!')
      attachment_path = os.path.join(os.path.split(output_path)[-1], 'Attachments')

   last_messages = {}

   for index, handle in enumerate(db.handles.values()):
      print ('Making conversation %i/%i'%(index + 1, len(db.handles)))

      considering_messages = list(filter(lambda m: m.handle.id == handle.id and m.handle.service == handle.service, db.messages))
      
      if considering_messages:
         last_messages[handle.rowid] = considering_messages[-1].message
      else:
         last_messages[handle.rowid] = '<i>No Messages</i>'

      with open(os.path.join(ressources_path, 'chat.html'), 'r') as f:
         content_raw = f.read()

      content = content_raw.format(
         HANDLE = handle.id,
         CHAT = makeConv(considering_messages)
      )

      with open(os.path.join(output_path,'chat-%i.html'%handle.rowid),'w') as f:
         f.write(content)

   print ('Making index.html')

   with open(os.path.join(ressources_path, 'index.html'), 'r') as f:
         content_raw = f.read()

   content = content_raw.format(
      CHOICE = makeChoice(db.handles, last_messages)
   )

   with open(os.path.join(output_path,'index.html'),'w') as f:
      f.write(content)
