#!/usr/bin/env python

import os
import sys
import shutil
import re
import pycurl
from dateutil.parser import *
from dateutil.tz import *
from datetime import datetime,time
from unidecode import unidecode

url = re.compile(r"(https://[^ ]+.jpg)")

class TextMessage(object):
    def __init__(self,time,sender,message=None,picture=None):
        """Set up text message with time, sender, and a message or a picture"""
        self.time = datetime.strptime(time,"%Y %b %d %H:%M:%S")
        
        if sender == 'Me' or sender == '+16267204969':
            sender = "Trevor Currie"
        self.sender = sender
        
        self.message = message
        self.picture = picture
        
        if picture is not None:
            try:
                download_picture(picture)
            except ReferenceError:
                self.picture = None

    def __str__(self):
        """Prints out text message as sender and message"""
        return self.sender, self.message

    def download_picture(self):
        """Downloads picture from given link"""
        picture_directory = '~/Projects/TextsBook/textFiles/pictures/'
        file_name = picture_directory + \
                datetime.strftime("%Y_%b_%d_%H_%M_%S",self.time) +\
                + ".jpg"
        try:
            with open(file_name, 'wb') as f:
                c = pycurl.Curl()
                print "Downloading picture"
                print self.picture
                c.setopt(c.URL, self.picture)
                c.setopt(c.WRITEDATA, f)
                c.perform()
                c.close()
            print "Saved file"
            print file_name
        except:
            raise ReferenceError


    def print_to_latex_file(self,file_name,print_right):
        """Prints message to a tex file at file_name"""
        if os.path.exists(file_name):
            start = "\n"
        else:
            start = "\chapter{"+datetime.strftime("%B",self.time)+"}\n"
        try:
            with open(file_name,'a') as messages_file:
                messages_file.write(start)
                if print_right == True: 
                    messages_file.write("\quoteRight{\n")
                else:
                    messages_file.write("\quoteLeft{\n")

                if self.picture is not None:
                    messages_file.write("\includegraphics[\maxWidth]{")
                    messages_file.write(self.picture)
                    messages_file.write("}")
                elif self.message is not None:
                    messages_file.write(self.message)
                
                messages_file.write("\n}{")
                messages_file.write(datetime.strftime("%d %b %Y %I:%M:%S%p",self.time))
                messages_file.write("}\n")
        except:
            print "Error in printing to file: "+messages_file

class Conversation(object):
    """Stores list of text messages"""
    def __init__(self,conversation_file):
        """Initialize conversation by reading text message files"""
        self.text_messages = []

        if os.path.exists(conversation_file):
            with open(conversation_file,'r') as conversation:
                for text_message in conversation:
                    text_message_parts = text_message.split(";")
                    sender = text_message_parts[0]
                    message = text_message_parts[1]
                                                                       
                    time = text_message_parts[2].strip()
                    
                    picture_links = url.findall(message)
                                                          
                    if picture_links:
                        for picture_link in picture_links:
                            split_message = message.split(picture_link)
                            message = split_message[1]
                            self.text_messages.append(\
                                    TextMessage(time, sender, \
                                    message = split_message[0]))
                            self.text_messages.append(\
                                    TextMessage(time, sender, \
                                    picture = picture_link))
                    else:
                        self.text_messages.append(\
                                 TextMessage(time, sender, \
                                 message=message))
        else:
            print conversation_file+" does not exist"

        self.sort_messages()
    
    def __add__(self,other):
        """ Adds two conversation objects together by combining 
            their lists"""
        
        if type(other) == type(self):
            raise TypeError
        else:
            self.text_messages += other.text_messages
            self.sort_messages()
    
    def get_time_of_first_message(self):
        """ Returns the earliest time in the conversation"""
        
        self.sort_messages()
        return self.text_messages[0].time

    def sort_messages(self):
        """ Sorts messages by timestamp """
        
        self.text_messages.sort(key=lambda text: text.time)#, reverse=True)

    def print_messages_to_latex(self, user):
        """ Prints the latex format of 
        each message in conversation."""
        
        conversation_directory = "~/Projects/TextsBook/textFiles/"
        conversation_file = datetime.strftime(self.get_time_of_first_message(),"%B")+".tex"
        for message in self.text_messages:
            if message.sender == user:
                message.print_to_latex_file(conversation_file,True)
            else:
                message.print_to_latex_file(conversation_file,False)

if __name__ == '__main__':
    texts_directory = '/home/twcurrie/Projects/Voice/Texts/'
    person = 'Klaudia Helena Zarako-Zarakowski'
    
    walk_dir = texts_directory+person
    
    print walk_dir
    for root,dirs,files in os.walk(walk_dir):
        for name in files:
            if "." not in name:
                print os.path.join(root,name)
                conversation_from_file = Conversation(os.path.join(root,name))
                conversation_from_file.print_messages_to_latex(person)
                print len(conversation_from_file.text_messages)




         


