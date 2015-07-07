#!/usr/bin/env python
# -*- coding: utf-8 -*- #

import re
import os
import sys
import json
from rdflib import ConjunctiveGraph, Graph, Namespace, BNode, URIRef, Literal, RDF, RDFS, OWL, XSD, plugin, query

## Nota Bene: This script assumes that the annotation.conf document in the brat
## installation will have been changed: the first line of each .txt file should
## contain a Quotation entity, rather than a QuotationID entity


vpq = Namespace("http://visibleprices.org/quotation/")
vps = Namespace("http://visibleprices.org/vp-schema#")
vp = Namespace("http://visibleprices.org/")

## the 'entities' dictionary is a 'switch' statement:
## each key calls a function that returns the
## rdf node appropriate to that entity type
entities = {
    "Quotation": lambda x: this,
    "PriceExpression": lambda x: this + "#" + x,
    "PricedThing": lambda x: BNode(),
    "ValueExpression": lambda x: BNode(),
    "NormalizedValue": lambda x: BNode()
}

## Parse the brat .ann file into a python dictionary:
def ann2dict(annfile):
    anndict = dict()
    for line in annfile:
        if line[0] == "#":
            nid, ent_eid, note_string = line.split('\t')
            entity, eid = ent_eid.split(' ', 1)
            anndict[nid] = {
                "node": entity,
                "note_string": note_string,
                "type": vps[entity]
            }
        
        elif line[0] == 'T':
            eid, ent_and_offsets, text = line.split('\t')
            entity, offsets = ent_and_offsets.split(' ', 1)
            offsets = [list([int(y) for y in x.split()]) for x in offsets.split(';')]
        
            anndict[eid] = {
                "type": vps[entity],
                "offsets": offsets,
                "text": text,
                "node": entities[entity](eid)
            }
            
        elif line[0] == "R":
            rid, prop, a1, a2, note = re.split('\s+', line, maxsplit=4)
        
            anndict[rid] = {
                "sub": a1.split(':')[1],
                "obj": a2.split(':')[1],
                "prop": vps[prop],
                "note": note if note else None
            }
            
    return anndict
    
def dict2graph(d, g):
    for i in d:
        entry = d[i]
        if re.match('T\d+', i):
            node = entry['node']
            type = entry["type"]
            text = entry["text"]
            offsets = entry["offsets"]
            g.add(( node, RDF.type, type ))
            g.add(( node, vps.textData, Literal(text, datatype=XSD.string) ))
            g.add(( node, vps.offsets, Literal(str(offsets), datatype=XSD.string) ))
        
        if re.match('R\d+', i):
            s = d[entry['sub']]['node']
            o = d[entry['obj']]['node']
            p = entry['prop']
            g.add(( s,p,o ))
    
    return g
    
anngraph = ConjunctiveGraph()
anngraph.namespace_manager.bind('vps', URIRef("http://visibleprices.org/vp-schema#"))
anngraph.namespace_manager.bind('vpq', URIRef("http://visibleprices.org/quotation/"))

try:
    brat_data_path = sys.argv[1]

    for x in set(os.path.splitext(file)[0] for file in os.listdir(brat_data_path)):
        ann = open(brat_data_path + x + ".ann", 'r')
        txt = open(brat_data_path + x + ".txt", 'r').read()
        qId = re.search("T\d+\tQuotation.*\t(.*)", ann.readline()).group(1)
        ann.seek(0)
        this = URIRef(vpq + qId)
        d = ann2dict(ann)
        dict2graph(d, anngraph)
    print anngraph.serialize(format="turtle").replace("\n\"\"\"^^xsd", '"""^^xsd')

except: print "usage: python brat2rdf.py /path/to/brat/data/directory/\nThe 'turtle' serialized graph will be written to stdout\nBut you could write it to a file thus:\npython brat2rdf.py /path/to/brat/data/directory/ > /path/to/outfile"
                
###############################################################################    
    
    