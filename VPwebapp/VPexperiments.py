#!/usr/bin/env python2.7
# -*- coding: utf-8 -*- #

import cgi
import cgitb
import re
import os
import sys
import json
import fnmatch
from hashlib import sha1
from pprint import pprint
from decimal import Decimal
import rdflib
from rdflib import ConjunctiveGraph, Graph, Namespace, BNode, URIRef, Literal, RDF, RDFS, OWL, XSD, plugin, query
from rdflib.collection import Collection
import decimal

import requests
import pygraphviz as pgv
import textwrap

import logging

logging.basicConfig(level=10)

cgitb.enable(format="text")

### Anglo-Saxon Pound calculations:
def tupleToPennies(t):
    """ reduce tuple of (£,s,d) to pennies """
    L,s,d = t
    L = L * 240
    s = s * 12
    return L + s + d    

def penniesToTuple(d):
    """ return (£,s,d) tuple from pennies """
    s, d = divmod(d, 12)
    return divmod(s, 20) + (d,)

def addASP(t1,t2):
    """ add two tuples (£,s,d) """
    v1 = tupleToPennies(t1)
    v2 = tupleToPennies(t2)
    return penniesToTuple(v1 + v2)

def subtractASP(t1,t2):
    """ subtract two tuples (£,s,d) """
    v1 = tupleToPennies(t1)
    v2 = tupleToPennies(t2)
    return penniesToTuple(v1 - v2)



### Generate RDF graph in memory and execute query:
oa = Namespace("http://www.w3.org/ns/oa#")
vps = Namespace("http://visibleprices.org/")


ggraph = ConjunctiveGraph()
ggraph.parse("data/testgraph.n3", format="n3") ## NB: if we're gonna write to the file, then the webserver process owner (_www in my case) has to own both the file and the directory it's in.

tquery = """
SELECT ?textdata ?headline ?pence
WHERE { ?s a vps:Quotation;
            vps:hasPriceExpression ?vpsPE .
                
        ?vpsPE a vps:PriceExpression;
                vps:textData ?textdata;
                vps:normalizedValue [
                    vps:pence ?pence
                ] .
        
        OPTIONAL {
            ?s schema:headline ?headline .
        }
                
        FILTER (?pence > 40 &&
                ?pence < 500)
    }
"""
#################### Keywords query experiments, process result ################
# keywordsQuery = """
# SELECT ?annotated_resource ?annotationURI ?user_comment ?keyword
# WHERE { ?annotationURI a oa:Annotation ;
#                     oa:hasTarget ?annotated_resource ;
#                     oa:hasBody [ vp:keyWords ?list ] .
#              
#               ?list rdf:rest*/rdf:first ?keyword  . # see: "property paths"
# 
# }
# """

# keywordsQuery = """
# CONSTRUCT { ?annotated_resource vps:hasKeywords ?keyword .}
# WHERE { ?annotationURI a oa:Annotation ;
#             oa:hasTarget ?annotated_resource ;
#             oa:hasBody [ vp:keyWords ?list ] .
#              
#         ?list rdf:rest*/rdf:first ?keyword  . # see: "property paths"
# 
# }"""

# keywordsQuery = """
# # failed, but on the right track:
# select ?annotated_resource (GROUP_CONCAT(?keyword ; separator = ', ') as ?kwds)
# WHERE { ?annotationURI a oa:Annotation ;
#                     oa:hasTarget ?annotated_resource ;
#                     oa:hasBody [ vp:keyWords ?list ] .
#              
#               ?list rdf:rest*/rdf:first ?keyword  . # see: "property paths"
# 
# }
# # # """
# kwRes = ggraph.query(keywordsQuery)
# # # kwDict = {b['?annotated_resource'].toPython(): [k['?keyword'].toPython() for k in kwRes.bindings] for b in kwRes.bindings}
# # 
# # ## that dictionary comprehension is the equivalent of the following for loop,
# # ## but I'm not sure we gain anything by it
# # # for b in kwRes.bindings:
# # #     key = b['?annotated_resource'].toPython()
# # #     if not key in kwDict:
# # #             kwDict[key] = [b['?keyword'].toPython()]
# # #     else:
# # #             kwDict[key].append(b['?keyword'].toPython())
# # #
# print kwRes.serialize(format="turtle")
###############################################################################

