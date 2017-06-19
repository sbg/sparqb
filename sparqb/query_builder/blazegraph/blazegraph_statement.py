__author__ = 'Adam Stanojevic <adam.stanojevic@sbgenomics.com>'
__date__ = '07 March 2016'
__copyright__ = 'Copyright (c) 2016 Seven Bridges Genomics'

from ..statement import *
from string import Template

class BlazegraphQuery(Query):
    def __init__(self):
        super(BlazegraphQuery, self).__init__()
        self._query_template = Template('$prefixes$select$$with_query$where$group_by$having$order_by$limit$offset')

    @property
    def type(self):
        # TODO - it may not be useful - investigate!
        pass

    @property
    def query_id(self):
        result = None
        for statement in self._statements:
            if isinstance(statement, QueryIdStatement):
                result = statement.query_id
                break
        return result

    def _serialize(self, serialization_mode=Statement.SERIALIZATION_RAW):
        # with section
        with_section = ''
        if hasattr(self, '_with_statements'):
            for statement in self._with_statements:
                with_section += str(statement)

        return Template(super(BlazegraphQuery, self)._serialize()).substitute(with_query=with_section)

    def key(self):
        ws = tuple(sorted(str(ws) for ws in self._with_statements))

        return hash(ws) ^ super(BlazegraphQuery, self).key()


class BDSSearchStatement(ServiceStatement):
    def __init__(self, variable: VariableExpression, value, match_all_terms=True, relevance=None):
        uri = "http://www.bigdata.com/rdf/search#search"

        search_value = '"%s"' % value

        statements = [AxiomStatement(variable, "<http://www.bigdata.com/rdf/search#search>", literal_f(search_value))]

        if match_all_terms:
            statements.append(AxiomStatement(variable,
                                             "<http://www.bigdata.com/rdf/search#matchAllTerms>", literal_f('"true"')))
        else:
            statements.append(AxiomStatement(variable,
                                             "<http://www.bigdata.com/rdf/search#matchAllTerms>", literal_f('"false"')))

        if relevance is not None:
            statements.append(AxiomStatement(variable,
                                             "<http://www.bigdata.com/rdf/search#relevance>", literal_f(relevance)))

        super(BDSSearchStatement, self).__init__(uri, *statements)


class QueryIdStatement(AxiomStatement):
    def __init__(self, query_id):
        self._id = query_id
        super(QueryIdStatement, self).__init__('hint:Query', 'hint:queryId', '"' + str(query_id) + '"')

    @property
    def query_id(self):
        return self._id


class QueryChunkSizeStatement(AxiomStatement):
    def __init__(self, query_chunk_size):
        super(QueryChunkSizeStatement, self).__init__('hint:Query', 'hint:chunkSize', '"' + str(query_chunk_size) + '"')


class QueryMaxParallelStatement(AxiomStatement):
    def __init__(self, query_max_parallel):
        super(QueryMaxParallelStatement, self).__init__('hint:Query', 'hint:maxParallel', '"' + str(query_max_parallel) + '"')


class QueryOptimizerStatement(AxiomStatement):
    def __init__(self, optimizer):
        super(QueryOptimizerStatement, self).__init__('hint:Query', 'hint:optimizer', '"' + optimizer.value + '"')


class SolutionSetStatement(Statement):
    def __init__(self, solution_set):
        super(SolutionSetStatement, self).__init__()
        self._solution_set = solution_set

    def key(self):
        return hash(str(self._solution_set))

    def _serialize(self, serialization_mode=Statement.SERIALIZATION_RAW):
        return ' INCLUDE %' + str(self._solution_set) + ' \n'


class IncludeStatement(Statement):
    def __init__(self, name):
        super(IncludeStatement, self).__init__()
        self._name = name

    def key(self):
        return hash(str(self._name))

    def _serialize(self, serialization_mode=Statement.SERIALIZATION_RAW):
        return ' INCLUDE %' + str(self._name) + ' \n'


class WithStatement(CompoundStatement):
    def __init__(self, name, *statements):
        super(WithStatement, self).__init__(*statements)
        self._name = name

    def key(self):
        return hash('with') ^ hash(str(self._name)) ^ super(WithStatement, self).key()

    def _serialize(self, serialization_mode=Statement.SERIALIZATION_RAW):
        result = '\nWITH\n' + super(WithStatement, self)._serialize() + 'AS %' + self._name + '\n'
        return result




