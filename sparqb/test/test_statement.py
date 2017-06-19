__author__ = 'Jovan Cejovic <jovan.cejovic@sbgenomics.com>'
__date__ = '16 June 2016'
__copyright__ = 'Copyright (c) 2016 Seven Bridges Genomics'

from sparqb.query_builder.statement import *


def test_axiom_statement():
    a = AxiomStatement('a', 'b', 'c')
    assert str(a).strip() == 'a b c .'


# def test_values_statement():
#     v = ValuesStatement()

