#!/usr/bin/python
# -*- coding: utf-8 -*-

#########Download spreadsheet as csv and run this script on the resulting file
#########to get a bunch of .txt and .ann files that can be uploaded to the brat
#########installation. The .ann files start out with minimal markup: the
#########Quotation entity and an AnnotatorNotes element that is a json literal
#########containing all the other metadata.


import csv
from pprint import pprint
import json

csvIn = csv.DictReader(open("/Users/jjc/Sites/VisiblePrices/May 2015 VP Data for Jon - Sheet1.csv","rU"))
qno = 1

for x in csvIn:
    # generate the .txt file
    qid = "VPex" + str(qno)
    txt = open("/Users/jjc/Sites/VisiblePrices/VP_revised_Jul_8/VPex" + str(qno) + ".txt", 'w')
    txt.write(qid + "\n" + x["Quote"].replace('"',''))
    txt.close()

    # generate the .ann file
    ann = open("/Users/jjc/Sites/VisiblePrices/VP_revised_Jul_8/VPex" + str(qno) + ".ann", 'w')
    
    #NB: the metadata dicts won't all have the same set of keys so watch out for KeyErrors
    metadata = {y[0]:y[1] for y in x.items() if y[1] and y[0] != "Quote"} 
    ann.write("""T1\tQuotation 0 %d\t%s\n#1\tAnnotatorNotes T1\t%s"""% (len(qid), qid, json.dumps(metadata))) 
    ann.close()
    qno += 1