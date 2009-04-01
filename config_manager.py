#!/usr/bin/env python
# encoding: utf-8
"""
config_manager.py

Created by Matt on 2009-02-22.
Copyright (c) 2009 Matt Gedigian. All rights reserved.

Upon import, this reads config from default location.
Then it is used by calling "get()" for particular keys

TODO: offer to create file if not found
TODO: allow mock structure for testing

"""
import os, sys
sys.path.append(os.path.dirname(__file__) + os.sep + 'mwclient') # or wherever you put it
try:
    import client as mwclient
except ImportError, e:
    print "Couldn't find mwclient"
    print "If you already have it, add it to your python path"
    print "else check it out in this directory with:"
    print "\tsvn co https://mwclient.svn.sourceforge.net/svnroot/mwclient/trunk/mwclient"
    print sys.path
    sys.exit()

class InvalidKeyException(Exception):
    def __init__(self, msg):
        self.msg = msg

class ConfigManager():    
    def __init__(self, configfile = '~/.mwclient/config.py'):
        self.configfile = configfile
        sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
        try:
            # this imports the config file
            import config
            print "Loaded config from", configfile
        except ImportError, e:
            print "Could not locate config file (%s)" % configfile
            print "mkdir %s " % os.path.dirname(os.path.expanduser(configfile))
            print "create file (%s) with the desired site and user information:" % configfile
            print
            print "site='www.sitename.com'             # fill this in as appropriate"
            print "path='/w/'                          # (default)"
            print "urlpath='/w/'                       # (default -- use '/w/index.php/' if no modrewrite)"
            print "username='username'                 # fill this in as appropriate"
            print "password='password'                 # fill this in as appropriate"
            print "editor = 'mate -w'"
            print "editor_filename_extension = '.wiki' # (default)"
            print "editor_encoding = 'utf-8'           # (default)"
            print "console_encoding = 'utf-8'          # (default)"
            sys.exit()

        self.default_config = { "editor_encoding":"utf-8", "console_encoding":"utf-8", "path":"/w/", "editor_filename_extension":".wiki" }

    def verify(self, lst):
        for i in lst:
            get(i)

    def get(self, key):
        import config
        if key in dir(config):
            return getattr(config, key)
        elif key in self.default_config:
            return self.default_config[key]
        else:
            raise InvalidKeyException("No value for '%s'" % key)


config_instance = None
# singleton
# but we want to do thing
def load(configfile = None):
    global config_instance
    if config_instance and config_instance.configfile == configfile:
        pass
    else:
        # reload configuration
        if configfile:
            config_instance = ConfigManager(configfile)
        else:
            config_instance = ConfigManager()
    return config_instance