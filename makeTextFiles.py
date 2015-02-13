#!/usr/bin/env python

import os
import sys
import shutil
import re
import string
import pycurl
from dateutil.parser import *
from dateutil.tz import *
from datetime import datetime
import time
from unidecode import unidecode

class Latex(object):
    @staticmethod
    escape_characters = {'%':'\%','$':'\$','{':'\{','_':'\_',\
                         '|':'\\textbar ','<':'\\textgreater ','-':'\\textendash ',\
                         '#':'\#','&':'\&','}':'\}','\\':'\\textbackslash ',\
                         '>':'\\textless '}

    def replace_escape_characters(self,string_to_replace):
        string_parts = list(string_to_replace)
        for index,part in enumerate(string_parts):
            for character in self.escape_characters:
                if character in part:
                    string_parts[index] = string.replace(part, character,\
                                      self.escape_characters[character])
        return ''.join(string_parts)

class Picture(object):
    jpg_search = re.compile(r"(https://[^ ]+.jpg)")
    png_search = re.compile(r"(https://[^ ]+.png)")
    gif_search = re.compile(r"(https://[^ ]+.gif)")
    
    def __init__(self,url,send_time):
        self.url = url
        self.send_time = send_time
        png = self.png_search.findall(url)
        jpg = self.jpg_search.findall(url)
        gif = self.gif_search.findall(url)
        if png:
            self.kind = '.png'
        elif jpg:
            self.kind = '.jpg'
        elif gif:
            self.kind = '.gif'
        else:
            self.kind = 'Unknown'

        try:
            self.file_name = self.download_picture()
        except ReferenceError:
            self.file_name = None
    
    def download_picture(self):
        """Downloads picture from given link"""
        #TODO: This will have to be generalized as well
        picture_directory = '/home/twcurrie/Projects/TextsBook/textFiles/pictures/'
        file_name = picture_directory + \
                self.send_time.strftime("%Y_%b_%d_%H_%M_%S")\
                + self.kind
        if not os.path.exists(file_name):
            try:
                with open(file_name, 'wb') as f:
                    c = pycurl.Curl()
                    print "Downloading picture"
                    print self.url
                    c.setopt(c.URL, self.url)
                    c.setopt(c.WRITEDATA, f)
                    c.perform()
                    c.close()
                print "Saved file"
                print file_name
            except:
                print "Error downloading file"
                raise ReferenceError
        else:
            print file_name + " already exists"
        return file_name

    def get_file_name(self):
        return self.file_name

class TextMessage(object):
    https_search = re.compile(r"(https://[^ ]+)")
    http_search = re.compile(r"(http://[^ ]+)")

    def __init__(self,string_time,sender,message=None,picture_link=None):
        """Set up text message with time, sender, and a message or a picture"""
        self.send_time = datetime.strptime(string_time,"%Y %b %d %H:%M:%S")

        self.sender = sender
        
        self.message = message
        
        if picture_link is not None:
            self.picture = Picture(picture_link,self.send_time)

    def __str__(self):
        """Prints out text message as sender and message"""
        return self.sender, self.message
    
    def __repr__(self):
        return '{}: {} {} {}'.format(self.__class__.__name__,
                                     self.sender,
                                     self.message,
                                     self.send_time)
 
    def print_to_latex_file(self,file_dir,print_right):
        """Prints message to a tex file at file_name"""
        month = self.send_time.strftime("%B")
        year = self.send_time.strftime("%Y")
        file_name = file_dir + month + "_" + year + ".tex"

        if os.path.exists(file_name):
            start = "\n"
        else:
            start = "\chapter*{"+month+"}\n"
            print file_name
        
        with open(file_name,'a') as messages_file:
            messages_file.write(start)
            if print_right == True: 
                messages_file.write("\quoteRight{\n")
            else:
                messages_file.write("\quoteLeft{\n")
            
            if hasattr(self,"picture"):
                messages_file.write("\includegraphics[\maxWidth]{")
                messages_file.write(self.picture.file_name)
                messages_file.write("}")
            elif hasattr(self,"message"):
                link_list = self.https_search.findall(self.message)
                link_list +=self.http_search.findall(self.message)
                if link_list:
                    message = self.message
                    message_parts = []
                    for link in link_list:
                        split_message = message.split(link)
                        message_parts.append(Latex.replace_escape_characters(split_message[0]))
                        link = Latex.replace_escape_characters(link)
                        message_parts.append("\url{"+link+"}")
                        message = split_message[1]
                    message = " ".join(message_parts)
                else:
                    message = Latex.replace_escape_characters(self.message)
                messages_file.write(message)
            
            messages_file.write("\n}{")
            messages_file.write(self.send_time.strftime("%d %b %Y %I:%M:%S%p"))
            messages_file.write("}\n")

class Conversation(object):
    """Stores list of text messages"""
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
        sender = text_message_parts[0]
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
            sender = message.sender.strip().lower()
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
    person = 'Klaudia Helena Zarako-Zarakowski'
    user = 'Trevor Currie'
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
