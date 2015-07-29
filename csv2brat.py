#!/usr/bin/python
# -*- coding: utf-8 -*-

# Download spreadsheet as csv and run this script on the resulting file to get a
# bunch of .txt and .ann files that can be uploaded to the brat installation. The
# .ann files start out with minimal markup: the Quotation entity and an
# AnnotatorNotes element that is a json literal containing all the other metadata.


import csv
from pprint import pprint
import json

path_to_csv = "/path/to/csv"
path_to_brat_data_dir = "/path/to/brat/data/dir"
csvIn = csv.DictReader(open(path_to_csv, 'rU'))
qno = 1

for row in csvIn:
    # generate the .txt file
    qid = "VPex" + str(qno)
    txt = open(path_to_brat_data_dir + "VPex" + str(qno) + ".txt", 'w')
    txt.write(qid + "\n" + row["Quote"].replace('"',''))
    txt.close()

    # generate the .ann file
    ann = open(path_to_brat_data_dir + "VPex" + str(qno) + ".ann", 'w')
    
    # NB: the dictionary comprehension, as stated, tests for the existence of values `if i[1]`
    # so metadata dicts won't all have the same set of keys: watch out for KeyErrors
    metadata = {i[0]:i[1] for i in row.items() if i[1] and i[0] != "Quote"} 
    ann.write("""T1\tQuotation 0 %d\t%s\n#1\tAnnotatorNotes T1\t%s"""% (len(qid), qid, json.dumps(metadata))) 
    ann.close()
    qno += 1

# Generates the files, gives no feedback :^(
