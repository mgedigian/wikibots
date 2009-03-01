import os
import sys
import config_manager as config
import client as mwclient
import TableParse    

class Query(object):
    def __init__(self, query, opts=None, site=None):
        global verbose
        verbose=False
        if not site:
            print "Connecting as %s to http://%s%s" % (config.get("username"), config.get("site"), config.get("path"))
            self.site  = mwclient.Site(config.get("site"), path=config.get("path"))
            self.site.login(config.get("username"),config.get("password"))
        else:
            self.site = site    
        if opts:
            query_parts = query.split("}}")
            query = query_parts[0] + " | " + " | ".join(k + "=" + str(v) for k,v in opts.items()) + "}}" + query_parts[1]

        if verbose:
            print "Parsing query:", query
        results = self.site.parse(query)
        if opts["format"].lower() == "csv":
            csv  = results['text']['*']
            print "NO CSV PROCESSING?"
            return
        else:
            html = results['text']['*']
            if verbose:
                print "Got html", html
            self.lol = TableParse.parse(html)
        if verbose:
            print "Parsed return", str(type(self.lol)), 'of length', len(self.lol)

    def result_lol(self):
        return self.lol
        
    def result_dict(self):
        result_dict = {}
        if len(self.lol):
            for row in self.lol:
                if len(row) == 0: continue
                try:
                    key = row[0]
                    val = row[1]
                    if len(key) > 0:
                        result_dict[key] = val
                except:
                    print "Bad Row", row
        return result_dict
    

if __name__ == '__main__':
    global verbose
    verbose = True
    opts = {"limit":500, "format":"html"}
    if len(sys.argv) == 1:
        query = '{{#ask: [[Category::Disease]] [[Summary::+]] | ?Summary }}'
    elif len(sys.argv) == 2:
        query = sys.argv[1]
    else:
        print "Only take one argument"
    q = Query(query, opts)
    summary_dict = q.result_dict()
    for article,summary in summary_dict.items():
        print article + ":\n  " + summary + "\n"
    
