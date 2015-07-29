#!/usr/bin/env python
# -*- coding: utf-8 -*- #

import re
import os
import sys
import json
import traceback
from urlparse import urlparse
from pprint import pprint
from rdflib import ConjunctiveGraph, Graph, Namespace, BNode, URIRef, Literal, RDF, RDFS, OWL, XSD, plugin, query
from rdflib.collection import Collection

bf = Namespace("http://bibframe.org/vocab/")
bibo = Namespace("http://purl.org/ontology/bibo/")
dc = Namespace("http://purl.org/dc/elements/1.1/")
dcterms = Namespace("http://purl.org/dc/terms/")
oa = Namespace("http://www.w3.org/ns/oa#")
rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
schema = Namespace("http://schema.org/vocab/")
unit = Namespace("http://qudt.org/vocab/unit#")
vp = Namespace("http://visibleprices.org/")
vpq = Namespace("http://visibleprices.org/quotation/")
vps = Namespace("http://visibleprices.org/vp-schema#")
xml = Namespace("http://www.w3.org/XML/1998/namespace")
xsd = Namespace("http://www.w3.org/2001/XMLSchema#")


# Create an empty ConjunctiveGraph to hold our triples
anngraph = ConjunctiveGraph()

# use namespace_manager to bind namespaces for serialization
anngraph.namespace_manager.bind('vp', URIRef("http://visibleprices.org/"))
anngraph.namespace_manager.bind('vps', URIRef("http://visibleprices.org/vp-schema#"))
anngraph.namespace_manager.bind('vpq', URIRef("http://visibleprices.org/quotation/"))
anngraph.namespace_manager.bind('dc', URIRef("http://purl.org/dc/elements/1.1/"))
anngraph.namespace_manager.bind('dcterms', URIRef("http://purl.org/dc/terms/"))
anngraph.namespace_manager.bind('bibo', URIRef("http://purl.org/ontology/bibo/"))
anngraph.namespace_manager.bind('bf', URIRef("http://bibframe.org/vocab/"))
anngraph.namespace_manager.bind('oa', URIRef("http://www.w3.org/ns/oa#"))
anngraph.namespace_manager.bind('schema', URIRef("http://schema.org/vocab/"))
anngraph.namespace_manager.bind('unit', URIRef("http://qudt.org/vocab/unit#"))

# in dict2graph(), we need to be able to call the namespace with a string when
# parsing the metadata (spreadsheet columns)
nsdict = dict(anngraph.namespaces())

## 'entities' dictionary used as a 'switch' statement:
## each key calls a function that returns the
## rdf node appropriate to that entity type.
## So that it might be extended different node types (?)
## or URI constructors. Too clever? Unnecessary?
entities = {
    "Quotation": lambda x: quotation_URI,
    "PriceExpression": lambda x: quotation_URI + "#" + x,
    "PricedThing": lambda x: BNode(),
    "ValueExpression": lambda x: BNode(),
    "NormalizedValue": lambda x: BNode()
}


def ann2dict(annfile):
    """ Takes a single brat annotation file (.ann), parses each line and
    generates a dictionary. So far, we're handling only entities 'T', relations
    'R', and user annotations '#'. Not here handling brat Events (N-ary
    relations). The presence of such a structure will break this. """
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
                "note": note if note else None # untested. Likely to break if relations have notes.
            }
            
    return anndict

def test_string_for_URI(st):
    """ Convenience function: A crude test to distinguish between resources and
    Literals. It just parses the string and if there's a scheme (html, ftp,
    whatever) and a netloc (a domain name) it treats it as a resource and
    returns a URIRef(), if not, it assumes it's a string literal and returns an
    xsd string Literal() """
    return URIRef(st) if (urlparse(st).netloc and urlparse(st).scheme) else Literal(st, datatype=XSD.string)
    
    
def dict2graph(d, g):
    """ Takes a single dictionary returned from ann2dict, and an existing
    ConjunctiveGraph (g) and adds triples to the Graph. Again, handling only the
    brat types T and R (Entity and Relation). """
    
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
                            kws = [test_string_for_URI(x.strip()) for x in o.split(',')]
                            g.add(( node, vps.keyWords, kwnode ))
                            c = Collection(g, kwnode, kws)
                            
                        else:
                            # This depends on metadata fields being QNames
                            ns, pred = p.split(":")
                            g.add(( node, URIRef(nsdict[ns] + pred), test_string_for_URI(o) ))
                            
                except ValueError:
                    g.add(( node, RDFS.comment, Literal(entry["notes"], datatype=XSD.string) ))
                
                        
        if re.match('R\d+', i):
            s = d[entry['sub']]['node']
            o = d[entry['obj']]['node']
            p = entry['prop']
            g.add(( s,p,o ))
            
    return g
    

if __name__ == "__main__":

# the main processing loop.
    # For each document starting with VP
    # read the markup data
    # read the text data for the quotation
    # get the quotation ID
    # go back to the top of the .ann file
    # create the Quotation node for the graph
    # turn the .ann markup data into a dictionary. ann2dict() reads a single .ann file's data.
    # read the data in from dict into the graph. dict2graph() adds triples to graph in memory.

    try:
        brat_data_path = sys.argv[1] # path to dir with .txt and .ann files
        
        for doc in set(os.path.splitext(file)[0] for file in os.listdir(brat_data_path) if file.startswith("VP")):
            ann = open(brat_data_path + doc + ".ann", 'r')                      
            quote_txt = open(brat_data_path + doc + ".txt", 'r').read()         
            qId = re.search("T\d+\tQuotation.*\t(.*)", ann.readline()).group(1) 
            ann.seek(0)
            quotation_URI = URIRef(vpq + qId)
            d = ann2dict(ann)
            dict2graph(d, anngraph)
        
        # anngraph has now been built in memory, one document at a time. Now serialize the graph and print it out.
        print anngraph.serialize(format="turtle").replace("\n\"\"\"^^xsd", '"""^^xsd')

    except:
        extype, exvalue, extb = sys.exc_info()
        print extype, exvalue
        print traceback.print_tb(extb)
        
        print "usage: python brat2rdf.py /path/to/brat/data/directory/\nThe 'turtle' serialized graph will be written to stdout\nBut you could write it to a file thus:\npython brat2rdf.py /path/to/brat/data/directory/ > /path/to/outfile"
                
###############################################################################    