################# GENERATE RDF FROM BRAT ANNOTATION DATA ######################
tstdoc = "/Users/jjc/Sites/VisiblePrices/VP8.ann"
base_path, ext = os.path.splitext(tstdoc)
doc_path = base_path + '.txt'
doctext = open(doc_path, "r").read()

qId = os.path.basename(tstdoc).split('.')[0]

vpq = Namespace("http://visibleprices.org/quotation/")
vps = Namespace("http://visibleprices.org/vp-schema#")
vp = Namespace("http://visibleprices.org/")
this = URIRef(vpq + qId)
anngraph = Graph() # local graph for testing tstdoc
annfile = open (tstdoc, "r")

## Dictionary as 'switch' statement:
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
def ann2dict(annf):
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
        
        if line[0] == 'T':
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
    
## generate the dictionary:
d = ann2dict(annfile)

## add triples to the graph:
for i in d:
    entry = d[i]
    if re.match('T\d+', i):
        node = entry['node']
        type = entry["type"]
        text = entry["text"]
        offsets = entry["offsets"]
        anngraph.add(( node, RDF.type, type ))
        anngraph.add(( node, vps.textData, Literal(text, datatype=XSD.string) ))
        anngraph.add(( node, vps.offsets, Literal(str(offsets), datatype=XSD.string) ))
        
    if re.match('R\d+', i):
        s = d[entry['sub']]['node']
        o = d[entry['obj']]['node']
        p = entry['prop']
        anngraph.add(( s,p,o ))
        
print anngraph.serialize(format="turtle")    
###############################################################################    
    
    
### Annotate named subjects

def write_to_graph(g_in, testgraph):
    """ with some kind of formal storage layer, replace this with appropriate API calls. For now we'll just serialize the graph and overwrite the file. """
    for t in g_in.triples((None, None, None)):
        testgraph.add((t))
        f = open("data/testgraph.n3", "w")
        f.write(testgraph.serialize(format="turtle"))
        f.close()

def annotationExists(uri):
    uri = URIRef(uri)
    if (uri, None, None) in ggraph:
        return True
    

def annotation(target, user_name, comment, keywds=None):
    """thisAnnotation id is the full string, eg:
    http://visibleprices.org/user/jjon/annotation/92c53723ba5f1e162e7c44e8bf8c71d02ed4065a
    the last element being a hash (hashlib.sha1(oa:hastarget).hexdigest()) of this full string:
    http://visibleprices.org/quotations/q3
    TODO:
        * read up oa for use of BNode for body element
        * make keywds optional parameter
    """

    target = target
    thisAnnotationURI = "http://visibleprices.org/user/%s/annotation/%s" % (user_name, sha1(target).hexdigest()[:16])
    
    if annotationExists(thisAnnotationURI):
        return {'annotationExists': "You've already annotated this resource: %s \nPresumably you could make a separate annotation with a different username. If you start doing that, you should keep track of all your usernames. With authentication and session logic, this won't be necessary." % (target)}
    else:
        thisann = URIRef(thisAnnotationURI)
        g = Graph()
        bodyNode = BNode()
        keywordCollection = BNode()

        triples = [
            (thisann, RDF.type, oa.Annotation),
            (thisann, oa.hasTarget, URIRef(target)),
            (thisann, oa.hasBody, bodyNode),
            (bodyNode, vps.userComment, Literal(comment, datatype=XSD.string))
        ]
        for t in triples: g.add(t)
        
        if keywds:
            g.add((bodyNode, vps.keyWords, keywordCollection))
            kws = [Literal(x, datatype=XSD.string) for x in keywds]
            c = Collection(g, keywordCollection, kws)
        
        write_to_graph(g, ggraph)
        

        return {"serialized_annotation_triples": g.serialize(format='turtle')}


if __name__ == "__main__":
    form = cgi.FieldStorage()
    
    
