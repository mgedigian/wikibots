"""
This gets query results as HTML tables, rather than CSV
"""
import query as query_module
import os
import config_manager
import client as mwclient
import codecs

config = config_manager.load()
opts = {"limit":500, "format":"html"}
query_text = '{{#ask: [[Summary::+]] | ?Summary }}'
query_audio = '{{#ask: [[Summary audio::+]] | ?Summary_audio }}'

import subprocess
NO_EXECUTE = False
def _cmd(output, dir, *cmditems):
    """Internal routine to run a shell command in a given directory."""

    cmd = ("cd \"%s\"; " % dir) + " ".join(cmditems)
    if output:
        output.write("+ %s\n" % cmd)
    if NO_EXECUTE:
        return 0
    child = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    child.stdin.close()
    while 1:
        line = child.stdout.readline()
        if not line:
            break
        if output:
            output.write(line)
    return child.wait()

def requires_tts(str, directory, txt_file):
    """ Test whether contents of txt_file match that of str, or if they are out of date
        If stale, the existing file is moved out of the way
    """
    if (os.path.exists(directory + os.sep + txt_file)):
        f = codecs.open(directory + os.sep + txt_file, "r", "utf-8" )
        contents = f.read() # Returns a Unicode string from the UTF-8 bytes in the file
        f.close()
        if (str.strip() == contents.strip()):
            print "\tExisting audio is current"
            return False
        else:
            print "\tExisting audio is stale"
            print "\t" + contents.strip()
            print "\t" + str.strip()
            os.rename(directory + os.sep + txt_file, directory + os.sep + txt_file + ".bak")
    return True

def tts(str, m_filename_txt, m_filename_mp3):
    """from contents of str, creates txt and mp3 files
       if txt_file exists, it is compared to str
          if unchanged, mp3 is not generated, false is returned
          if changed,   mp3 is     generated, true  is returned
    """
    cmd = "text2mp3 \"tts/%s\" \"tts/%s\"" % (m_filename_txt, m_filename_mp3)
    if (os.path.exists("tts/" + m_filename_mp3)):
        os.rename("tts/" + m_filename_mp3, "tts/" + m_filename_mp3 + ".bak")
    try:
        print "\tRunning", cmd
        _cmd(None, ".", cmd)
    except Exception, e:
        print "\tException doing tts of "
        print "\t", m_filename_txt, os.path.exists("tts/" + m_filename_txt)
        print "\t", m_filename_mp3, os.path.exists("tts/" + m_filename_mp3)

def prepend(article, top_text, site):
    page = site.Pages[article]
    text = page.edit()
    if top_text:
        new_text = top_text + u'\n' + text
        page.save(new_text, summary = 'Prepended')
    else:
        print "No change to", article


def main():
    global config
    username = config.get("username")
    password = config.get("password")
    sitename = config.get("site")
    sitepath = config.get("path")

    print "Connecting as %s to http://%s%s" % (username, sitename, sitepath)
    site  = mwclient.Site(sitename, path=sitepath)
    site.login(username, password)
    
    query_for_text = query_module.Query(query_text, opts, site=site)
    result = query_for_text.execute()
    lol = query_module.html2lol(result)
    text_dict = query_module.lol2dict(lol,single_item=True)

    query_for_audio = query_module.Query(query_audio, opts, site=site)
    result = query_for_audio.execute()
    lol = query_module.html2lol(result)
    audio_dict = query_module.lol2dict(lol, single_item=True)

    print "Comparing %d text results to" % len(text_dict)
    print "       to %d audio" % len(audio_dict)
    no_audio = []
    for k in text_dict:
        if not k in audio_dict:
            no_audio.append(k)
    if no_audio:
        print "These %d articles have text but no audio:" % len(no_audio)
        print "\t" + "\t\n".join(no_audio)
    
    for article, summary in text_dict.items():
        if len(article.strip()) == 0: continue
        print "\n\nProcessing article '%s' : %s" % (article, summary)
        m_filename_txt = article.replace(" ", "_") + ".txt"
        m_filename_mp3 = article.replace(" ", "_") + ".mp3"
        if requires_tts(summary, "tts", m_filename_txt):
            print "\tUpdating summary"
            out = file( "tts" + os.sep + m_filename_txt, "w" )
            out.write( codecs.BOM_UTF8 )
            out.write( summary.encode( "utf-8" ) )
            out.close()
            
            tts(summary, m_filename_txt, m_filename_mp3)
            print "\tUploading mp3"
            if (os.path.exists('tts/%s' % m_filename_mp3)):
                print "python upload.py -keep -noverify \"tts/%s\"" % m_filename_mp3
                # mwclient can only upload images, not audio files
                # site.upload(open('tts/%s' % m_filename_mp3), m_filename_mp3, '%s summary audio' % article, ignore=True)
            else:
                print "*\tERROR creating mp3, upload skipped"
        if article in audio_dict:
            print "\tAlready has audio linked"
        else:
            print "\tAdding audio template to link the audio file"
            prepend(article, "{{Audio|Summary|%s}}" % m_filename_mp3, site)
    
if __name__ == '__main__':
    main()