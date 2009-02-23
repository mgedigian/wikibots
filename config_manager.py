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
    print "\tsvn co https://mwclient.svn.sourceforge.net/svnroot/mwclient/trunk/mwclient"
    sys.exit()

configfile = '~/.mwclient/config.py'
sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
try:
    import config
except ImportError, e:
    
    print "Could not locate config file (%s)" % configfile
    print "mkdir %s " % os.path.dirname(os.path.expanduser(configfile))
    print "create file (%s) with the desired site and user information:" % configfile
    print
    print "site='www.sitename.com'             # fill this in as appropriate"
    print "path='/w/'                          # (default)"
    print "username='username'                 # fill this in as appropriate"
    print "password='password'                 # fill this in as appropriate"
    print "editor = 'mate -w'"
    print "editor_filename_extension = '.wiki' # (default)"
    print "editor_encoding = 'utf-8'           # (default)"
    print "console_encoding = 'utf-8'          # (default)"
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