## DEBUG at command line or in editor
#     class FakeStorage(dict):
#         def __init__(self, s=None):
#             self.value = s
#         def getvalue(self, k):
#             return self[k]
#
#     form = FakeStorage()
#     form["target"] = "http://visibleprices.org/vp-schema#person1"
#     form["username"] = "jfdks"
#     form["comment"] = "person 1 is a foobar"
#     form["keywords"] = "fee, fie, fo fum"

    try:
        if "namedSubjects" in form:
            print "Content-Type: application/json\n"
            print "\n"
            print json.dumps(list(set(x.toPython() for x in ggraph.subjects() if not isinstance(x, BNode))))

        if "sparqlQuery" in form:
            query = form.getvalue("sparqlQuery")
            result = ggraph.query(query)
            
            print "Content-Type: text/plain\n"
        
            if re.search('select\s+\?', query, re.IGNORECASE):
                for x in result.bindings:
                    for y in x.items():
                        print "%s: %s" % y
                    print "~~~~~~~~~~~~\n"
            
            elif re.search('construct\s+{', query, re.IGNORECASE):
                print result.serialize(format="turtle")

        ##need to handle 'ASK' queries too; rdflib does not support 'DESCRIBE' yet.

        if "serialize" in form:
            sformat = form['serialize'].value
            print "Content-Type: text/plain\n"
            print "\n"
            print ggraph.serialize(format = sformat)

        if "target" in form:
            target = form.getvalue("target")
            usr = form.getvalue("username")
            comment = form.getvalue("comment")
            keywds = form.getvalue("keywords")
            keywds = [x.strip() for x in keywds.split(",")] if keywds else None
            
            print "Content-Type: application/json\n"
            print "\n"
            print json.dumps(annotation(target, usr, comment, keywds))

        if not form:
            print "Content-Type: text/plain\n"
            print "\n"
            print "you lookin' fer sumpin?"
        
    except StandardError as e:
        print "Content-Type: text/html\n"
    
        print e


################### related example data below this line #######################
###################    not needed for the script above   #######################


