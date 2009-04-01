import os
import config_manager as config
import client as mwclient
import codecs

import subprocess
NO_EXECUTE = False

def touch(page):
    page.save(page.edit(), summary = 'Refreshed')
    
success = []
failure = []

def savecounter():
    out = file( "log_win.txt", "w" )
    out.write( codecs.BOM_UTF8 )
    for i in success:        
        out.write( i.encode( "utf-8" ) )
    out.close()

    out = file( "log_fail.txt", "w" )
    out.write( codecs.BOM_UTF8 )
    for i in failure:        
        out.write( i.encode( "utf-8" ) )
    out.close()

import atexit
atexit.register(savecounter)
   
if __name__ == '__main__':
    print "Connecting as %s to http://%s%s" % (config.get("username"), config.get("site"), config.get("path"))
    site  = mwclient.Site(config.get("site"), path=config.get("path"))
    site.login(config.get("username"),config.get("password"))

    namespaces = {
    0 :"Main",
    1 :"Talk",
    2 :"User",
    3 :"User talk",
    4 :"HealthWiki",
    5 :"HealthWiki talk",
    6 :"Image",
    7 :"Image talk",
    8 :"MediaWiki",
    9 :"MediaWiki talk",
    10:"Template",
    11:"Template talk",
    12:"Help",
    13:"Help talk",
    14:"Category",
    15:"Category talk",
    }
    
    everything = [(k, v, site.allpages(namespace=k)) for (k,v) in namespaces.items()]

    for k,v,g in everything:
        if k in (1,3,5,6,7,9,11,13,15):
            continue
        l = list(g)
        if len(l) == 0:
            continue
        print "%2d. \"%s\" (%d entries)" % (k, v, len(l))

        decorated = [ (page.name, page) for page in l ]
        decorated.sort()
        for pagename, page in decorated:
            try:
                touch(page)
                success.append(pagename)
            except KeyboardInterrupt, e:
                raise
            except Exception, e:
                print "Failed with", pagename
                failure.append(pagename)
            
    print "Successfully touched:", len(success)
    print "\n".join(success)
    print "\n"
    print "Failed to touch:", len(failure)
    print "\n".join(failure)

