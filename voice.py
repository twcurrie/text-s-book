#!/usr/bin/env python

import os
import sys
import shutil
import re
from bs4 import BeautifulSoup as bs
from dateutil.parser import *
from dateutil.tz import *
from datetime import datetime,time
from unidecode import unidecode
from types import *

class VoiceParser(object):
    """ Parses directory with Google Voice html files,
        stores in text message, call, sender, and picture 
        objects.  Goal to export to database. """

    def __init__(self,directory):
        """ Initializes the parser by parsing the text messages
            and storing the text message objects into an array.
            Fills a phonebook phoneBookDict and conversations dict"""
        
        self.conversations = {}
        self.phonebook = {}

        if os.path.isdir(directory):
            for filename in os.listdir(directory):
                try:
                    soup = bs(open(directory+"/"+filename))

                    for message_to_parse in soup.find_all(class_="message"):
                        get = {'name':self.get_name,'phone':self.get_phone,\
                               'text':self.get_text,'time':self.get_time]
                        
                        for item in get:
                            try:
                                # Replace function in dict with value
                                get[item] = get[item](message_to_parse)
                            except:
                                print "No "+item+" found in "+filename
                                get[item] = ""
                        
                        # If function type still stored, not successful
                        if get['name'] is not FunctionType and \
                                get['number'] is not FunctionType:
                            sender = Sender(get['phone'], get['name'])
                            self.phonebook[get['phone']] = get['name']
    		            
                            if get['time'] is not FunctionType and \
                                get['text'] is not FunctionType:
                                
                                message = TextMessage(get['time'], sender, get['text'])

                                if self.conversations.has_key(sender):
                                    self.conversations[sender].append(message)
                                else:
                                    self.conversations[sender] = [message]
                except:
                    raise IOError

    def sort_conversations(self):
        """ Sorts conversations in the dictionary's lists """

        for sender in self.conversations:
            self.conversations[sender].sort(message key=lambda message: message.send_time)
    

    def get_name(self, div)
        """ Parses name from div in Google Voice html file """

        name = ""
        try:
            name = div.find(class_="fn").get_text()
        except:
            print "No name"

        return name

    def get_phone(self,div):
        """ Parses phone number from div in Google Voice html file """
        
        return div.find(class_="tel")['href'][4:]

    def get_text(self,div):
        """ Parses text from div in Google Voice html file """
        
        return text = div.find('q').get_text() 

    def get_time(self,div):
        """ Parses time stamp from div in Google Voice html file.
            Returns datetime object."""
        
    	return time = parse(div.find(class_="dt").get_text())

    def check_and_make_directory(self, directory):
        """ Checks if directory exists, makes it if it doesn't """

        if not os.path.isdir(directory):
            try:
                os.mkdir(directory)
                return False
            except:
                print "Error creating directory: "+directory
        else:
            return True

    def save_phonebook_in_file(self, directory_name):
        """ Saves phonebook into file in specified directory. """
    
        if self.phonebook:
            self.check_and_make_directory("./"  + directory_name)

            with open("./" +directory_name+"/phonebook") as phonebookFile:
                for number in self.phonebook:
                    phonebookFile.write(number + ": " +self.phonebook[number] + "\n")
                    

    def save_conversations_in_files(self, directory_name):
        """ Saves parsed conversations in folder directory """

        if self.conversations:
            check_and_make_directory("./"  + directory_name)
            
            for number in self.phonebook:
                if self.phonebook[number]:
                    name = self.phonebook[number]
                else:
                    name = number
                
                base_path = "./" + directory_name + "/" + name
                check_and_make_directory(base_path)

                for message in self.conversations[name]:
                    split_time_string = message.get_time_string().split()
                    path = base_path
                    
                    for time_string in split_time_string:
                        if time_string == split_time_string[-1]:
                            with open(path+"/"+time_string,'a') as conversation_file:
                                conversation_file.write(message.text)
                        else:
                            path += "/" + time_string
                            check_and_make_directory(path)
        return None


if __name__ == "__main__":
    parser = VoiceParser("~/Projects/Voice/Texts/")