# see http://qudt.org/vocab/unit#
GBPqudt = """
<rdf:RDF 
xmlns:html="http://uispin.org/html#" 
xmlns:lm-cat="http://www.linkedmodel.org/catalog/lm#" 
xmlns:quantity-1.1="http://qudt.org/1.1/schema/quantity#" 
xmlns:letrs="http://uispin.org/letrs#" 
xmlns:lm-cat-1.2="http://www.linkedmodel.org/1.2/catalog/lm#" 
xmlns:arg="http://spinrdf.org/arg#" 
xmlns:qudt-1.1="http://qudt.org/1.1/schema/qudt#" 
xmlns:omv="http://omv.ontoware.org/2005/05/ontology#" 
xmlns:qudt-unit-1.1="http://qudt.org/1.1/vocab/unit#" 
xmlns:qudt-quantity-1.1="http://qudt.org/1.1/vocab/quantity#" 
xmlns:quantity="http://qudt.org/schema/quantity#" 
xmlns:qudt-dimension="http://qudt.org/vocab/dimension#" 
xmlns:void="http://rdfs.org/ns/void#" 
xmlns:dtype="http://www.linkedmodel.org/schema/dtype#" 
xmlns:lmdoc="http://www.linkedmodel.org/oui/lmdoc#" 
xmlns:tui="http://uispin.org/tui#" 
xmlns:sp="http://spinrdf.org/sp#" 
xmlns:style="http://uispin.org/style#" 
xmlns:qudt-quantity="http://qudt.org/vocab/quantity#" 
xmlns:voag-1.0="http://voag.linkedmodel.org/1.0/schema/voag#" 
xmlns:owl="http://www.w3.org/2002/07/owl#" 
xmlns:let="http://uispin.org/let#" 
xmlns:dimension="http://qudt.org/schema/dimension#" 
xmlns:xhtml="http://topbraid.org/xhtml#" 
xmlns:spl="http://spinrdf.org/spl#" 
xmlns:unit="http://qudt.org/vocab/unit#" 
xmlns:sxml="http://topbraid.org/sxml#" 
xmlns:qudt-cat="http://qudt.org/catalog/qudt#" 
xmlns:fn="http://www.w3.org/2005/xpath-functions#" 
xmlns:vaem-1.2="http://www.linkedmodel.org/1.2/schema/vaem#" 
xmlns:voag="http://voag.linkedmodel.org/schema/voag#" 
xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" 
xmlns:dimension-1.1="http://qudt.org/1.1/schema/dimension#" 
xmlns:spin="http://spinrdf.org/spin#" 
xmlns:foaf="http://xmlns.com/foaf/0.1/" 
xmlns:qudt="http://qudt.org/schema/qudt#" 
xmlns:smf="http://topbraid.org/sparqlmotionfunctions#" 
xmlns:qudt-cat-11="http://qudt.org/1.1/catalog/qudt#" 
xmlns:xsd="http://www.w3.org/2001/XMLSchema#" 
xmlns:composite="http://www.topbraid.org/2007/05/composite.owl#" 
xmlns:qudt-dimensionalunit-1.1="http://qudt.org/1.1/vocab/dimensionalunit#" 
xmlns:vaem="http://www.linkedmodel.org/schema/vaem#" 
xmlns:catalog="http://www.linkedmodel.org/schema/catalog#" 
xmlns:dtype-1.0="http://www.linkedmodel.org/1.0/schema/dtype#" 
xmlns:skos="http://www.w3.org/2004/02/skos/core#" 
xmlns:css="http://uispin.org/css#" 
xmlns:ui="http://uispin.org/ui#" 
xmlns:dc="http://purl.org/dc/elements/1.1/" 
xmlns:spra="http://spinrdf.org/spra#" 
xmlns:vann="http://purl.org/vocab/vann/" 
xmlns:qudt-dimension-1.1="http://qudt.org/1.1/vocab/dimension#" 
xmlns:catalog-1.0="http://www.linkedmodel.org/1.2/schema/catalog#" 
xmlns:creativecommons="http://creativecommons.org/ns#" 
xmlns:spr="http://spinrdf.org/spr#" 
xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#" xml:base="http://qudt.org/vocab/unit">
<rdf:Description rdf:about="#PoundSterling">
    <skos:exactMatch rdf:resource="http://dbpedia.org/resource/Pound_sterling"/>
    <qudt:description>United Kingdom</qudt:description>
    <qudt:currencyExponent rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">2</qudt:currencyExponent>
    <qudt:code rdf:datatype="http://www.w3.org/2001/XMLSchema#string">826</qudt:code>
    <qudt:abbreviation rdf:datatype="http://www.w3.org/2001/XMLSchema#string">GBP</qudt:abbreviation>
    <rdfs:label rdf:datatype="http://www.w3.org/2001/XMLSchema#string">Pound Sterling</rdfs:label>
    <rdf:type rdf:resource="http://qudt.org/schema/qudt#CurrencyUnit"/>
</rdf:Description>
</rdf:RDF>
"""

# for rst-currency see http://personal.sirma.bg/vladimir/crm/art/thesauri.ttl.html
GBPrst = """
@prefix crm:   <http://erlangen-crm.org/current/> .
@prefix owl:   <http://www.w3.org/2002/07/owl#> .
@prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>.
@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos:  <http://www.w3.org/2004/02/skos/core#> .
@prefix unit:  <http://qudt.org/vocab/unit#> .
@prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .
@prefix rst-currency:      <http://www.researchspace.org/thesaurus/currency/> .
rst-currency:GBP a crm:E55_Type, skos:Concept;
  skos:inScheme rst-currency:; crm:P2_has_type rst-currency:;
  rdfs:label "GBP".
"""

ex2 = """
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix rst-currency: <http://www.researchspace.org/thesaurus/currency/> .
@prefix crm: <http://erlangen-crm.org/current/> .

rst-currency:HFL a crm:E55_Type, skos:Concept;
  skos:inScheme rst-currency:; crm:P2_has_type rst-currency:;
  rdfs:label "HFL", "florijnen". # I assume they are the same
rst-currency:GBP a crm:E55_Type, skos:Concept;
  skos:inScheme rst-currency:; crm:P2_has_type rst-currency:;
  rdfs:label "GBP".
rst-currency:FRF a crm:E55_Type, skos:Concept;
  skos:inScheme rst-currency:; crm:P2_has_type rst-currency:;
  rdfs:label "FRF".
"""

