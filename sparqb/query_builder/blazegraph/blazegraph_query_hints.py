__author__ = 'Nemanja Vukosavljevic <nemanja.vukosavljevic@sbgenomics.com>'
__date__ = '10 June 2016'
__copyright__ = 'Copyright (c) 2016 Seven Bridges Genomics'

from enum import Enum


class Optimizer(Enum):
    none = "None"
    static = "Static"
    runtime = "Runtime"
