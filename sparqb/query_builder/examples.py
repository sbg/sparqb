__author__ = 'Jovan Cejovic <jovan.cejovic@sbgenomics.com>'
__date__ = '02 March 2016'
__copyright__ = 'Copyright (c) 2016 Seven Bridges Genomics'

from sparqb.query_builder.blazegraph.blazegraph_query_builder import BlazegraphQueryBuilder
from sparqb.query_builder.expression import *
from uuid import uuid4

from rdflib.namespace import XSD

if __name__ == '__main__':
    qb = BlazegraphQueryBuilder()

    qb.axiom("a", "a", "tcga:Analyte"). \
        union().axiom(var_f("a"), "a", uri_f("tcga:Aliquot")).build(). \
        union().axiom("a", "a", "https://www.sbgenomics.com/ontologies/2014/11/tcga#Sample").build(). \
        optional().axiom("a", "tcga:hasAmount", var_f("am")).build(). \
        bind(bound_f("am"), "exists"). \
        group_by("type", var_f("exists")). \
        select("type").select("exists").select(as_f(count_f(distinct_f('a')), "cnt")). \
        set_prefix("https://www.sbgenomics.com/ontologies/2014/11/tcga#", "tcga")

    query = qb.build()

    with open('ex1.sparql', 'w') as f:
        f.write(str(query))

    qb = BlazegraphQueryBuilder()

    qb.axiom("f", "rdfs:label", var_f("fn")). \
        bds_search("fn", '"C500.TCGA-ZF-AA53-10A-01D-A394-08.2"', match_all_terms=True).\
        axiom("f", "tcga:hasDataFormat", "df").\
        axiom(var_f("df"), "rdfs:label", "dfl").\
        values(("dfl",), [('"BAM"',), ('"BAI"',)]).\
        filter_exists().axiom("f", "tcga:hasCase", "c").build().\
        select("f").limit(10). \
        set_prefix("https://www.sbgenomics.com/ontologies/2014/11/tcga#", "tcga")

    query = qb.build()

    with open('ex2.sparql', 'w') as f:
        f.write(str(query))

    qb = BlazegraphQueryBuilder()

    qb.union().\
            axiom("a", "rdf:type", "tcga:Aliquot").\
            union().\
            axiom("a", "rdf:type", "tcga:Analyte").\
            build().\
        build().\
        axiom("a", "tcga:hasAmount", "am").\
        filter((var_f("am") > literal_f("'5.5'", uri_f(XSD.decimal))) &
               (var_f("am") < literal_f(5.8))).\
        select("a").select("am").limit(100). \
        set_prefix("https://www.sbgenomics.com/ontologies/2014/11/tcga#", "tcga")

    query = qb.build()

    with open('ex3.sparql', 'w') as f:
        f.write(str(query))

    qb = BlazegraphQueryBuilder()

    qb.axiom("a", "rdf:type", "type"). \
        axiom("type", "rdfs:subClassOf", "tcga:TCGAEntity"). \
        group_by("type"). \
        select("type").select(as_f(count_f('*'), "cnt")). \
        set_prefix("https://www.sbgenomics.com/ontologies/2014/11/tcga#", "tcga")

    query = qb.build()

    with open('ex4.sparql', 'w') as f:
        f.write(str(query))

    qb = BlazegraphQueryBuilder()

    qb.axiom("f", "rdfs:label", var_f("fn")). \
        bds_search("fn", '"C500.TCGA-ZF-AA53-10A-01D-A394-08.2"', match_all_terms=True). \
        query_id(str(uuid4())). \
        axiom("f", "tcga:hasDataFormat", "df"). \
        axiom(var_f("df"), "rdfs:label", "dfl"). \
        values(("dfl",), [('"BAM"',), ('"BAI"',)]). \
        filter_exists().axiom("f", "tcga:hasCase", "c").build(). \
        select("f").select("s").limit(10). \
        set_prefix("https://www.sbgenomics.com/ontologies/2014/11/tcga#", "tcga")

    query = qb.build()

    with open('ex5.sparql', 'w') as f:
        f.write(str(query))
