from ngsolve import H1, BilinearForm, FESpace, Mesh, dx, unit_square
from ngsolve.utils import SumOfIntegrals

from ngstSpaceKit.trefftz_formulation import TrefftzFormulation


def sum_of_ints(fes: FESpace) -> SumOfIntegrals:
    u, v = fes.TnT()
    return u * v * dx


def test_trefftz_op():
    formulation = TrefftzFormulation(sum_of_ints)

    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))
    fes = H1(mesh, order=2)

    a = BilinearForm(fes)
    a += formulation.trefftz_op(fes)
    a.Assemble()

    b = BilinearForm(fes)
    b += sum_of_ints(fes)
    b.Assemble()

    for i in range(a.mat.height):
        for j in range(a.mat.width):
            assert a.mat.ToDense()[(i, j)] == b.mat.ToDense()[(i, j)]


def test_trefftz_rhs_none():
    formulation = TrefftzFormulation(sum_of_ints)

    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))
    fes = H1(mesh, order=2)

    assert formulation.trefftz_rhs(fes) is None


def test_trefftz_rhs_from_sumofint():
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))
    fes = H1(mesh, order=2)

    formulation = TrefftzFormulation(sum_of_ints, sum_of_ints(fes))

    a = BilinearForm(fes)
    trhs = formulation.trefftz_rhs(fes)
    assert trhs is not None
    a += trhs
    a.Assemble()

    b = BilinearForm(fes)
    b += sum_of_ints(fes)
    b.Assemble()

    for i in range(a.mat.height):
        for j in range(a.mat.width):
            assert a.mat.ToDense()[(i, j)] == b.mat.ToDense()[(i, j)]


def test_trefftz_rhs_from_callable():
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))
    fes = H1(mesh, order=2)

    formulation = TrefftzFormulation(sum_of_ints, trefftz_rhs=sum_of_ints)

    a = BilinearForm(fes)
    trhs = formulation.trefftz_rhs(fes)
    assert trhs is not None
    a += trhs
    a.Assemble()

    b = BilinearForm(fes)
    b += sum_of_ints(fes)
    b.Assemble()

    for i in range(a.mat.height):
        for j in range(a.mat.width):
            assert a.mat.ToDense()[(i, j)] == b.mat.ToDense()[(i, j)]
