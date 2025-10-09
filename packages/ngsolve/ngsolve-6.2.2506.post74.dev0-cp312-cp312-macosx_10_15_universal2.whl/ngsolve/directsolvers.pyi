from __future__ import annotations
from ngsolve.comp import BilinearForm
import ngsolve.la
from ngsolve.la import BaseMatrix
from ngsolve.la import BaseVector
import pyngcore.pyngcore
from pyngcore.pyngcore import BitArray
__all__ = ['BaseMatrix', 'BaseVector', 'BilinearForm', 'BitArray', 'SuperLU']
class SuperLU(ngsolve.la.BaseMatrix):
    def Mult(self, x: ngsolve.la.BaseVector, y: ngsolve.la.BaseVector):
        ...
    def Update(self):
        ...
    def __init__(self, a, freedofs: pyngcore.pyngcore.BitArray = None):
        ...
