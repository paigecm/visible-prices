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
import decimal

import requests
import pygraphviz as pgv
import textwrap

import logging

logging.basicConfig(level=10)

cgitb.enable(format="text")

# define query:
VPquery = u"""
select ?textdata ?headline ?pence
where { ?s a vps:Quotation;
            vps:textData ?textdata;
            vps:hasPriceExpression ?vpsPE .
                
        ?vpsPE a vps:PriceExpression;
                vps:normalizedValue [
                    vps:pence ?pence
                ] .
        
        OPTIONAL {
            ?s schema:headline ?headline .
        }
                
        filter (?pence > 40 &&
                ?pence < 500)
                
                
    }
"""

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
g = ConjunctiveGraph()
g.parse("testgraph.n3", format="n3")
    

if __name__ == "__main__":
    form = cgi.FieldStorage()
    try:
        if "sparqlQuery" in form:
            query = unicode(form.getvalue('sparqlQuery'))
            result = g.query(query)
            
            print "Content-Type: text/plain\n"
        
            for x in result.bindings:
                for y in x.items():
                    print "%s: %s" % y
                print "~~~~~~~~~~~~\n"

        if "serialize" in form:
            sformat = form.getvalue('serialize_format')
            serialized_graph = pprint(g.serialize(format = sformat))
            print "Content-Type: text/plain\n"
            print "\n"
            print g.serialize(format = sformat)
    
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

