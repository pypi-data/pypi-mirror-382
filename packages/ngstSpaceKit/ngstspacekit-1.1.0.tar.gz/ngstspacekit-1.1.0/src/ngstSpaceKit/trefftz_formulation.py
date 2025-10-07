from typing import Callable

from ngsolve import FESpace
from ngsolve.comp import SumOfIntegrals


class TrefftzFormulation:
    """
    Holds a Trefftz operator, as well as an optional Trefftz right-hand-side.
    """

    _trefftz_op: Callable[[FESpace], SumOfIntegrals]
    _trefftz_rhs: SumOfIntegrals | Callable[[FESpace], SumOfIntegrals] | None
    trefftz_cutoff: float

    def __init__(
        self,
        trefftz_op: Callable[[FESpace], SumOfIntegrals],
        trefftz_rhs: SumOfIntegrals
        | Callable[[FESpace], SumOfIntegrals]
        | None = None,
        trefftz_cutoff: float = 1e-8,
    ) -> None:
        """
        For the spaces form `ngstSpaceKit`,
        you do not need to provide a trial space for the Trefftz formulation.
        Just pass a function / lambda that accepts the trial space and assembles a `SumOfIntegrals`.
            Example:
            ```python
            def top(fes: FESpace) -> SumOfIntegrals:
                u = fes.TrialFunction()
                v = YOUR_TEST_SPACE.TestFunction()
                return u * v * dx
            ```
        Your Trefftz right-hand-side might or might not depend on the trial space,
        or you might not have a right-hand-side.
        """
        self._trefftz_op = trefftz_op
        self._trefftz_rhs = trefftz_rhs
        self.trefftz_cutoff = trefftz_cutoff

    def trefftz_op(self, fes: FESpace) -> SumOfIntegrals:
        """
        Assembles the Trefftz operator as a SumOfIntegrals,
        in dependence on the trial space.
        """
        return self._trefftz_op(fes)

    def trefftz_rhs(self, fes: FESpace) -> SumOfIntegrals | None:
        """
        Assembles the Trefftz right-hand-side as a SumOfIntegrals,
        in dependence on the trial space.
        """
        if self._trefftz_rhs is None:
            return None
        elif isinstance(self._trefftz_rhs, SumOfIntegrals):
            return self._trefftz_rhs
        elif isinstance(self._trefftz_rhs, Callable):
            return self._trefftz_rhs(fes)
        else:
            raise NotImplementedError(self._trefftz_rhs)
