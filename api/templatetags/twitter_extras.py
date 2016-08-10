#! /usr/bin/env python
# -*- coding: utf-8 -*-
from django import template
import re
register = template.Library()

from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape

def hashe(text):
    text = conditional_escape(text)
    for hash in re.findall('#([a-zA-Z_0-9]+)', text):
        text=text.replace("#%s"%(hash),u'<a href="http://twitter.com/#search?q=%%23%s">#%s</a>'%(hash,hash))

    return mark_safe(text)
register.filter('hashe', hashe)

def replyize(text):
    for user in re.findall('@([a-zA-Z_0-9]+)', text):
        text=text.replace(user,u'<a href="http://twitter.com/%s">%s</a>'%(user,user))
    return mark_safe(text)
register.filter('replyize', replyize)


import re, htmlentitydefs

##
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.

def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return mark_safe(re.sub("&#?\w+;", fixup, text))
register.filter('unescape', unescape)



#    text = conditional_escape(text)
#    komentare=Diskuse.objects.filter(navod=comment.navod)
#
#    for cislo in re.findall('\[([0-9]+)]', text):
#        try:
#            komentar = komentare[int(cislo)-1]
#            comment.reakce.add(komentar)
#            print komentar
#            text=text.replace("[%s]"%cislo,u'<a href="#comment-%s">↑#%s %s</a>' % (komentar.id,komentar.get_turn(),komentar.nick))
#            comment
#        except (IndexError,AssertionError):
#            pass
#    return mark_safe(text)
