import os
import re
import datetime
import pycurl
from latex_utils import Latex
    
#TODO: change regex to search for both http, https with one search
HTTPS_SEARCH = re.compile(r"(https://[^ ]+)")
HTTP_SEARCH = re.compile(r"(http://[^ ]+)")
JPG_SEARCH = re.compile(r"(https://[^ ]+.jpg)")
PNG_SEARCH = re.compile(r"(https://[^ ]+.png)")
GIF_SEARCH = re.compile(r"(https://[^ ]+.gif)")


class Sender(object):
    """ Stores sender with phone number and name """

    def __init__(self, phoneNumber, name = None):
        """ Constructor """

        self.phoneNumber = phoneNumber
        self.name = name

    
    def __str__(self):
        """ Standard string output function """
        
        if self.name is not None:
            string = self.name + ": " + self.phoneNumber
        else:
            string = self.phoneNumber

        return string


    def get_name(self):
        """ Returns name of sender """
        
        if self.name is not None:
            return self.name
        else:
            return self.phoneNumber


    def get_phone_number(self):
        """ Returns phone number """

        return self.phoneNumber
    

class Picture(object):
    
    def __init__(self,url,send_time):
        """ Constructor, retrieves hyperlink from string,
            stores type, url, and send_time """

        self.url = url
        self.send_time = send_time
        png = self.PNG_SEARCH.findall(url)
        jpg = self.JPG_SEARCH.findall(url)
        gif = self.GIF_SEARCH.findall(url)

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
        """Downloads picture from given link, stores file in
            $PWD/pictures/ folder """

        picture_directory = os.getcwd() + "/pictures/"
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
        """ Returns file name """

        return self.file_name


class TextMessage(object):
    """ Class to store text message as object with sender,
        time, message, and a possible picture.  Picture is init'd
        as a hyperlink to retrieve the picture from """


    def __init__(self,time,sender,message=None,picture_link=None):
        """Set up text message with string time, sender, and a message or a picture"""
        
        if type(time) is str:
            self.send_time = datetime.strptime(time,"%Y %b %d %H:%M:%S")
        elif isinstance(time,datetime):
            self.send_time = time
        else:
            print "Time not correctly formatted"

        self.sender = sender
        
        self.message = message
        
        if picture_link is not None:
            self.picture = Picture(picture_link,self.send_time)

    def __str__(self):
        """Prints out text message as sender and message"""
        
        string = time.get_time_string()
        string += ": " + self.sender.get_name() + ": " + self.message
        
        return string


    def __repr__(self):

        return '{}: {} {} {}'.format(self.__class__.__name__,
                                     self.sender.get_name(),
                                     self.message,
                                     self.send_time)
 
    def get_time_string(self,format_setting = "%d %b %Y %I:%M:%S%p"):
        """Returns time string """
        return self.send_time.strftime(format_setting)

    def get_time_object(self):
        """Returns time object """
        return self.send_time

    def write_to_latex_file(self,file_dir,print_right):
        """Prints message to a tex file at file_name"""

        month = self.get_time_object().strftime("%B")
        year = self.get_time_object().strftime("%Y")
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
                messages_file.write("\includegraphics[width=\maxWidth]{")
                messages_file.write(self.picture.file_name[:-4])
                messages_file.write("}")
            
            elif hasattr(self,"message"):
                link_list = self.HTTPS_SEARCH.findall(self.message)
                link_list += self.HTTP_SEARCH.findall(self.message)

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
            messages_file.write(self.get_time_string())
            messages_file.write("}\n")

