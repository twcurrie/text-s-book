import sys
import os
import vobject
import argparse

class Contact(object):
    """ Contact class """

    def __init___(self, email, firstName, lastName, phoneNumber):
        """ Constructor """
        self.email = email
        self.firstName = firstName
        self.lastName = lastName
        self.phoneNumber = phoneNumber


class Parser(object):
    """ Parser class """

    def __init__(self, vcardDir, verbose_mode=False, print_output_mode=True):
        """ Constructor"""
        self.dirname = self.validate_dir(vcardDir)
        self.verbose_mode = verbose_mode
        self.print_output_mode = print_output_mode
        self.phoneBook = {}
        self.emailBook = {}

        self.parse_vcard_dir(vcardDir, self.print_output_mode)

    def validate_dir(self, dirname):
        """ Verifies file exists. """
        if not os.path.isdir(dirname):
            raise ValueError("The directory given is not valid")
        return dirname

    def parse_vcard_dir(self, vcardDir, print_output_mode):
        """ Parses the vCard files in a directory and stores in list of vcards """
        for root, dirs, files in os.walk(vcardDir):
            for vcardFile in files:
               with open(vcardDir+'/'+vcardFile) as vcard_data:
                    data = vcard_data.readlines()
                    vcardString = ''.join(data)
                    #if 'Currie' in vcardString:
                    #    print vcardString
                    try: 
                        vcard_parsed = vobject.readOne(vcardString)
                        try:
                            name = vcard_parsed.fn.value.encode('ascii','ignore')
                            if name[-2:] == '\M':
                                name = name[:-2]
                        except:
                            name = None
                        try: 
                            email = vcard_parsed.email.value.encode('ascii','ignore')
                        except:
                            email = None
                        try:
                            phone = vcard_parsed.tel.value.encode('ascii','ignore')
                            phone = phone.replace('-','').replace('.','').replace('(','').replace(')','').replace(' ','')
                            if phone[:2] != '+1':
                                phone = '+1'+phone
                        except: 
                            phone = None
                        
                        if name is not None:
                            if phone is not None:
                                self.phoneBook[phone] = name
                            if email is not None:
                                self.emailBook[email] = name
                    except:
                        pass # unsure of what to do with broken vcard

def main(argv):
    parser = argparse.ArgumentParser(description='Commandline python script that allows reading of vcard files.')

    parser.add_argument('vcardfile', type=str, help='filename of the vcardfile')
    parser.add_argument('--verbose', '-v', action="store_true", help='activates the verbose mode')

    args = parser.parse_args()

    vcards = Parser(args.logfile)
    

if __name__ == "__main__":
    main(sys.argv)



