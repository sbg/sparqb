__author__ = 'Adam Stanojevic <adam.stanojevic@sbgenomics.com>'
__date__ = '23 February 2016'
__copyright__ = 'Copyright (c) 2016 Seven Bridges Genomics'

import abc
from .util import *


class Expression(object, metaclass=abc.ABCMeta):
    VALUE_TYPE = 'value'
    AS_TYPE = 'as'

    def __init__(self, expression_type=VALUE_TYPE):
        self._type = expression_type

    @property
    def type(self):
        return self._type

    @abc.abstractmethod
    def _serialize(self):
        pass

    def __str__(self):
        return self._serialize()

    @staticmethod
    def check_binary_expression_compatibility(left, right):
        if not (isinstance(left, Expression) and left.type == Expression.VALUE_TYPE and isinstance(right,
                                                                                                   Expression) and right.type == Expression.VALUE_TYPE):
            raise ValueError
        return True

    @staticmethod
    def check_unary_expression_compatibility(expr):
        if not (isinstance(expr, Expression) and expr.type == Expression.VALUE_TYPE):
            raise ValueError
        return True

    def __and__(self, other):
        if Expression.check_binary_expression_compatibility(self, other):
            return BinaryOperatorExpression('&&', self, other)

    def __or__(self, other):
        if Expression.check_binary_expression_compatibility(self, other):
            return BinaryOperatorExpression('||', self, other)

    def __invert__(self):
        if Expression.check_unary_expression_compatibility(self):
            return UnaryOperatorExpression('!', self)

    def __gt__(self, other):
        if Expression.check_binary_expression_compatibility(self, other):
            return BinaryOperatorExpression('>', self, other)

    def __lt__(self, other):
        if Expression.check_binary_expression_compatibility(self, other):
            return BinaryOperatorExpression('<', self, other)

    def __eq__(self, other):
        if Expression.check_binary_expression_compatibility(self, other):
            return BinaryOperatorExpression('=', self, other)

    def __le__(self, other):
        if Expression.check_binary_expression_compatibility(self, other):
            return BinaryOperatorExpression('<=', self, other)

    def __ge__(self, other):
        if Expression.check_binary_expression_compatibility(self, other):
            return BinaryOperatorExpression('>=', self, other)


class VariableExpression(Expression):
    def __init__(self, name):
        super(VariableExpression, self).__init__(Expression.VALUE_TYPE)
        if isinstance(name, str) and name:
            if name.startswith('?'):
                if len(name[1:]) > 0:
                    self._name = name[1:]
                else:
                    raise ValueError
            else:
                self._name = name
        else:
            raise ValueError

    @property
    def name(self):
        return self._name

    def _serialize(self):
        return '?' + self._name


class LiteralExpression(Expression):
    def __init__(self, value, value_type=None):
        super(LiteralExpression, self).__init__(Expression.VALUE_TYPE)
        if value is None or value == '':
            raise ValueError
        self._value = value
        self._value_type = value_type

    def _serialize(self):
        return str(self._value) + ('^^' + str(self._value_type) if self._value_type else '')


class FunctionExpression(Expression):
    def __init__(self, name, *arguments):
        super(FunctionExpression, self).__init__(Expression.VALUE_TYPE)
        if name is None or name == '':
            raise ValueError
        if isinstance(name, str):
            self._name = name
        else:
            raise TypeError

        if all([isinstance(arg, Expression) and arg.type == Expression.VALUE_TYPE for arg in arguments]):
            self._arguments = arguments
        else:
            raise TypeError

    def _serialize(self):
        return self._name + '(' + ', '.join([str(arg) for arg in self._arguments]) + ')'


class AsExpression(Expression):
    def __init__(self, expression: Expression, variable: VariableExpression):
        super(AsExpression, self).__init__(Expression.AS_TYPE)
        if expression is None or variable is None:
            raise ValueError
        if isinstance(expression, Expression) and expression.type == Expression.VALUE_TYPE and isinstance(variable, VariableExpression):
            self._expression = expression
            self._variable = variable
        else:
            raise TypeError

    def _serialize(self):
        return '(' + str(self._expression) + ' AS ' + str(self._variable) + ')'


class UnaryOperatorExpression(Expression):
    def __init__(self, operator, expression):
        super(UnaryOperatorExpression, self).__init__(Expression.VALUE_TYPE)
        if expression is None or operator is None:
            raise ValueError
        if isinstance(expression, Expression) and expression.type == Expression.VALUE_TYPE:
            self._expression = expression
        else:
            raise TypeError

        self._operator = operator

    def _serialize(self):
        return str(self._operator) + str(self._expression)


