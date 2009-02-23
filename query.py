import os
import sys
import config_manager as config
import client as mwclient
import TableParse    
    
if __name__ == '__main__':
    print "Connecting as %s to http://%s%s" % (config.get("username"), config.get("site"), config.get("path"))
    site  = mwclient.Site(config.get("site"), path=config.get("path"))
    site.login(config.get("username"),config.get("password"))

    results = site.parse('{{#ask: [[Category::Disease]] [[Summary::+]] | ?Summary | limit=500 }}')
    html = results['text']['*']
    print "Got html", html
    lol = TableParse.parse(html)
    print "Parsed return", str(type(lol))
    i = 1
    result_dict = {}
    for row in lol:
        # print "Parsed return row", str(type(row)), len(row)
        if len(row) == 0: continue
        result_dict[row[0].strip()] = row[1]
    for k,v in result_dict.items():
        print k + ":\n  " + v + "\n"
