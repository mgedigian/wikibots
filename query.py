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
    """ Query class
        Initialized with a query, options, and a site.
          If no options are given, defaults to HTML
          If no site is given, reads from config file
        Has only a single execute method which executes the query 
          and reformats the results in some way
    """
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
        response = self.site.parse(self.query)
        if self.opts["format"].lower() == "html":
            result = response['text']['*']
            if verbose:
                print "Got html", result.encode("utf-8")
        elif self.opts["format"].lower() == "csv":
            # extract the title from the result (starts with "title=" and ends with """)
            response_body = response['text']['*']
            if verbose:
                print "Got response_body", response_body.encode("utf-8")
            # my_regex = " title=\"(.*?)\""  
            href_regex = "href=\"(.*?)\""  
            match = re.search(href_regex, response_body)
            href = match.groups()[0]
            url = 'http://' + config.get("site") + href

            # write the csv file to disk and read it back (could maybe simplify with StringIO)
            f = urllib.urlopen(url) 
            csv_data = f.read()
            f.close()

            csv_data_array = csv_data.split("\n")
            if verbose:
                print "CSV rows\n", "\n\n".join(csv_data_array)
            
            csv_reader = csv.reader(csv_data_array, delimiter=',', quotechar='"')
            
            results = []
            for row in csv_reader:
                results.append(row)
        	
        return results
        

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
        if format == "html" and reformat_html:
            html2lol(result)
        elif format == "csv":
            list_of_list = result
            print "\n\n".join(["\t".join(row) for row in result])
            
            # print result.encode("utf-8")
        else:
            print result.encode("utf-8")
    except Usage, err:
        print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
        print >> sys.stderr, "\t for help use --help"
        return 2


if __name__ == "__main__":
    sys.exit(main())
