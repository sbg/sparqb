__author__ = 'Jovan Cejovic <jovan.cejovic@sbgenomics.com>'
__date__ = '17 June 2016'
__copyright__ = 'Copyright (c) 2016 Seven Bridges Genomics'

import pytest
from sparqb.query_builder.expression import *


def test_variable_expression_plain_string():
    v = VariableExpression('abc')
    assert str(v) == '?abc'


def test_variable_expression_sparql_var():
    v = VariableExpression('?abc')
    assert str(v) == '?abc'


def test_variable_expression_empty_string():
    with pytest.raises(ValueError):
        v = VariableExpression('')


def test_variable_expression_empty_sparql_var():
    with pytest.raises(ValueError):
        v = VariableExpression('?')


def test_variable_expression_none():
    with pytest.raises(ValueError):
        v = VariableExpression(None)


def test_literal_expression_untyped():
    l = LiteralExpression(5)
    assert str(l) == "5"


def test_literal_expression_typed():
    l = LiteralExpression('s', 'xsd:string')
    assert str(l) == "s^^xsd:string"


def test_literal_expression_empty_string():
    with pytest.raises(ValueError):
        l = LiteralExpression('')


def test_literal_expression_none():
    with pytest.raises(ValueError):
        l = LiteralExpression(None)


def test_function_expression_one_argument():
    arg1 = VariableExpression('arg1')
    f = FunctionExpression('str', arg1)
    assert str(f) == 'str(%s)' % str(arg1)


def test_function_expression_two_arguments():
    arg1 = VariableExpression('arg1')
    arg2 = VariableExpression('arg2')
    f = FunctionExpression('str', arg1, arg2)
    assert str(f) == 'str(%s, %s)' % (str(arg1), str(arg2))


def test_function_expression_invalid_name():
    with pytest.raises(TypeError):
        arg1 = VariableExpression('arg1')
        f = FunctionExpression(123, arg1)


def test_function_expression_empty_name():
    with pytest.raises(ValueError):
        arg1 = VariableExpression('arg1')
        f = FunctionExpression('', arg1)


def test_function_expression_invalid_argument():
    with pytest.raises(TypeError):
        f = FunctionExpression('str', 'arg1')


def test_function_expression_some_invalid_argument():
    with pytest.raises(TypeError):
        arg1 = VariableExpression('arg1')
        f = FunctionExpression('str', arg1, 'arg2')


def test_as_expression():
    arg1 = VariableExpression('arg1')
    f = FunctionExpression('str', arg1)
    v = VariableExpression('x')
    a = AsExpression(f, v)
    assert str(a) == '(%s AS %s)' % (str(f), str(v))


def test_as_expression_expression_none():
    v = VariableExpression('x')
    with pytest.raises(ValueError):
        a = AsExpression(None, v)


def test_as_expression_variable_none():
    arg1 = VariableExpression('arg1')
    f = FunctionExpression('str', arg1)
    with pytest.raises(ValueError):
        a = AsExpression(f, None)


def test_as_expression_variable_invalid_expression_argument():
    arg1 = VariableExpression('arg1')
    f = FunctionExpression('str', arg1)
    with pytest.raises(TypeError):
        a = AsExpression(f, arg1)
        a2 = AsExpression(a, arg1)


def test_unary_operator_expression():
    v = VariableExpression('abc')
    u = UnaryOperatorExpression('!', v)
    assert str(u) == '!?abc'


def test_unary_operator_expression_invalid_expression():
    arg1 = VariableExpression('arg1')
    f = FunctionExpression('str', arg1)
    with pytest.raises(TypeError):
        a = AsExpression(f, arg1)
        u = UnaryOperatorExpression('!', a)


def test_unary_operator_expression_none():
    with pytest.raises(ValueError):
        u = UnaryOperatorExpression('!', None)


def test_unary_operator_expression_operator_none():
    v = VariableExpression('abc')
    with pytest.raises(ValueError):
        u = UnaryOperatorExpression(None, v)


def test_binary_operator_expression():
    v = VariableExpression('abc')
    x = LiteralExpression(5)
    b = BinaryOperatorExpression('+', v, x)
    assert str(b) == '(%s + %s)' % (v, x)


def test_binary_operator_expression_invalid_expression():
    arg1 = VariableExpression('arg1')
    v = VariableExpression('abc')
    f = FunctionExpression('str', arg1)
    with pytest.raises(TypeError):
        a = AsExpression(f, arg1)
        b = BinaryOperatorExpression('+', v, a)


def test_binary_operator_expression_none():
    v = VariableExpression('abc')
    with pytest.raises(ValueError):
        b = BinaryOperatorExpression('+', v, None)


def test_distinct_expression():
    v = VariableExpression('abc')
    d = DistinctExpression(v)
    assert str(d) == 'DISTINCT %s' % str(v)


def test_distinct_expression_invalid_expression():
    arg1 = VariableExpression('arg1')
    f = FunctionExpression('str', arg1)
    with pytest.raises(TypeError):
        d = DistinctExpression(f)


def test_distinct_expression_none():
    with pytest.raises(TypeError):
        d = DistinctExpression(None)


def test_star_expression():
    s = StarExpression()
    assert str(s) == '*'


def test_uri_expression():
    u = UriExpression('https://www.sbgenomics.com/ontologies/2014/11/tcga#Case')
    assert str(u) == '<https://www.sbgenomics.com/ontologies/2014/11/tcga#Case>'


def test_uri_expression_short():
    u = UriExpression('tcga:Case')
    assert str(u) == 'tcga:Case'


def test_uri_expression_invalid_uri():
    with pytest.raises(ValueError):
        u = UriExpression('abc')


def test_uri_expression_invalid_none():
    with pytest.raises(ValueError):
        u = UriExpression(None)


def test_in_expression():
    v = VariableExpression('abc')
    l = (LiteralExpression(5), LiteralExpression(6), LiteralExpression(7))
    i = InExpression(v, *l)
    assert str(i) == '%s IN (%s, %s, %s)' % ((v,) + l)


def test_in_expression_invalid_expression():
    arg1 = VariableExpression('arg1')
    v = VariableExpression('abc')
    f = FunctionExpression('str', arg1)
    a = AsExpression(f, arg1)
    l = (a, LiteralExpression(6), LiteralExpression(7))
    with pytest.raises(TypeError):
        i = InExpression(v, *l)


def test_in_expression_invalid_none():
    v = VariableExpression('abc')
    l = (None, LiteralExpression(6), LiteralExpression(7))
    with pytest.raises(TypeError):
        i = InExpression(v, *l)


def test_regex_expression():
    v = VariableExpression('file')
    regex = r'File(_1)?$'
    r = RegexExpression(v, regex)
    assert str(r) == 'regex(str(%s), "%s", "i")' % (str(v), str(regex))


def test_regex_expression_invalid_expression():
    arg1 = VariableExpression('arg1')
    v = VariableExpression('abc')
    f = FunctionExpression('str', arg1)
    a = AsExpression(f, arg1)
    regex = r'File(_1)?$'
    with pytest.raises(TypeError):
        r = RegexExpression(a, regex)


def test_regex_expression_regex_none():
    v = VariableExpression('file')
    with pytest.raises(ValueError):
        r = RegexExpression(v, None)


def test_regex_expression_none():
    regex = r'File(_1)?$'
    with pytest.raises(ValueError):
        r = RegexExpression(None, regex)
