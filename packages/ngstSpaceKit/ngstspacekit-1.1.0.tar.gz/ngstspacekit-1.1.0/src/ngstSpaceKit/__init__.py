"""
`ngstSpaceKit` implements several spaces, that are currently not implemented
in `ngoslve`.
In `ngstSpaceKit.demo` you find spaces, that are natively implemented in `ngsolve` already.

[![ngstSpaceKit repository](https://get-it-on.codeberg.org/get-it-on-blue-on-white.png)](https://codeberg.org/johann-cm/ngstspacekit)
"""

__all__ = [
    "Argyris",
    "BognerFoxSchmitt",
    "CrouzeixFalk",
    "CrouzeixHO",
    "HDiv",
    "Hermite",
    "ImmersedP1FE",
    "ImmersedQ1FE",
    "Morley",
    "TrefftzFormulation",
    "WeakH1",
    "WeakStokes",
]

from .argyris import Argyris
from .bfs import BognerFoxSchmitt
from .crouzeix import CrouzeixFalk, CrouzeixHO
from .hdiv import HDiv
from .hermite import Hermite
from .immersedfe import ImmersedP1FE, ImmersedQ1FE
from .morley import Morley
from .stokes import WeakStokes
from .trefftz_formulation import TrefftzFormulation
from .weak_h1 import WeakH1
