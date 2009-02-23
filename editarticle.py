#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## modified to use mwclient
## 
## 

# Edit a Wikipedia article with your favourite editor.
#
# (C) Gerrit Holl 2004
# Distributed under the terms of the MIT license.

# Version 0.4.
#
# TODO: - non existing pages
#       - edit conflicts
#       - minor edits
#       - watch/unwatch
#       - ...

__metaclass__ = type
__version__ = "$Id: editarticle.py 5846 2008-08-24 20:53:27Z siebrand $"


import sys
import os
import string
import optparse
import tempfile

from sys import path

# for mwclient
import config_manager as config
import client as mwclient

config.verify(["editor"])

msg = {
    'ar': u'تعديل يدوي: %s',
    'de': u'Manuelle Bearbeitung: %s',
    'en': u'Manual edit: %s',
    'he': u'עריכה ידנית: %s',
    'ja': u'手動編集: %s',
    'pt': u'Editando manualmente com bot: %s',
    'sv': u'Manuell redigering: %s',
    'is': u'Handvirk breyting: %s',
    'zh': u'手動編輯: %s',
}

#################################################################
def log(str):
    pass;

class uiFake:
    def uioutput(self, str, **kwargs):
        print str;
ui = uiFake()

import threading
output_lock = threading.Lock()
input_lock = threading.Lock()
output_cache = []
def output(text, decoder = None, newline = True, toStdout = False):
    """Output a message to the user via the userinterface.

    Works like print, but uses the encoding used by the user's console
    (console_encoding in the configuration file) instead of ASCII.
    If decoder is None, text should be a unicode string. Otherwise it
    should be encoded in the given encoding.

    If newline is True, a linebreak will be added after printing the text.

    If toStdout is True, the text will be sent to standard output,
    so that it can be piped to another process. All other text will
    be sent to stderr. See: http://en.wikipedia.org/wiki/Pipeline_%28Unix%29

    text can contain special sequences to create colored output. These
    consist of the escape character \03 and the color name in curly braces,
    e. g. \03{lightpurple}. \03{default} resets the color.

    """
    output_lock.acquire()
    try:
        if decoder:
            text = unicode(text, decoder)
        elif type(text) is not unicode:
            if verbose:
                print "DBG> BUG: Non-unicode (%s) passed to wikipedia.output without decoder!" % type(text)
                print traceback.print_stack()
                print "DBG> Attempting to recover, but please report this problem"
            try:
                text = unicode(text, 'utf-8')
            except UnicodeDecodeError:
                text = unicode(text, 'iso8859-1')
        if newline:
            text += u'\n'
        log(text)
        if input_lock.locked():
            cache_output(text, toStdout = toStdout)
        else:
            print "Calling output with " + str(type(text)) + " " + str(type(toStdout))
            ui.uioutput(text, toStdout = toStdout)
    finally:
        output_lock.release()
import difflib
def showDiff(oldtext, newtext):
    """
    Prints a string showing the differences between oldtext and newtext.
    The differences are highlighted (only on Unix systems) to show which
    changes were made.
    """
    # For information on difflib, see http://pydoc.org/2.3/difflib.html
    color = {
        '+': 'lightgreen',
        '-': 'lightred',
    }
    diff = u''
    colors = []
    # This will store the last line beginning with + or -.
    lastline = None
    # For testing purposes only: show original, uncolored diff
    #     for line in difflib.ndiff(oldtext.splitlines(), newtext.splitlines()):
    #         print line
    for line in difflib.ndiff(oldtext.splitlines(), newtext.splitlines()):
        if line.startswith('?'):
            # initialize color vector with None, which means default color
            lastcolors = [None for c in lastline]
            # colorize the + or - sign
            lastcolors[0] = color[lastline[0]]
            # colorize changed parts in red or green
            for i in range(min(len(line), len(lastline))):
                if line[i] != ' ':
                    lastcolors[i] = color[lastline[0]]
            diff += lastline + '\n'
            # append one None (default color) for the newline character
            colors += lastcolors + [None]
        elif lastline:
            diff += lastline + '\n'
            # colorize the + or - sign only
            lastcolors = [None for c in lastline]
            lastcolors[0] = color[lastline[0]]
            colors += lastcolors + [None]
        lastline = None
        if line[0] in ('+', '-'):
            lastline = line
    # there might be one + or - line left that wasn't followed by a ? line.
    if lastline:
        diff += lastline + '\n'
        # colorize the + or - sign only
        lastcolors = [None for c in lastline]
        lastcolors[0] = color[lastline[0]]
        colors += lastcolors + [None]

    result = u''
    lastcolor = None
    for i in range(len(diff)):
        if colors[i] != lastcolor:
            if lastcolor is None:
                result += '\03{%s}' % colors[i]
            else:
                result += '\03{default}'
        lastcolor = colors[i]
        result += diff[i]
    output(result)
def inputunicode(question, password = False):
    """
    Works like raw_input(), but returns a unicode string instead of ASCII.

    Unlike raw_input, this function automatically adds a space after the
    question.
    """

    # TODO: make sure this is logged as well
    print question + ' '
    if password:
        import getpass
        text = getpass.getpass('')
    else:
        text = raw_input()
    text = unicode(text, config.get("console_encoding"))
    return text
###################################################################




