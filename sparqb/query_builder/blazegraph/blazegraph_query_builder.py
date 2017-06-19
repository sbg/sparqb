__author__ = 'Adam Stanojevic <adam.stanojevic@sbgenomics.com>'
__date__ = '07 March 2016'
__copyright__ = 'Copyright (c) 2016 Seven Bridges Genomics'

from .blazegraph_query_hints import Optimizer
from .blazegraph_statement import *
from ..query_builder import *


class BlazegraphSubqueryBuilder(QueryBuilder):
    def __init__(self, parent_builder=None):
        self._query_id = None
        self._query_chunk_size = None
        super(BlazegraphSubqueryBuilder, self).__init__(parent_builder)
        self._query_cls = BlazegraphQuery

    def query_id(self, query_id):
        self._query_id = query_id
        return self

    def chunk_size(self, chunk_size):
        if chunk_size and isinstance(chunk_size, int):
            self._plug_statement(QueryChunkSizeStatement(chunk_size))
        return self

    def max_parallel(self, max_parallel):
        if max_parallel and isinstance(max_parallel, int):
            self._plug_statement(QueryMaxParallelStatement(max_parallel))
        return self

    def service(self, uri):
        return BlazegraphCompoundStatementBuilder(ServiceStatement, self, uri)

    def bds_search(self, variable, value, match_all_terms=True, relevance=None):
        if isinstance(variable, str):
            variable = var_f(variable)
        self._plug_statement(BDSSearchStatement(variable, value, match_all_terms, relevance))
        return self

    def optimizer(self, optimizer=None):
        if optimizer is None:
            optimizer = Optimizer.static
        self._plug_statement(QueryOptimizerStatement(optimizer))
        return self

    def solution_set(self, solution_set):
        self._plug_statement(SolutionSetStatement(solution_set))

    def subquery(self, query=None):
        if query is None:
            return BlazegraphSubqueryBuilder(self)
        else:
            return super(BlazegraphSubqueryBuilder, self).subquery(query)

    def include(self, name=None):
        self._plug_statement(IncludeStatement(name))

    def build(self):
        if self._query_id is not None:
            self._plug_statement(QueryIdStatement(self._query_id))

        query = super(BlazegraphSubqueryBuilder, self).build()

        return query


class BlazegraphQueryBuilder(BlazegraphSubqueryBuilder):
    def __init__(self):
        super(BlazegraphQueryBuilder, self).__init__()
        self._with_statements = []

    def with_query(self, name, query=None):
        if query is None:
            return NamedSubqueryBuilder(name, self)
        else:
            self._with_statements.append(WithStatement(name, query))
        return self

    def build(self):
        query = super(BlazegraphQueryBuilder, self).build()
        query._with_statements = self._with_statements
        return query


class NamedSubqueryBuilder(BlazegraphSubqueryBuilder):
    def __init__(self, name, parent_builder: BlazegraphQueryBuilder):
        super(NamedSubqueryBuilder, self).__init__(parent_builder=parent_builder)
        self._name = name

    def build(self):
        query = self._query_cls()
        query._select = self._select
        query._is_distinct = self._is_distinct
        query._order_by = self._order_by
        query._group_by = self._group_by
        query._having = self._having
        query._statements = self.statements
        query._prefixes = self._prefixes
        query._limit = self._limit
        query._offset = self._offset

        query._deletes = self._deletes
        query._inserts = self._inserts

        self._parent_builder._with_statements.append(WithStatement(self._name, query))
        return self._parent_builder


class BlazegraphCompoundStatementBuilder(BlazegraphSubqueryBuilder):
    def __init__(self, statement_cls: type(CompoundStatement), parent_builder: BlazegraphSubqueryBuilder, *args):
        self._statement_cls = statement_cls
        self._cls_args = args
        self._parent_builder = parent_builder
        super(BlazegraphCompoundStatementBuilder, self).__init__()

    def build(self):
        statement = self._statement_cls(*self._cls_args)
        statement._statements = self.statements
        self._parent_builder._plug_statement(statement)
        return self._parent_builder
