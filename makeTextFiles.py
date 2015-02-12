#!/usr/bin/env python

import os
import sys
import shutil
import re
from dateutil.parser import *
from dateutil.tz import *
from datetime import datetime,time
from unidecode import unidecode

url = re.compile(r"(https://[^ ]+)")

class TextMessage(object):
    def __init__(self,time,sender,message=None,picture=None)
        self.time = datetime.strptime(time,"%Y %b %d %H:%M:%S")
        if sender == 'Me':
            sender = "Trevor Currie"
        self.sender = sender
        
        self.message = message
        self.picture = picture

    def __str__(self):
        return self.sender, self.message

    def print_to_latex_file(self,file_name,right):
        with open(file_name,'a') as messages_file:
            if right == True: 
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
            messages_file.write(self.time.strftime("%d %b %Y %I:%M:%S%p"))
            messages_file.write("}\n")


class Conversation(object)
    def __init__(self,conversation_file):
        self.text_messages = []
        if os.path.exists(conversation_file):
            with open(conversation_file,'r') as conversation:
                for text_message in conversation:
                    text_message_parts = text_message.split(";")
                    sender = text_message_parts[0]
                    message = text_message_parts[1]
                    messages = []
                                                                       
                    time = text_message_parts[2]
                    
                    picture_links = url.findall(message)
                                                          
                    if not picture_links:
                        for picture_link in picture_links:
                            split_message = message.split(picture_link)
                            message = split_message[1]
                            messages.append(split_message[0])
                            messages.append(picture_link)

                    else:
                        messages.append(message)

                    for message in messages:
                        if url.search(message) is None:
                            self.text_message.append(TextMessage(time,sender,message=message))
                        else:
                            self.text_message.append(TextMessage(time,sender,picture=message))

        self.sort_messages()
    
    def __add__(self,other):
        if type(other) == type(self):
            raise TypeError
        else:
            self.messages += other.messages
            self.sort_messages()
    
    def sort_messages(self):
        self.messages.sort(key=lambda text: text.time)#, reverse=True)


    

if  __name__ =='__main__':
    current_directory = os.path.abspath(os.curdir)	

