#!/usr/bin/env python

import os
import sys
import shutil
import re
import string
import pycurl
import time
from dateutil.parser import *
from dateutil.tz import *
from datetime import datetime
from unidecode import unidecode
from latex_utils import Latex
from text_message import TextMessage,Sender,Picture

#TODO: Sender needs to be changed from string to actual Sender object


class Conversation(object):
    """Stores list of text messages, parses from series of
        text message files, properly formatted """

    def __init__(self,conversation_file=None):
        """Initialize conversation by reading text message files"""
        self.text_messages = []

        if conversation_file is not None:
            if os.path.exists(conversation_file):
                print "Reading file ...."
                print conversation_file
                with open(conversation_file,'r') as conversation:
                    for text_message in conversation:
                        sender,message,send_time = \
                                self.split_up_line_in_file(text_message,"(_*_)")

                        picture_links = self.find_all_picture_links(message)

                        if picture_links:
                            for link in picture_links:
                                split_message = message.split(link)
                                message = split_message[1]
                                
                                self.save_text(send_time,sender,\
                                            message = split_message[0])

                                self.text_messages.append(\
                                        TextMessage(send_time, sender, \
                                        picture_link = link))
                        else:
                            self.save_text(send_time,sender,\
                                            message = split_message[0])
            else:
                print conversation_file+" does not exist"
        else:
            print "empty conversation created"

        self.sort_messages()

    
    def save_text(self,send_time,sender_name,text_message):
        """ Creates message object and appends it to list """
        character_limit = 160
        text_messages = [text_message]
        if len(text_message) > character_limit:
            text_messages = self.split_up_messages(text_message,character_limit)
 
        for text_message in text_messages:
            split_text = TextMessage(send_time,sender_name, message = text_message)
            self.text_messages.append(split_text)


    def split_up_message(self, text_message, character_limit):
        """ Splits up message string to specified character limit"""
        words = text_message.split(" ")
        messages = []
        while words:
            message = words.pop(0)
            message_length = len(message)
            if message_length <= character_limit:
                if len(words[0]) + message_length <= character_limit:
                    message += " " + words.pop(0)
                else:
                    messages.append(message)
            else:
                while message:
                    messages.append(message[:character_limit])
                    message = message[character_limit:]

        return messages

        
    def split_up_line_in_file(self,text_message,delimiter):
        """ Splits up message into its parts, by the delimiter """
        text_message_parts = text_message.split(delimiter)
        sender = text_message_parts[0] #TODO this needs to be a sender object, not a string
        message = text_message_parts[1]
                                                       
        send_time = text_message_parts[2].strip()
        return sender,message,send_time


    def get_time_of_first_message(self):
        """ Returns the earliest time in the conversation"""
        return self.text_messages[0].send_time


    def find_all_picture_links(self,message):
        """ Returns all links in message """
        picture_links = Picture.png_search.findall(message)
        picture_links += Picture.jpg_search.findall(message)
        return picture_links 


    def combine_conversations(self,another_conversation):
        self.text_messages += another_conversation.text_messages


    def sort_messages(self):
        """ Sorts messages by timestamp """
        self.text_messages.sort(key=lambda item: item.send_time)


    def print_messages_to_latex(self, user):
        """ Prints the latex format of 
        each message in conversation."""
        #TODO: Will likely need to generalize this string:
        conversation_dir = "/home/twcurrie/Projects/TextsBook/textFiles/"
        
        for message in self.text_messages:
            sender = message.sender.get_name().strip().lower()
            # TODO: Generalize this
            if sender == 'me' or sender == '+16267204969' \
                    or sender == "trevor w. currie":
                sender = "trevor currie"

            if sender == user.strip().lower():
                message.print_to_latex_file(conversation_dir,True)
            else:
                message.print_to_latex_file(conversation_dir,False)


if __name__ == '__main__':
    texts_directory = '/home/twcurrie/Projects/Voice/Texts/'
    person = 'User 1'
    user = 'User 2'
    walk_dir = texts_directory+person
    
    print walk_dir
    conversations = Conversation()    
    for root,dirs,files in os.walk(walk_dir):
        for name in files:
            if "." not in name:
                print os.path.join(root,name)
                conversation_from_file = Conversation(os.path.join(root,name))
                conversations.combine_conversations(conversation_from_file)
    
    conversations.sort_messages()
    conversations.print_messages_to_latex(user)