class BinaryOperatorExpression(Expression):
    def __init__(self, operator, left_expression, right_expression):
        super(BinaryOperatorExpression, self).__init__(Expression.VALUE_TYPE)
        if left_expression is None or right_expression is None:
            raise ValueError
        if operator is None:
            raise ValueError

        if isinstance(left_expression, Expression) and isinstance(right_expression, Expression) and \
                        left_expression.type == Expression.VALUE_TYPE and \
                        right_expression.type == Expression.VALUE_TYPE:
            self._left_expression = left_expression
            self._right_expression = right_expression
        else:
            raise TypeError

        self._operator = operator

    def _serialize(self):
        return '(' + str(self._left_expression) + ' ' + str(self._operator) + ' ' + str(self._right_expression) + ')'


class DistinctExpression(Expression):
    def __init__(self, *expressions):
        super(DistinctExpression, self).__init__(Expression.VALUE_TYPE)
        if len(expressions) > 0 and all(
                [(isinstance(expression, VariableExpression) or isinstance(expression, AsExpression))
                 for expression in expressions]):
            self._expressions = expressions
        else:
            raise TypeError

    def _serialize(self):
        return 'DISTINCT ' + ' '.join(str(expression) for expression in self._expressions)


class StarExpression(Expression):
    def __init__(self):
        super(StarExpression, self).__init__(Expression.VALUE_TYPE)

    def _serialize(self):
        return '*'


class UriExpression(Expression):
    def __init__(self, uri):
        super(UriExpression, self).__init__(Expression.VALUE_TYPE)
        if is_valid_uri(str(uri)):
            self._uri = str(uri)
        else:
            raise ValueError

    def _serialize(self):
        if is_valid_short(self._uri):
            return self._uri
        else:
            return '<' + self._uri + '>'


class InExpression(Expression):
    def __init__(self, expression, *values):
        super(InExpression, self).__init__(Expression.VALUE_TYPE)
        if isinstance(expression, Expression) and expression.type == Expression.VALUE_TYPE:
            self._expression = expression
        else:
            raise TypeError

        if all([isinstance(item, Expression) and item.type == Expression.VALUE_TYPE for item in values]):
            self._values = values
        else:
            raise TypeError

    def _serialize(self):
        return str(self._expression) + ' IN ' + '(' + ', '.join(str(item) for item in self._values) + ')'


class RegexExpression(Expression):
    def __init__(self, expression, regex):
        super(RegexExpression, self).__init__(Expression.VALUE_TYPE)
        if expression is None:
            raise ValueError
        if isinstance(expression, Expression) and expression.type == Expression.VALUE_TYPE:
            self._expression = expression
        else:
            raise TypeError

        if regex is not None:
            self._regex = regex
        else:
            raise ValueError

    def _serialize(self):
        return 'regex(str(%s), "%s", "i")' % (str(self._expression), str(self._regex))


# some short named functions to ease expression building
def as_f(expression: Expression, variable):
    if isinstance(variable, str):
        variable = var_f(variable)
    return AsExpression(expression, variable)


def literal_f(value, value_type=None):
    return LiteralExpression(value, value_type)


def count_f(argument):
    if isinstance(argument, str):
        if argument.strip() == '*':
            argument = StarExpression()
        else:
            argument = var_f(argument)
    return FunctionExpression('COUNT', argument)


def desc_f(argument):
    if isinstance(argument, str):
        argument = var_f(argument)
    return FunctionExpression('DESC', argument)


def var_f(name):
    return VariableExpression(name)


def uri_f(uri):
    if is_valid_uri(uri):
        return UriExpression(uri)
    else:
        raise ValueError


def distinct_f(*names):
    prepared = []
    for item in names:
        if isinstance(item, Expression):
            prepared.append(item)
        else:
            prepared.append(var_f(item))
    return DistinctExpression(*prepared)


def in_f(expression: Expression, *possible_values):
    return InExpression(expression, *possible_values)


def bound_f(name):
    if isinstance(name, str):
        name = var_f(name)
    return FunctionExpression('BOUND', name)


def equals_f(expression_1, expression_2):
    return BinaryOperatorExpression(' = ', expression_1, expression_2)


def regex_f(expression, value):
    return RegexExpression(expression, value)
