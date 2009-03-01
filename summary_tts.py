import query as query_module
import os
import config_manager as config
import client as mwclient
import codecs

opts = {"limit":500, "format":"html"}
query_summary = '{{#ask: [[Summary::+]] | ?Summary }}'
query_summary_audio = '{{#ask: [[Summary audio::+]] | ?Summary_audio }}'

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

def requires_tts(str, txt_file):
    if (os.path.exists("tts/" + txt_file)):
        # f = open("tts/" + txt_file, "r")
        # contents = " ".join(f.readlines())
        f = codecs.open("tts/" + txt_file, "r", "utf-8" )
        contents = f.read() # Returns a Unicode string from the UTF-8 bytes in the file
        f.close()
        if (str.strip() == contents.strip()):
            print "\tExisting summary audio"
            return False
        else:
            print "\tExisting summary audio is out of date"
            print "\t" + contents.strip()
            print "\t" + str.strip()
            os.rename("tts/" + txt_file, "tts/" + txt_file + ".bak")
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
    
if __name__ == '__main__':
    print "Connecting as %s to http://%s%s" % (config.get("username"), config.get("site"), config.get("path"))
    site  = mwclient.Site(config.get("site"), path=config.get("path"))
    site.login(config.get("username"),config.get("password"))
    
    qs = query_module.Query(query_summary, opts, site=site)
    qsa = query_module.Query(query_summary_audio, opts, site=site)
    
    summary_dict = qs.result_dict()
    summary_audio_dict = qsa.result_dict()

    print "Comparing %d (of %d) summaries" % (len(summary_dict), len(qs.lol))
    print "Comparing %d (of %d) summaries audios" % (len(summary_audio_dict), len(qsa.lol))
    for k in summary_dict:
        if not k in summary_audio_dict:
            print k, "has summary, but no summary audio"
    
    for article, summary in summary_dict.items():
        print "Processing", article
        m_filename_txt = article.replace(" ", "_") + ".txt"
        m_filename_mp3 = article.replace(" ", "_") + ".mp3"
        if requires_tts(summary, m_filename_txt):
            print "\tUpdating summary"
            # m_text = open("tts/" + m_filename_txt, "w")
            # m_text.write(summary + "\n")
            # m_text.close()
            out = file( "tts/" + m_filename_txt, "w" )
            out.write( codecs.BOM_UTF8 )
            out.write( summary.encode( "utf-8" ) )
            out.close()
            
            tts(summary, m_filename_txt, m_filename_mp3)
            print "\tUploading mp3"
            if (os.path.exists('tts/%s' % m_filename_mp3)):
                print "python upload.py -keep -noverify \"tts/%s\"" % m_filename_mp3
                # site.upload(open('tts/%s' % m_filename_mp3), m_filename_mp3, '%s summary audio' % article, ignore=True)
            else:
                print "*\tERROR creating mp3, upload skipped"
        if article in summary_audio_dict:
            print "\tAlready has audio linked"
        else:
            print "\tAdding audio template to link the audio file"
            prepend(article, "{{Audio|Summary|%s}}" % m_filename_mp3, site)
