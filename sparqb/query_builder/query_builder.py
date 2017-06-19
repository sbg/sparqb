__author__ = 'Adam Stanojevic <adam.stanojevic@sbgenomics.com>'
__date__ = '23 February 2016'
__copyright__ = 'Copyright (c) 2016 Seven Bridges Genomics'

import abc
import operator
from .statement import *
from .expression import *


class StatementBuilder(metaclass=abc.ABCMeta):
    def __init__(self, parent_builder=None):
        self._statements = []
        if parent_builder:
            self._parent_builder = parent_builder

    def _plug_statement(self, statement: Statement):
        self._statements.append(statement)

    @abc.abstractmethod
    def build(self):
        pass

    def axiom(self, s, p, o):
        if isinstance(s, str):
            if is_valid_uri(s):
                s = uri_f(s)
            else:
                s = var_f(s)
        if isinstance(o, str):
            if is_valid_uri(o):
                o = uri_f(o)
            else:
                o = var_f(o)
        self._plug_statement(AxiomStatement(s, p, o))
        return self

    def subquery(self, query=None):
        if query is None:
            return QueryBuilder(self)
        else:
            self._plug_statement(CompoundStatement(query))
            return self

    def compound(self):
        return CompoundStatementBuilder(CompoundStatement, self)

    def service(self, uri):
        return CompoundStatementBuilder(ServiceStatement, self, uri)

    def filter_exists(self, not_exists_type=False):
        return CompoundStatementBuilder(FilterExistsStatement, self, not_exists_type)

    def optional(self):
        return CompoundStatementBuilder(OptionalStatement, self)

    def union(self):
        add_keyword = self._statements and type(self._statements[len(self._statements)-1]) == UnionStatement
        return CompoundStatementBuilder(UnionStatement, self, add_keyword=add_keyword)

    def minus(self):
        return CompoundStatementBuilder(MinusStatement, self)

    def values(self, variables, variable_value_tuples):
        self._plug_statement(ValuesStatement(variables, variable_value_tuples))
        return self

    def bind(self, expression: Expression, variable):
        if isinstance(variable, str):
            variable = var_f(variable)
        self._plug_statement(BindStatement(expression, variable))
        return self

    def filter(self, expression: Expression):
        self._plug_statement(FilterStatement(expression))
        return self


class CompoundStatementBuilder(StatementBuilder):
    def __init__(self, statement_cls: type(CompoundStatement), parent_builder: StatementBuilder, *args, **kwargs):
        self._statement_cls = statement_cls
        self._cls_args = args
        self._cls_kwargs = kwargs
        self._parent_builder = parent_builder
        super(CompoundStatementBuilder, self).__init__()

    def build(self):
        statement = self._statement_cls(*self._cls_args, **self._cls_kwargs)
        statement._statements = self._statements
        self._parent_builder._plug_statement(statement)
        return self._parent_builder


class QueryBuilder(StatementBuilder):
    def __init__(self, parent_builder=None):
        self._select = []
        self._order_by = []
        self._group_by = []
        self._having = None
        self._prefixes = {}
        self._limit = None
        self._offset = None
        self._is_distinct = False

        # not yet supported
        self._deletes = []
        self._inserts = []

        self._query_cls = Query

        super(QueryBuilder, self).__init__(parent_builder)

    @property
    def select_items(self):
        return self._select

    def set_prefix(self, namespace, prefix):
        self._prefixes[prefix] = namespace
        return self

    def select(self, *expressions):
        for expression in expressions:
            if isinstance(expression, str):
                if expression.strip() == '*':
                    expression = StarExpression()
                else:
                    expression = var_f(expression)
            self._select.append(expression)
        return self

    def distinct(self):
        self._is_distinct = True
        return self

    def group_by(self, *grouping_expressions):
        if len(grouping_expressions) > 0:
            if all((isinstance(item, Expression) or isinstance(item, str)) for item in grouping_expressions):
                prepared_expressions = []
                for item in grouping_expressions:
                    if isinstance(item, Expression):
                        prepared_expressions.append(item)
                    elif isinstance(item, str):
                        prepared_expressions.append(var_f(item))
                self._group_by.extend(prepared_expressions)
            else:
                raise ValueError
        else:
            raise ValueError
        return self

    def having(self, expression: Expression):
        if expression.type == Expression.VALUE_TYPE:
            self._having = expression
        else:
            raise ValueError
        return self

    def order_by(self, *expressions):
        if len(expressions) > 0:
            if all([(isinstance(item, Expression) or isinstance(item, str)) for item in expressions]):
                prepared_expressions = []
                for item in expressions:
                    if isinstance(item, Expression):
                        prepared_expressions.append(item)
                    elif isinstance(item, str):
                        prepared_expressions.append(var_f(item))
                self._order_by.extend(prepared_expressions)
            else:
                raise TypeError
        else:
            raise ValueError
        return self

    def limit(self, limit_value):
        self._limit = limit_value
        return self

    def offset(self, offset_value):
        self._offset = offset_value
        return self

    def build(self):
        query = self._query_cls()
        query._select = self._select
        query._is_distinct = self._is_distinct
        query._order_by = self._order_by
        query._group_by = self._group_by
        query._having = self._having
        query._statements = self._statements
        query._prefixes = self._prefixes
        query._limit = self._limit
        query._offset = self._offset

        query._deletes = self._deletes
        query._inserts = self._inserts

        if hasattr(self, '_parent_builder'):
            self._parent_builder._plug_statement(CompoundStatement(query))
            return self._parent_builder

        return query
