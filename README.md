sparqb
===================

[CHANGESETS](CHANGES.md)


Sparqb is a [Python](http://www.python.org/) library for programmatic construction
of [SPARQL](https://www.w3.org/TR/rdf-sparql-query/) queries. It works with Python 3+.

We are aiming to support full [SPARQL 1.1 specification](https://www.w3.org/TR/sparql11-query/),
but some features are missing at the moment, as the library is in very active development.

The library is in the alpha release. Expect APIs to potentially break in future versions. More 
detailed examples and documentation will be added in the stable release.

Installation
------------

The easiest way to install sparqb is using pip:

    $ pip install git+https://github.com/sbg/sparqb

Get the Code
------------

sparqb is actively developed on GitHub, where the code is
always available.

The easiest way to obtain the source is to clone the public repository:

    $ git clone git@github.com:sbg/sparqb.git

Once you have a copy of the source, you can embed it in your Python
package, or install it into your site-packages by invoking:

    $ python setup.py install


Run Tests
---------

In order to run tests clone this repository, position yourself in the
root of the cloned project and after installing requirements-dev.txt,
invoke:

    py.test

Examples
--------

There are two classes of objects prominent in this library: Statements and Expressions. Statements represent major constructs in the SPARQL language (UNION clause, Values clause etc). Expressions cover a range of terms such as variables, literals, functions etc. While it's possible to construct queries by manually combining instances of these classes, the recommended approach is to use the provided QueryBuilder class which offers a fluent interface for easier query creation.

Note: each of the examples works with a new instance of the QueryBuilder class.


``` {.sourceCode .python}
from sparqb.query_builder import QueryBuilder
qb = QueryBuilder()

qb.axiom('?a', '?b', '?c')
print(qb.build())
>>> 
select *
WHERE{
 ?a ?b ?c .
}
```
Operations on the query builder can be chained:

```{.sourceCode .python}
qb.axiom('?a', '?b', '?c').axiom('?e', '?f', '?g')
>>> 
select *
WHERE{
 ?a ?b ?c .
 ?e ?f ?g .
}
```
Selections can be customized:

```{.sourceCode .python}
qb.axiom('?a', '?b', '?c').select('?a')
```
In order to avoid question marks when defining variables, we can use the var_f utility function from the expressions module:

```{.sourceCode .python}
from sparqb.query_builder.expression import var_f

a = var_f(a)
>>> ?a
```

This function generates a VariableExpression instance which can be reused throughout the query.
There are other utility functions in this module for generating expressions of different types which will be shown in later examples.

**Filtering:**
```{.sourceCode .python}
a = var_f('a')
b = var_f('b')
c = var_f('c')
qb.axiom(a, b, c).select(a)\
.filter((a > literal_f(5.5)) & (a < literal_f(5.8)))
>>>
select ?a
WHERE{
 ?a ?b ?c .
 FILTER (((?a > 5.5) && (?a < 5.8)))
}
```

**Union statement:**
```{.sourceCode .python}
a = var_f('a')
qb.axiom(a, var_f('b'), var_f('c')).select(a)\
.union().axiom(var_f('e'), var_f('f'), var_f('g')).build()\
.union().axiom(var_f('e'), var_f('f'), var_f('g')).build()\
.build()
>>>
select ?a
WHERE{
 ?a ?b ?c .
{
 ?e ?f ?g .
}
UNION {
 ?e ?f ?g .
}
}
```

Union is a compound statement. It has its own body which can be built using the same fluent interface. When the union() method is called, a new scope is opened and further statements are added to it until build() method is called. The build() method closes the scope of the compound statement and returns the control to the parent scope, which in the example above is the root query builder scope. Other statements that are also compound are Optional, Minus, Service and Query.

**Subqueries:**

```{.sourceCode .python}
a = var_f('a')
qb.axiom(a, var_f('b'), var_f('c')).select(a)\
.subquery().axiom(a, var_f('f'), var_f('g')).select(a).distinct().build()\
.build()
>>>
select ?a
WHERE{
 ?a ?b ?c .
{
select DISTINCT ?a
WHERE{
 ?a ?f ?g .
}
}
}
```

This example showcases aggregate functions, grouping, optional statements, prefixes and limit setting.

```{.sourceCode .python}
qb.axiom("a", "a", "tcga:Analyte"). \
        union().axiom(var_f("a"), "a", uri_f("tcga:Aliquot")).build(). \
        union().axiom("a", "a", "https://www.sbgenomics.com/ontologies/2014/11/tcga#Sample").build(). \
        optional().axiom("a", "tcga:hasAmount", var_f("am")).build(). \
        bind(bound_f("am"), "exists"). \
        group_by("type", var_f("exists")). \
        select("type").select("exists").select(as_f(count_f(distinct_f('a')), "cnt")). \
        set_prefix("https://www.sbgenomics.com/ontologies/2014/11/tcga#", "tcga"). \
        limit(100).build()
>>>
select ?type ?exists (COUNT(DISTINCT ?a) AS ?cnt)
WHERE{
 ?a a tcga:Analyte .
{
 ?a a tcga:Aliquot .
}
UNION {
 ?a a <https://www.sbgenomics.com/ontologies/2014/11/tcga#Sample> .
}
OPTIONAL {
 ?a tcga:hasAmount ?am .
}
BIND(BOUND(?am) AS ?exists)
}
GROUP BY ?type ?exists
LIMIT 100
```
There's another query builder class included, the BlazegraphQueryBuilder which covers Blazegraph specific features such as search statements and query hints.
Examples of usage as well as more detailed examples are located in the examples.py.

Contributors
===================
- Adam Stanojevic <adam.stanojevic@sbgenomics.com>
- Ivan Selimbegovic <ivan.selimbegovic@sbgenomics.com>
- Nemanja Vukosavljevic <nemanja.vukosavljevic@sbgenomics.com>
- Milica Miletic <milica.miletic@sbgenomics.com>
- Jelena Derikonjic <jelena.derikonjic@sbgenomics.com>
- Vladimir Mladenovic <vladimir.mladenovic@sbgenomics.com>
- Jovan Cejovic <jovan.cejovic@sbgdinc.com>
