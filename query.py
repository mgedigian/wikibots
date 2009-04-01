import csv
import getopt
import os
import re
import sys
import urllib
from tempfile import NamedTemporaryFile

import config_manager
import client as mwclient

verbose = False
config = config_manager.load()

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
        elif self.opts["format"].lower() == "csv":
        	long_string = results['text']['*']

            # extract the title from the result (starts with "title=" and ends with """)
        	my_regex = " title=\"(.*?)\""  
        	match = re.search(my_regex,long_string)
        	title = match.groups()[0]
        	try:
        	    url_path = config.get("urlpath")
        	except config_manager.InvalidKeyException:
        	    url_path = config.get("path")
        	url = 'http://' + config.get("site") + url_path + title

            # write the csv file to disk ("CSV.txt")
        	f = urllib.urlopen(url) 
            # local_file = open('CSV.txt', 'w') #trying to create a file called csv but doesn't work...
        	local_file = NamedTemporaryFile()
        	local_file.write(f.read()) 
        	local_file_reader = open(local_file.name , 'r')
        	local_file.close()


            # read the csv file from disk
            # fileReader = csv.reader(open ('CSV.txt' , 'r'), delimiter=',', quotechar='"')
        	result = csv.reader(local_file_reader, delimiter=',', quotechar='"')
        else:
            result = results
        return result
        

def html2lol(html):
    import TableParse    
    lol = TableParse.parse(html)
    if verbose:
        print "Parsed return", str(type(lol)), 'of length', len(lol)
    return lol
    # for l in lol:
    #     print "\t\t".join(l) + "\n"

def lol2dict(lol, single_item = False):
    dictionary = {}
    for item in lol:
        if len(item) >= 2:
            if single_item:
                dictionary[item[0]] = item[1]
            else:
                dictionary[item[0]] = item[1:]
    return dictionary
    
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
        print q.query
        result = q.execute();
        if reformat_html:
            html2lol(result)
        else:
            print result.encode("utf-8")
    except Usage, err:
        print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
        print >> sys.stderr, "\t for help use --help"
        return 2


if __name__ == "__main__":
    sys.exit(main())
