__author__ = 'Adam Stanojevic <adam.stanojevic@sbgenomics.com>'
__date__ = '19 February 2016'
__copyright__ = 'Copyright (c) 2016 Seven Bridges Genomics'

import abc
from string import Template
from .expression import *


class Statement(metaclass=abc.ABCMeta):

    SERIALIZATION_RAW = 'raw'
    SERIALIZATION_PRETTY = 'pretty'

    @abc.abstractmethod
    def _serialize(self, serialization_mode=SERIALIZATION_RAW):
        pass

    @abc.abstractmethod
    def key(self):
        pass

    def __hash__(self):
        return hash(self.key())

    def serialize(self, serialization_mode=SERIALIZATION_PRETTY):
        return self._serialize(serialization_mode)

    def __str__(self):
        return self.serialize(Statement.SERIALIZATION_RAW)


class CompoundStatement(Statement):
    def __init__(self, *statements):
        self._statements = statements
        super(CompoundStatement, self).__init__()

    def key(self):
        sts = tuple(sorted([s.key() for s in self._statements]))
        return hash(sts)

    def _serialize(self, serialization_mode=Statement.SERIALIZATION_RAW):
        result = '{\n'
        result += ' \n'.join([str(statement) for statement in self._statements])
        result += '}\n'
        return result


class AxiomStatement(Statement):
    def __init__(self, s, p, o):
        super(AxiomStatement, self).__init__()
        self._s = s
        self._p = p
        self._o = o

    def key(self):
        sts = tuple([str(s) for s in [self._s, self._p, self._o]])
        return hash(sts)

    def _serialize(self, serialization_mode=Statement.SERIALIZATION_RAW):
        return ' ' + str(self._s) + ' ' + str(self._p) + ' ' + str(self._o) + ' . \n'


class ValuesStatement(Statement):

    def __init__(self, variables_tuple, value_tuples):
        super(ValuesStatement, self).__init__()

        if type(variables_tuple) != tuple:
            raise TypeError

        total = len(variables_tuple)

        self._variables_tuple = tuple(item if isinstance(item, Expression) else var_f(item) for item in
                                      variables_tuple)
        self._value_tuples = []

        for item in value_tuples:
            if type(item) != tuple:
                raise TypeError
            elif len(item) != total:
                raise ValueError
            self._value_tuples.append(item)

    def key(self):
        return hash(tuple(str(s) for s in self._variables_tuple)) ^ \
               hash(tuple(sorted(hash(v) for v in self._value_tuples)))

    def _serialize(self, serialization_mode=Statement.SERIALIZATION_RAW):
        result = ' VALUES ( %s ) { ' % ' '.join(str(item) for item in self._variables_tuple)
        result += '\n '.join(['(%s)' % s for s in self._value_tuples]) + ' } \n'
        return result


class Query(CompoundStatement):
    def __init__(self):
        super(Query, self).__init__()
        self._select = []
        self._order_by = []
        self._group_by = []
        self._having = None
        self._prefixes = {}
        self._limit = None
        self._offset = None
        self._is_distinct = False
        self._query_template = Template('''$prefixes$select$where$group_by$having$order_by$limit$offset''')

        # not yet supported - TODO
        self._deletes = []
        self._inserts = []

    def _serialize(self, serialization_mode=Statement.SERIALIZATION_RAW):

        # prefix section

        prefix_records = ''
        if len(self._prefixes) > 0:
            prefix_records += ''.join(['PREFIX ' + prefix + ': ' + '<' + self._prefixes[prefix] + '>' + '\n'
                                       for prefix in self._prefixes])

        # select section

        select_section = 'select '
        if len(self._select) > 0:
            # select query
            selects = self._select
            if self._is_distinct:
                selects = [DistinctExpression(*selects)]
            select_section += ' '.join(str(item) for item in selects)
        else:
            select_section += '*'

        # where section

        where_section = ''
        if len(self._statements) > 0:
            for statement in self._statements:
                where_section += str(statement)
        where_section = '\nWHERE{\n' + where_section + '}\n'

        # group by section

        group_by_section = ''
        if len(self._group_by) > 0:
            group_by_section += '\nGROUP BY ' + ' '.join([str(item) for item in self._group_by])

        # having section

        having_section = ''
        if self._having:
            having_section += '\nHAVING ' + str(self._having)

        # order by section

        order_by_section = ''
        if len(self._order_by) > 0:
            order_by_section = 'ORDER BY ' + ' '.join([str(item) for item in self._order_by])

        # limit section

        limit_section = ''
        if self._limit is not None:
            limit_section += ' LIMIT ' + str(self._limit) + '\n'

        # offset section

        offset_section = ''
        if self._offset is not None:
            offset_section += ' OFFSET ' + str(self._offset) + '\n'

        return self._query_template.substitute(prefixes=prefix_records, select=select_section, where=where_section,
                                       group_by=group_by_section, having=having_section,
                                       order_by=order_by_section, limit=limit_section,
                                       offset=offset_section)

    @property
    def select_items(self):
        return self._select

    def key(self):
        s = tuple(sorted(str(s) for s in self._select))
        ob = tuple(sorted(str(o) for o in self._order_by))
        gb = tuple(sorted(str(g) for g in self._group_by))
        hv = str(self._having)

        return hash(s) ^ hash(ob) ^ hash(gb) ^ hash(hv) ^ super(Query, self).key()

    def __hash__(self):
        return hash(self.key())


