#!/usr/bin/env python
# encoding: utf-8
"""
Symptoms.py

Created by Yeon Jin Lee on 2009-03-05.
"""
import CSVReader
import sys
import os
import string

import summary_tts

opts = {"limit":500, "format":"html"}
query = '{{#ask: [[Has symptom::+]] | ?Has symptom }}'
query_audio = '{{#ask: [[Has symptom audio::+]] | ?Has symptom audio }}'

def list_symptoms(disease, symptoms):
    """ Used to take a disease and a list of symptoms and produce a sentence.
    """
	return "The symptoms of " + disease + " include: " + ", ".join(symptoms) 

def write(filename, contents):
    """ Writes a (non-unicode) string to a new file 
    """
	f = open(filename, 'w')
	f.write(contents)
	f.close()

def read_into_files(symptoms_sentence, basename):
    """ Takes a sentence describing the symptoms and an article name
        Creates txt, aiff, and mp3 files of the sentence with filenames based on the article name.
    """
    basename = "symptoms/" + basename
    write(basename + ".txt", symptoms_sentence)

    make_aiff_cmd = "say -f \"%s.txt\" -o \"%s.aiff\""  % (basename, basename)
    make_mp3_cmd  = "lame --quiet \"%s.aiff \"%s.mp3\"" % (basename, basename)

    print "Running command....[%s]" % make_aiff_cmd
    summary_tts._cmd(None, ".", make_aiff_cmd)

    print "Running command....[%s]" % make_mp3_cmd
    summary_tts._cmd(None, ".", make_mp3_cmd)

def csv_query():
    """ Executes a query for symptoms
        Returns a dictionary, with diseases as keys, and lists of symptoms as values.
    """
    import csv
    import urllib
    # Execute a query for symptoms
	query_summary = '{{#ask: [[Has symptom::+]] | ?Has symptom }}'
	qs = query_module.Query(query_summary, {'format': "csv"})
	result = qs.execute()
	long_string=result['text']['*']

    # extract the title from the result (starts with "title=" and ends with """)
	my_regex= " title=\"(.*?)\""  
	matchObj= re.search(my_regex,long_string)
	title = matchObj.groups()[0]
	url = 'http://www.hesperian.net/health/' + title

    # write the csv file to disk ("CSV.txt")
	f = urllib.urlopen(url) 
	local_file = open('CSV.txt', 'w') #trying to create a file called csv but doesn't work...
	local_file.write(f.read()) 
	local_file.close()

    # read the csv file from disk
	fileReader = csv.reader(open ('CSV.txt' , 'r'), delimiter=',', quotechar='"')

    # expect two column format, column_1 = disease_name, column_2 = comma separated list of symptoms
	sd = dict()
	for row in fileReader:
		if len(row)==2:
			disease = row[0]
			symptoms = row[1].split(',')
			sd[disease]= symptoms 
	return sd
    	
def main(args=None):
    # make a dictionary from diseases to sentences listing the symptoms
    disease_dict = csv_query()
    for disease in disease_dict.keys():
        disease_dict[disease] = list_symptoms(disease, disease_dict[disease])

    # write the symptoms sentences to files named $disease_symptoms
    for disease, symptoms in disease_dict.items():
        read_into_files(symptoms, disease + '_symptoms')


if __name__ == '__main__':
	main()
