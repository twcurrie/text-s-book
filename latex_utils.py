#!/usr/bin/env python

class Latex(object):
    escape_characters = {"%":"\%", "$":"\$", "{":"\{", "_":"\_", \
                         "|":"\\textbar ", "<":"\\textgreater ", "-":"\\textendash ", \
                         "#":"\#", "&":"\&", "}":"\}", "\\":"\\textbackslash ", \
                         ">":"\\textless ",  "^":"\\textasciicircum "}

    @staticmethod
    def replace_escape_characters(self, string_to_replace):
        string_parts = list(string_to_replace)
        for index, part in enumerate(string_parts):
            for character in Latex.escape_characters:
                if character in part:
                    string_parts[index] = string.replace(part, character,\
                                      Latex.escape_characters[character])
        return "".join(string_parts)
