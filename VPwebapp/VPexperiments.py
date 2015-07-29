#!/usr/bin/env python
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
vp = Namespace("http://visibleprices.org/")
vpq = Namespace("http://visibleprices.org/quotations/")
vps = Namespace("http://visibleprices.org/vp-schema#")
unit = Namespace("http://qudt.org/vocab/unit#")

vpgraph = ConjunctiveGraph()
vpgraph.namespace_manager.bind('vp', URIRef("http://visibleprices.org/"))
vpgraph.namespace_manager.bind('vps', URIRef("http://visibleprices.org/vp-schema#"))
vpgraph.namespace_manager.bind('vpq', URIRef("http://visibleprices.org/quotation/"))
vpgraph.namespace_manager.bind('oa', URIRef("http://www.w3.org/ns/oa#"))
vpgraph.namespace_manager.bind('unit', URIRef("http://qudt.org/vocab/unit#"))

## NB: if we're gonna write to the file, then the webserver process owner (_www
## in my case) has to own both the file and the directory it's in.
vpgraph.parse("data/testgraph3.ttl", format="turtle")


### Annotate named subjects

def write_to_graph(g_in, testgraph):
    """ with some kind of formal storage layer, replace this with appropriate API calls. For now we'll just serialize the graph and overwrite the file. """
    for t in g_in.triples((None, None, None)):
        testgraph.add((t))
        f = open("data/testgraph3.ttl", "w")
        f.write(testgraph.serialize(format="turtle"))
        f.close()

def annotationExists(uri):
    uri = URIRef(uri)
    if (uri, None, None) in vpgraph:
        return True
    

def annotation(target, user_name, comment, keywds=None):
    """
    thisAnnotation id is the full string, eg:
    http://visibleprices.org/user/jjon/annotation/
    92c53723ba5f1e162e7c44e8bf8c71d02ed4065a the last element being an sha1 hash
    (hashlib.sha1(oa:hastarget).hexdigest()) of this full string:
    "http://visibleprices.org/quotations/q3". For readability we'll just use the
    first 16 digits of the hash.
    TODO: read up on oa for use of BNode for body element
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
        
        write_to_graph(g, vpgraph)
        

        return {"serialized_annotation_triples": g.serialize(format='turtle')}

### add NormalizedValues
def quotes_PriceExpressions(g):
    return json.dumps({quote:[pe for pe in g.objects(quote, vps.hasPriceExpression)] for quote in g.subjects(vps.hasPriceExpression, None)})

def addValue(peURI, pence):
    if list(vpgraph.objects(peURI, vps.hasNormalizedValue)):
        return "That PriceExpression already has a NormalizedValue"
        
    else:
        g = Graph()
        newNormalizedValue = BNode()
        g.add((peURI, vps.hasNormalizedValue, newNormalizedValue))
        g.add((newNormalizedValue, RDF.type, vps.NormalizedValue))
        g.add((newNormalizedValue, vps.currency, unit.ASPound))
        g.add((newNormalizedValue, vps.normalizedValueDetail, Literal("A-S Pound expressed in pence", datatype=XSD.string)))
        g.add((newNormalizedValue, vps.pence, Literal(pence, datatype=XSD.decimal)))
    
        write_to_graph(g, vpgraph)
    
        return "the following triples have been written to the graph at %s:\n\n%s" % (vpgraph.contexts().next().n3(), g.serialize(format="turtle"))


if __name__ == "__main__":
    form = cgi.FieldStorage()

    ## for DEBUG at command line or in editor
    class FakeStorage(dict):
        def __init__(self, s=None):
            self.value = s
        def getvalue(self, k):
            return self[k]

#     form = FakeStorage()
#     form["priceExpression"] = "http://visibleprices.org/quotation/VPex1#T2"

    try:
        if "addValue" in form:
            pe = URIRef(form.getvalue("peURI"))
            pence = form.getvalue("addValue")
            print "Content-Type: application/json\n"
            print "\n"
            print addValue(pe, pence)           
        
        if "getPriceExpressions" in form:
            print "Content-Type: application/json\n"
            print "\n"
            print quotes_PriceExpressions(vpgraph)
        
        if "namedSubjects" in form:
            print "Content-Type: application/json\n"
            print "\n"
            print json.dumps(list( set(x.toPython() for x in vpgraph.subjects() if not isinstance(x, BNode)) ))

        if "priceExpression" in form:
            pe = URIRef(form.getvalue("priceExpression"))
            print "Content-Type: application/json\n"
            print "\n"
            
            q = vpgraph.subjects(None, pe).next()
            text = vpgraph.objects(q, vps.textData).next()
            pedict = {pe.toPython():{a.toPython().split('#')[1]: b.toPython() for a,b in vpgraph.predicate_objects(pe)}}
            pedict[pe.toPython()]['inQuote'] = text
            print json.dumps(pedict)
            
        if "sparqlQuery" in form:
            query = form.getvalue("sparqlQuery")
            ns = dict(vpgraph.namespace_manager.namespaces())
            result = vpgraph.query(query, initNs=ns)
            
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
            print vpgraph.serialize(format = sformat)

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
