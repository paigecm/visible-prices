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
@prefix schema: <http://schema.org> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix dc:   <http://purl.org/dc/elements/1.1/> .
@prefix vcard: <http://www.w3.org/2006/vcard/ns#> . @prefix rdfa: <http://www.w3.org/ns/rdfa#> .

unit:ASPound a qudt:CurrencyUnit ;
    rdfs:label "Anglo-Saxon Pound"^^xsd:string ;
    qudt:abbreviation "ASP"^^xsd:string ;
    qudt:description "Currency in Britain until 1971" ;
    skos:exactMatch <http://dbpedia.org/resource/Anglo-Saxon_pound> .

vpq:q1 a vps:Quotation;
    vps:textData "Wheat, eight shillings and six-pence the bushel."^^xsd:string;
    vps:hasPriceExpression vp:pe1;
    bibo:bibdata "Placeholder. Whatever property is here should point to a resource containing all the necessary bibliographical data to precisely locate the quoted text."^^xsd:string .

vp:pe1 a vps:PriceExpression;
    vps:textData "Wheat, eight shillings and six-pence the bushel."^^xsd:string;
    vps:textOffsets "[[4, 52]]"^^xsd:string;
    vps:hasPricedThing [ a vps:PricedThing ;
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
    vps:hasPricedThing [ a vps:PricedThing ;
        vps:textData "Anti-Syphilicon a pot"^^xsd:string ;
        vps:textOffsets "[[30,45],[67,72]]"^^xsd:string ] ;
    vps:hasValueExpression [a vps:ValueExpression ;
        vps:textData "Six Shillings"^^xsd:string ;
        vps:textOffsets "[[53,66]]"^^xsd:string ] ;
    vps:normalizedValue [ a vps:NormalizedValue ;
        vps:normalizedValueDetail "A-S Pound expressed in pence"^^xsd:string;
        vps:currency unit:ASPound;
        vps:pence "72"^^xsd:decimal ] .
 
 vpq:q3 a vps:Quotation;
 	vps:textData "The Norman Razor is the only one that will stand the test by which a Quick, Clean, and Easy Shave may be effected. It Is the most Novel and Perfect Razor of the day. See Testimonials. Black handles, 3s. 6d. Ivory, 5 s. each ; with Patent Guards, perfect security from cutting the face, 2s. each extra;"^^xsd:string ;
 	vps:hasPriceExpression vp:pe3 ;
 	vps:hasPriceExpression vp:pe4 ;
 	vps:hasPriceExpression vp:pe5 ;
 	dc:isPartOf <http://books.google.ca/books?id=tRhAAAAAcAAJ&pg=PP5#v=onepage&q&f=false> ;
 	schema:headline "The Norman Razor is the only one" ;
    bibo:bookSection "The Lancet General Advertiser" ;
    bibo:pages "1" ;
    bibo:bibdata "Placeholder. I'm not sure what vocabulary should represent the graphical location, i.e. column and placement."^^xsd:string .
 	
 vp:pe3 a vps:PriceExpression ;
 	vps:textData "The Norman Razor Black handles, 3s. 6d."^^xsd:string ;
 	vps:textOffsets "[[4 20],[188 210]]"^^xsd:string ;
 	vps:hasPricedThing [ a vps:PricedThing ;
 		vps:textData "The Norman Razor Black handles."^^xsd:string ;
 		vps:textOffsets "[[4 20],[188 201]]"^^xsd:string ] ;
 	vps:hasValueExpression [ a vps:ValueExpression ;
 	    vps:textData "3s. 6d."^^xsd:string ;
 	    vps:textOffsets "[[203 210]]"^^xsd:string ] ;
    vps:normalizedValue [
        vps:normalizedValueDetail "A-S Pound expressed in pence"^^xsd:string ;
        vps:currency unit:ASPound ;
        vps:pence "42"^^xsd:decimal ] .    
            
 vp:pe4 a vps:PriceExpression ;
 	vps:textData "Ivory, 5 s. The Norman Razor"^^xsd:string ;
 	vps:textOffsets "[[211 222],[4 20]]"^^xsd:string ;
 	vps:hasPricedThing [ a vps:PricedThing ;
 		vps:textData "Ivory The Norman Razor"^^xsd:string ;
 		vps:textOffsets "[[211 216],[4 20]]"^^xsd:string ] ;
 	vps:hasValueExpression [ a vps:ValueExpression ;
 	    vps:textData "5 s."^^xsd:string ;
 	    vps:textOffsets "[[218 221]]"^^xsd:string ] ;
    vps:normalizedValue [
        vps:normalizedValueDetail "A-S Pound expressed in pence"^^xsd:string;
        vps:currency unit:ASPound;
        vps:pence "60"^^xsd:decimal ] .    
            
 vp:pe5 a vps:PriceExpression ;
 	vps:textData "with Patent Guards 2s. each extra The Norman Razor"^^xsd:string ;
 	vps:textOffsets "[[230 248],[290 304],[4 20]]"^^xsd:string ;
 	vps:hasPricedThing [ a vps:PricedThing ;
 		vps:textData "with Patent Guards each extra The Norman Razor"^^xsd:string ;
 		vps:textOffsets "[[230 248],[294 304],[4 20]]"^^xsd:string ] ;
 	vps:hasValueExpression [ a vps:ValueExpression ;
 	    vps:textData "2s"^^xsd:string ;
 	    vps:textOffsets "[[290 292]]"^^xsd:string ] ;
    vps:normalizedValue [
        vps:normalizedValueDetail "A-S Pound expressed in pence"^^xsd:string;
        vps:currency unit:ASPound;
        vps:pence "24"^^xsd:decimal ] .    
            
<http://books.google.ca/books?id=tRhAAAAAcAAJ&pg=PP5#v=onepage&q&f=false> a bibo:journal ;
    dc:title "The Lancet: A Journal of British and Foreign Medicine, Physiology, Surgery, Chemistry, Criticism, Literature, and News"^^xsd:string ;
    dc:date "1852-01-17" ;
    bibo:volume "1" ;
    bibo:issue "2" ;
    bibo:editor vps:person1 ;
    dc:publisher vps:person2 ;
    bibo:distributor <http://books.google.com> .
    
vps:person1 a foaf:Person ;
    foaf:givenname "Thomas" ;
    foaf:family_name "Wakley" ;
    bibo:bibdata "Placeholder containing other text listed with Wakley's name: Surgeon, M.P. For The Metropolitan District of Finsbury, And Coroner For The County Of Middlesex"^^xsd:string .

 vps:person2 a foaf:Person ;
    foaf:givenname "George" ;
    foaf:family_name "Churchill" ;
    vcard:hasAddress [ a vcard:Work;
       vcard:country-name "England" ;
       vcard:locality "London" ;
       vcard:street-address "22 Strand" ] .       
 	
 	                
"""

# define query:
VPquery = u"""
SELECT ?textdata ?headline ?pence
WHERE { ?s a vps:Quotation;
            vps:hasPriceExpression ?vpsPE .
                
        ?vpsPE a vps:PriceExpression;
                vps:normalizedValue [
                    vps:pence ?pence
                ] ;
                vps:hasPricedThing [
                    vps:textData ?textdata
                ] .
        
        OPTIONAL {
            ?s schema:headline ?headline .
        }
                
        FILTER (?pence > 40 &&
                ?pence < 500)
    }
"""

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
    print "Priced thing: %s\n\
            headline: %s\n\
            price in ASP (Pounds, shillings, and pence): %s\n~~~~~~~~~~\n" % (x[0], x[1], penniesToTuple(eval(x[2])))


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