class TextEditor:
    def __init__(self):
        pass

    def command(self, tempFilename, text, jumpIndex = None):
        command = config.get("editor")
        if jumpIndex:
            # Some editors make it possible to mark occurences of substrings, or
            # to jump to the line of the first occurence.
            # TODO: Find a better solution than hardcoding these, e.g. a config
            # option.
            line = text[:jumpIndex].count('\n')
            column = jumpIndex - (text[:jumpIndex].rfind('\n') + 1)
        else:
            line = column = 0
        # Linux editors. We use startswith() because some users might use parameters.
        if config.get("editor").startswith('kate'):
            command += " -l %i -c %i" % (line, column)
        elif config.get("editor").startswith('gedit'):
            command += " +%i" % (line + 1) # seems not to support columns
        elif config.get("editor").startswith('emacs'):
            command += " +%i" % (line + 1) # seems not to support columns
        elif config.get("editor").startswith('jedit'):
            command += " +line:%i" % (line + 1) # seems not to support columns
        elif config.get("editor").startswith('vim'):
            command += " +%i" % (line + 1) # seems not to support columns
        elif config.get("editor").startswith('nano'):
            command += " +%i,%i" % (line + 1, column + 1)
        # Windows editors
        elif config.get("editor").lower().endswith('notepad++.exe'):
            command += " -n%i" % (line + 1) # seems not to support columns

        command += ' %s' % tempFilename
        #print command
        return command

    def convertLinebreaks(self, text):
        if sys.platform=='win32':
            return text.replace('\r\n', '\n')
        # TODO: Mac OS handling
        return text

    def restoreLinebreaks(self, text):
        if text is None:
            return None
        if sys.platform=='win32':
            return text.replace('\n', '\r\n')
        # TODO: Mac OS handling
        return text

    def edit(self, text, jumpIndex = None, highlight = None):
        """
        Calls the editor and thus allows the user to change the text.
        Returns the modified text. Halts the thread's operation until the editor
        is closed.

        Returns None if the user didn't save the text file in his text editor.

        Parameters:
            * text      - a Unicode string
            * jumpIndex - an integer: position at which to put the caret
            * highlight - a substring; each occurence will be highlighted
        """
        text = self.convertLinebreaks(text)
        if config.get("editor"):
            tempFilename = '%s.%s' % (tempfile.mktemp(), config.get("editor_filename_extension"))
            tempFile = open(tempFilename, 'w')
            tempFile.write(text.encode(config.get("editor_encoding")))
            tempFile.close()
            creationDate = os.stat(tempFilename).st_mtime
            command = self.command(tempFilename, text, jumpIndex)
            os.system(command)
            lastChangeDate = os.stat(tempFilename).st_mtime
            if lastChangeDate == creationDate:
                # Nothing changed
                return None
            else:
                newcontent = open(tempFilename).read().decode(config.get("editor_encoding"))
                os.unlink(tempFilename)
                return self.restoreLinebreaks(newcontent)
        else:
            return self.restoreLinebreaks(wikipedia.ui.editText(text, jumpIndex = jumpIndex, highlight = highlight))

class ArticleEditor:
    joinchars = string.letters + '[]' + string.digits # join lines if line starts with this ones

    def __init__(self):
        self.set_options()
        self.site = mwclient.Site(config.get("site"), config.get("path"))
        self.site.login(config.get("username"), config.get("password"))
        self.setpage()

    def set_options(self):
        """Parse commandline and set options attribute"""
        my_args = []
        print "Ignoring pywikipedia config args"
        # for arg in wikipedia.handleArgs():
        #     my_args.append(arg)
        print "Reading from command line directly"
        for arg in sys.argv[1:]:
            my_args.append(arg)
        if len(my_args) == 0:
            raise Exception("specify pages to edit with --page article_name")
        parser = optparse.OptionParser()
        parser.add_option("-r", "--edit_redirect", action="store_true", default=False, help="Ignore/edit redirects")
        parser.add_option("-p", "--page", help="Page to edit")
        parser.add_option("-w", "--watch", action="store_true", default=False, help="Watch article after edit")
        #parser.add_option("-n", "--new_data", default="", help="Automatically generated content")
        (self.options, args) = parser.parse_args(args=my_args)

        # for convenience, if we have an arg, stuff it into the opt, so we
        # can act like a normal editor.
        if (len(args) == 1):
            self.options.page = args[0]

    def setpage(self):
        """Sets page and page title"""
        # site = wikipedia.getSite()
        # pageTitle = self.options.page or wikipedia.input(u"Page to edit:")
        # self.page = wikipedia.Page(site, pageTitle)
        pageTitle = self.options.page
        print "Requesting page: [[%s]]" % pageTitle
        self.page = self.site.Pages[pageTitle]
        print "We don't follow redirects to their targets"
        # if not self.options.edit_redirect and self.page.isRedirectPage():
        #     self.page = self.page.getRedirectTarget()

    def handle_edit_conflict(self):
        fn = os.path.join(tempfile.gettempdir(), self.page.title())
        fp = open(fn, 'w')
        fp.write(new)
        fp.close()
        wikipedia.output(u"An edit conflict has arisen. Your edit has been saved to %s. Please try again." % fn)

    def run(self):
        # try:
        #     old = self.page.get(get_redirect = self.options.edit_redirect)
        # except wikipedia.NoPage:
        #     old = ""
        old = self.page.edit()
        textEditor = TextEditor()
        new = textEditor.edit(old)
        if new and old != new:
            # wikipedia.showDiff(old, new)
            # changes = wikipedia.input(u"What did you change?")
            # comment = wikipedia.translate(wikipedia.getSite(), msg) % changes

            showDiff(old, new)
            summary = inputunicode(u"What did you change (summary)?")
            self.page.save(new, summary = summary)
            # try:
            #     self.page.put(new, comment = comment, minorEdit = False, watchArticle=self.options.watch)
            # except wikipedia.EditConflict:
            #     self.handle_edit_conflict(new)
        else:
            print (u"Nothing changed")

def main():
    app = ArticleEditor()
    app.run()

if __name__ == "__main__":
    main()

