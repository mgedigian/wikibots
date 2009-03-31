import os
import sys
import config_manager as config
import client as mwclient
import getopt

verbose = False

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

class Query(object):
    global verbose
    def __init__(self, query, opts=None, site=None):
        if not site:
            print >> sys.stderr, "Connecting as %s to http://%s%s" % (config.get("username"), config.get("site"), config.get("path"))
            self.site  = mwclient.Site(config.get("site"), path=config.get("path"))
            self.site.login(config.get("username"),config.get("password"))
        else:
            self.site = site
        if not opts:
            self.opts = {}
        else:
            self.opts = opts;
        if not "format" in self.opts:
            self.opts["format"] = "html"
        query_parts = query.split("}}")
        self.query = query_parts[0] + " | " + " | ".join(k + "=" + str(v) for k,v in self.opts.items()) + "}}" + query_parts[1]
        
    def execute(self):
        if verbose:
            print "Parsing query:", self.query
        results = self.site.parse(self.query)
        if self.opts["format"].lower() == "html":
            result = results['text']['*']
            if verbose:
                print "Got html", result.encode("utf-8")
        else:
            result = results
        return result

    def result_lol(self):
        return self.lol
        

def html2lol(html):
    import TableParse    
    lol = TableParse.parse(html)
    if verbose:
        print "Parsed return", str(type(lol)), 'of length', len(lol)
    for l in lol:
        print "\t\t".join(l) + "\n"
    
def main(argv=None):
    if argv is None:
        argv = sys.argv

    global verbose
    limit = 500
    format = "html"
    reformat_html = False
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "hl:f:vr", ["help", "limit=", "format=", "verbose", "reformat"])
        except getopt.error, msg:
            raise Usage(msg)

        # option processing
        for option, value in opts:
            if option in ("-v", "--verbose"):
                verbose = True
            elif option in ("-h", "--help"):
                raise Usage(help_message)
            elif option in ("-l", "--limit"):
                limit = int(value)
            elif option in ("-f", "--format"):
                format = value
            elif option in ("-r", "--reformat"):
                reformat_html = True
            else:
                print "What is this:", option
                  
        if reformat_html and not format == "html":
            raise Usage("We can only reformat HTML")
        if len(args) == 0:
            query = '{{#ask: [[Category::Disease]] [[Summary::+]] | ?Summary }}'
        elif len(args) == 1:
            query = args[0]
        else:
            raise Usage("We only can handle a single query argument")

        opts = {"limit":limit, "format":format}
        q = Query(query, opts)
        result = q.execute();
        if reformat_html:
            html2lol(result)
        else:
            print result.encode("utf-8")
        # summary_dict = q.result_dict()
        # for article,summary in summary_dict.items():
        #     print article + ":\n  " + summary + "\n"
    except Usage, err:
        print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
        print >> sys.stderr, "\t for help use --help"
        return 2


if __name__ == "__main__":
    sys.exit(main())
