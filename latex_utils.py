#!/usr/bin/env python

class Latex(object):
    @staticmethod
    escape_characters = {'%':'\%','$':'\$','{':'\{','_':'\_',\
                         '|':'\\textbar ','<':'\\textgreater ','-':'\\textendash ',\
                         '#':'\#','&':'\&','}':'\}','\\':'\\textbackslash ',\
                         '>':'\\textless ', '^':'\\textasciicircum'}

    def replace_escape_characters(self,string_to_replace):
        string_parts = list(string_to_replace)
        for index,part in enumerate(string_parts):
            for character in self.escape_characters:
                if character in part:
                    string_parts[index] = string.replace(part, character,\
                                      self.escape_characters[character])
        return ''.join(string_parts)
