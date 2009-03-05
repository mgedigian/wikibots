#
# Usage: 
#  python bot.py BOOK_ABBREVIATION
#  

import os.path
import sys
import config_manager as config
import client as mwclient

log = open("command.log", "a")

# connect to the site
print "Connecting as %s to http://%s%s" % (config.get("username"), config.get("site"), config.get("path"))
site  = mwclient.Site(config.get("site"), path=config.get("path"))
site.login(config.get("username"),config.get("password"))

def process_section(section_name, template_line):
    print "\tAdd", template_line, "to", section_name, "(if not there already)"    
    page = site.Pages[section_name]
    text = page.edit()
    if template_line in text:
        print( 'Skipping %s because already processed' % section_name)
        return
    if "{{Next section" in text or "{{Previous and next sections" in text or "{{Previous section" in text:
        print( 'Skipping %s because already has some pointer in it' % section_name)
        log.write ( 'Skipping %s because already has some pointer in it' % section_name)
        return
    page.save(text.rstrip() + "\n" + template_line, summary = 'Added adjacent section pointers')
    
def process_chapter(chapter, sections_filename=None, templates_filename=None):
    if not sections_filename:
        sections_filename = chapter + "_topics.txt"
    if not os.path.exists("sections" + os.sep + sections_filename):
        return
    if not templates_filename:
        templates_filename = chapter + "_topics.txt.output"
    if not os.path.exists("sections" + os.sep + templates_filename):
        return

    print "Processing", chapter, "from file", sections_filename, "and", templates_filename
    s = open("sections" + os.sep + sections_filename, "r")
    sections = s.readlines()
    sections = [section.strip() for section in sections]

    t = open("sections" + os.sep + templates_filename, "r")
    templates = t.readlines()
    templates = [template.strip() for template in templates]

    if len(sections) != len(templates):
        log.write ( 'Skipping %s because length mismatch between sections (%d) and templates (%d)\n' % chapter, len(sections), len(templates))
        return
    for i in xrange(len(sections)):
        process_section(sections[i], templates[i])
        
    
def main(args=None):
    if args == None:
        args = sys.argv[1:]
    if not args:
        args = ["WTND"]
    for book in args:
        print "Processing", book
        for i in xrange(50):
            if i == 1:
                continue
            process_chapter("%s_Chapter_%d" % (book, i))
            

if __name__ == '__main__':
    main()