class ServiceStatement(CompoundStatement):
    def __init__(self, uri, *statements):
        super(ServiceStatement, self).__init__()
        if is_valid_uri(uri):
            self._uri_for_service = uri
        else:
            raise ValueError
        self._statements = statements

    def key(self):
        return hash('service') ^ hash(str(self._uri_for_service)) ^ super(ServiceStatement, self).key()

    def _serialize(self, serialization_mode=Statement.SERIALIZATION_RAW):
        result = ' SERVICE <' + self._uri_for_service + '> '
        result += super(ServiceStatement, self)._serialize()
        return result


class FilterExistsStatement(CompoundStatement):
    def __init__(self, *statements, not_exists_type=False):
        super(FilterExistsStatement, self).__init__()
        self._statements = statements
        self._not_exists_type = not_exists_type

    def key(self):
        return hash('filter_exists') ^ hash(str(self._not_exists_type)) ^ super(FilterExistsStatement, self).key()

    def _serialize(self, serialization_mode=Statement.SERIALIZATION_RAW):
        if not self._not_exists_type:
            result = ' FILTER EXISTS ' + super(FilterExistsStatement, self)._serialize()
        else:
            result = ' FILTER NOT EXISTS ' + super(FilterExistsStatement, self)._serialize()
        return result


class UnionStatement(CompoundStatement):
    def __init__(self, *statements, add_keyword=True):
        super(UnionStatement, self).__init__(*statements)
        self._add_keyword = add_keyword

    def key(self):
        return hash('union') ^ super(UnionStatement, self).key()

    def _serialize(self, serialization_mode=Statement.SERIALIZATION_RAW):
        result = super(UnionStatement, self)._serialize()
        if self._add_keyword:
            result = 'UNION ' + result
        return result


class OptionalStatement(CompoundStatement):
    def __init__(self, *statements):
        super(OptionalStatement, self).__init__(*statements)

    def key(self):
        return hash('optional') ^ super(OptionalStatement, self).key()

    def _serialize(self, serialization_mode=Statement.SERIALIZATION_RAW):
        return 'OPTIONAL ' + super(OptionalStatement, self)._serialize()


class MinusStatement(CompoundStatement):
    def __init__(self, *statements):
        super(MinusStatement, self).__init__(*statements)

    def key(self):
        return hash('minus') ^ super(MinusStatement, self).key()

    def _serialize(self, serialization_mode=Statement.SERIALIZATION_RAW):
        return 'MINUS ' + super(MinusStatement, self)._serialize()


class BindStatement(Statement):
    def __init__(self, expression: Expression, variable: VariableExpression):
        super(BindStatement, self).__init__()
        if expression.type != Expression.VALUE_TYPE:
            raise ValueError
        if not isinstance(variable, VariableExpression):
            raise ValueError
        self._expression = expression
        self._variable = variable

    def key(self):
        return hash(str(self._variable)) ^ hash(str(self._expression))

    def _serialize(self, serialization_mode=Statement.SERIALIZATION_RAW):
        return 'BIND' + str(AsExpression(self._expression, self._variable)) + '\n'


class FilterStatement(Statement):
    def __init__(self, expression: Expression):
        super(FilterStatement, self).__init__()
        if expression.type != Expression.VALUE_TYPE:
            raise ValueError
        self._filter_expression = expression

    def key(self):
        return hash(str(self._filter_expression))

    def _serialize(self, serialization_mode=Statement.SERIALIZATION_RAW):
        return ' FILTER (' + str(self._filter_expression) + ')\n'
