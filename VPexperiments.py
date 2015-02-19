#!/usr/bin/env python
# -*- coding: utf-8 -*- #

#How about use: http://en.wikipedia.org/wiki/Anglo-Saxon_pound as URI?

# define serialized graph as string:
ex1 = """
@prefix bibo: <http://ex.org/bibo#> .
@prefix qudt: <http://qudt.org/schema/qudt#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix unit: <http://qudt.org/vocab/unit#> .
@prefix vp: <http://visibleprices.org/> .
@prefix vpq: <http://visibleprices.org/quotations/> .
@prefix vps: <http://visibleprices.org/vp-schema#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

unit:ASPound a qudt:CurrencyUnit ;
    rdfs:label "Anglo-Saxon Pound"^^xsd:string ;
    qudt:abbreviation "ASP"^^xsd:string ;
    qudt:description "Currency in Britain until 1971" ;
    skos:exactMatch <http://en.wikipedia.org/wiki/Anglo-Saxon_pound> .

vpq:q1 a vps:Quotation;
    vps:textData "Wheat, eight shillings and six-pence the bushel."^^xsd:string;
    vps:hasPriceExpression vp:pe1;
    bibo:bibdata "Placeholder. Whatever property is here should point to a resource containing all the necessary bibliographical data to precisely locate the quoted text."^^xsd:string .

vp:pe1 a vps:PriceExpression;
    vps:textData "Wheat, eight shillings and six-pence the bushel."^^xsd:string;
    vps:textOffsets "[[4, 52]]"^^xsd:string;
    vps:hasPricedThing [ a vps:ThingPriced ;
            vps:textData "Wheat, the bushel"^^xsd:string ;
            vps:textOffsets "[[4,9],[41,52]]"^^xsd:string ] ;
    vps:hasValueExpression [ a vps:ValueExpression ;
            vps:textData "eight shillings and six-pence"^^xsd:string ;
            vps:textOffsets "[[11, 40]]"^^xsd:string ] ;
            vps:normalizedValue [ a vps:NormalizedValue ;
                vps:normalizedValueDetail "A-S Pound expressed in pence"^^xsd:string;
                vps:currency unit:ASPound;
                vps:pence "102"^^xsd:decimal ] .
                
vpq:q2 a vps:Quotation;
    vps:textData "The Price of this most noble Anti-Syphilicon is but Six Shillings a Pot, which considering its extraordinary Efficacy, one Pot only being sufficient in most Cases to accomplish the Cure, is not a tenth Part of its Value"^^xsd:string ;
    vps:hasPriceExpression vp:pe2 ;
    bibo:bibdata "placeholder"^^xsd:string .
    
vp:pe2 a vps:PriceExpression;
    vps:textData "most noble Anti-Syphilicon is but Six Shillings a Pot"^^xsd:string ;
    vps:textOffsets "[[1,220]]"^^xsd:string ;
    vps:hasPricedThing [ a vps:ThingPriced ;
            vps:textData "Anti-Syphilicon a pot"^^xsd:string ;
            vps:textOffsets "[[30,45],[67,72]]"^^xsd:string ] ;
    vps:hasValueExpression [a vps:ValueExpression ;
            vps:textData "Six Shillings"^^xsd:string ;
            vps:textOffsets "[[53,66]]"^^xsd:string ] ;
            vps:normalizedValue [ a vps:NormalizedValue ;
                vps:normalizedValueDetail "A-S Pound expressed in pence"^^xsd:string;
                vps:currency unit:ASPound;
                vps:pence "72"^^xsd:decimal ] .
"""

# define query:
VPquery = u"""
select ?textdata ?pence
where { ?s a vps:Quotation;
            vps:textData ?textdata;
            vps:hasPriceExpression ?vpsPE .
                
        ?vpsPE a vps:PriceExpression;
                vps:normalizedValue [
                    vps:pence ?pence
                ] .
                
        filter (?pence > 70 &&
                ?pence < 105)
                
                
    }
"""

# import sys
# sys.path.insert(0, "/Users/jjc/ComputerInfo/RDF/rdflib/")

from rdflib import ConjunctiveGraph#, Graph, Namespace, BNode, URIRef, Literal, RDF, RDFS, OWL, XSD, plugin, query      
import decimal

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
g.parse(data=ex1, format="n3")

res = g.query(VPquery)
for x in res:
    print "quotation text: %s\n\
            price in pence: %s\n\
            price in ASP (Pounds, shillings, and pence): %s\n~~~~~~~~~~\n" % (x[0], x[1], penniesToTuple(eval(x[1])))


print '\n#################\n'
print g.serialize(format='n3')
    



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

