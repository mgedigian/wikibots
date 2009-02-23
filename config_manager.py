#!/usr/bin/env python
# encoding: utf-8
"""
config_manager.py

Created by Matt on 2009-02-22.
Copyright (c) 2009 Matt Gedigian. All rights reserved.
"""
import os, sys
sys.path.append('mwclient') # or wherever you put it
try:
    import client as mwclient
except ImportError, e:
    print "Couldn't find mwclient"
    print "If you already have it, add it to your python path"
    print "else check it out in this directory with:"
    print "\tsvn co https://mwclient.svn.sourceforge.net/svnroot/mwclient"
    sys.exit()

configfile = '~/.mwclient/config.py'
sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
try:
    import config
except ImportError, e:
    print "Create config file (%s), containing:" % configfile
    print "\tsite='www.sitename.com'"
    print "\tpath='/w/'                          # (default)"
    print "\tusername='username'"
    print "\tpassname='password'"
    print "\teditor = 'mate -w'"
    print "\teditor_filename_extension = '.wiki' # (default)"
    print "\teditor_encoding = 'utf-8'           # (default)"
    print "\tconsole_encoding = 'utf-8'          # (default)"
    sys.exit()

defaults = { "editor_encoding":"utf-8", "console_encoding":"utf-8", "path":"/w/", "editor_filename_extension":".wiki" }

def verify(lst):
    for i in lst:
        get(i)

def get(key):
    if key in dir(config):
        return getattr(config, key)
    elif key in defaults:
        return defaults[key]
    else:
        raise Exception("No value for '%s'" % key)
        
# if not config.path[-1] == "/":
#     config.path = config.path + "/"

