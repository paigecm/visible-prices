#!/usr/bin/env python
# -*- coding: utf-8 -*- #

import re
import os
import sys
import json
import fnmatch
from pprint import pprint
from rdflib import ConjunctiveGraph, Graph, Namespace, BNode, URIRef, Literal, RDF, RDFS, OWL, XSD, plugin, query
from rdflib.collection import Collection

vpq = Namespace("http://visibleprices.org/quotation/")
vps = Namespace("http://visibleprices.org/vp-schema#")
vp = Namespace("http://visibleprices.org/")

## Parse a single brat .ann file into a python dictionary:
def ann2dict(annfile):
    """ Takes a single brat annotation file (.ann), parses each line and generates a dictionary. So far, we're handling only entities 'T', relations 'R', and user annotations '#'. Not here handling brat Events (N-ary relations). The presence of such a structure will break this.
    """
    anndict = dict()
    for line in annfile:
        if line[0] == "#": # this sort of user annotation should only exist in document order, AFTER the entity it annotates
            nid, ent_eid, note_string = line.split('\t')
            entity, eid = ent_eid.split(' ', 1)
            anndict[eid]["notes"] = note_string
            
        elif line[0] == 'T':
            eid, ent_and_offsets, text = line.split('\t')
            entity, offsets = ent_and_offsets.split(' ', 1)
            offsets = [list([int(y) for y in x.split()]) for x in offsets.split(';')]
        
            if entity == "Quotation":
            # The Quotation entity serves a a proxy for the document as a whole so we're not preserving the offsets.
                anndict[eid] = {
                    "type": vps[entity],
                    "text": quote_txt,
                    "node": entities[entity](eid)
                }
            else:
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
                "note": note if note else None # likely to break if relations have notes.
            }
            
    return anndict
    
def dict2graph(d, g):
    """ Takes a single dictionary returned from ann2dict, and an existing ConjunctiveGraph (g) and adds triples to the Graph. Again, handling only the brat types T and R (Entity and Relation).
    """
    for i in d:
        entry = d[i]
        if re.match('T\d+', i):
            node = entry.get('node')
            ent_type = entry.get("type")
            text = entry.get("text")
            offsets = entry.get("offsets")
            g.add(( node, RDF.type, ent_type ))
            g.add(( node, vps.textData, Literal(text, datatype=XSD.string) ))
            if offsets:
                g.add(( node, vps.offsets, Literal(str(offsets), datatype=XSD.string) ))

            if entry.get("notes"):
                # Try to parse the 'notes' field as a json object, on ValueError exception,
                # the notes field will be interpreted as a string and added to the graph
                # as an rdfs:comment Literal()
                try:
                    bibdata = json.loads( entry["notes"] )
                    for p,o in bibdata.items():
                        if p == "Keywords":
                            # This might collide with the UI keyword annotation function
                            # remember Collection.append() if we need to integrate them.
                            kwnode = BNode()
                            kws = [Literal(x.strip(), datatype=XSD.string) for x in o.split(',')]
                            g.add(( node, vps.keyWords, kwnode ))
                            c = Collection(g, kwnode, kws)
                        else:
                            g.add(( node, vps[re.sub('\s+', '_', p)], Literal(o, datatype=XSD.string) ))
                            
                except ValueError:
                    g.add(( node, RDFS.comment, Literal(entry["notes"], datatype=XSD.string) ))
                
                        
        if re.match('R\d+', i):
            s = d[entry['sub']]['node']
            o = d[entry['obj']]['node']
            p = entry['prop']
            g.add(( s,p,o ))
            
    return g
    

if __name__ == "__main__":

    ## 'entities' dictionary used as a 'switch' statement:
    ## each key calls a function that returns the
    ## rdf node appropriate to that entity type.
    ## So that it might be extended different node types (?)
    ## or URI constructors.
    entities = {
        "Quotation": lambda x: quotation_URI,
        "PriceExpression": lambda x: quotation_URI + "#" + x,
        "PricedThing": lambda x: BNode(),
        "ValueExpression": lambda x: BNode(),
        "NormalizedValue": lambda x: BNode()
    }

    anngraph = ConjunctiveGraph()
    
    # use namespace_manager to bind namespaces for serialization
    anngraph.namespace_manager.bind('vp', URIRef("http://visibleprices.org/"))
    anngraph.namespace_manager.bind('vps', URIRef("http://visibleprices.org/vp-schema#"))
    anngraph.namespace_manager.bind('vpq', URIRef("http://visibleprices.org/quotation/"))

    try:
        brat_data_path = "/Users/jjc/Desktop/VP_revised_Jul_8/" #sys.argv[1]
        for doc in set(os.path.splitext(file)[0] for file in os.listdir(brat_data_path) if file.startswith("VP")):
            ann = open(brat_data_path + doc + ".ann", 'r')
            quote_txt = open(brat_data_path + doc + ".txt", 'r').read()
            qId = re.search("T\d+\tQuotation.*\t(.*)", ann.readline()).group(1)
            ann.seek(0)
            quotation_URI = URIRef(vpq + qId)
            d = ann2dict(ann)
            dict2graph(d, anngraph)
        print anngraph.serialize(format="turtle").replace("\n\"\"\"^^xsd", '"""^^xsd')

    except:
        print sys.exc_info()
        print "usage: python brat2rdf.py /path/to/brat/data/directory/\nThe 'turtle' serialized graph will be written to stdout\nBut you could write it to a file thus:\npython brat2rdf.py /path/to/brat/data/directory/ > /path/to/outfile"
                
###############################################################################    
    
    
