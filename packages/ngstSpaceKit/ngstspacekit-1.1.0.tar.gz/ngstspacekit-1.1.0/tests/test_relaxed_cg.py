import pytest
from ngsolve import GridFunction, Mesh, unit_square

import ngstSpaceKit.weak_h1

from .helper import estimate_facet_moment_jump


def test_relaxed_cg_runs():
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))

    rcg = ngstSpaceKit.weak_h1.RelaxedCGConformity(mesh, 3, 1)

    gfu = GridFunction(rcg)
    assert len(gfu.vec) > 0


@pytest.mark.parametrize("conformity_order", range(5))
def test_relaxed_cg_conformity(conformity_order: int):
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))

    crouzeix_falk = ngstSpaceKit.weak_h1.RelaxedCGConformity(
        mesh, 5, conformity_order
    )

    gfu = GridFunction(crouzeix_falk)
    for i in range(crouzeix_falk.ndof):
        gfu.vec.data[:] = 0
        gfu.vec.data[i] = 1

        assert 0.0 == pytest.approx(
            estimate_facet_moment_jump(gfu, conformity_order)
        )


@pytest.mark.parametrize("vertex_conforming", [True, False])
def test_weak_h1_runs(vertex_conforming: bool):
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))

    rcg = ngstSpaceKit.WeakH1(
        mesh, 3, vertex_conforming, facet_conformity_order=2
    )

    gfu = GridFunction(rcg)
    assert len(gfu.vec) > 0


def test_weak_h1_rejects_overgrown_facet_conformity():
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))

    with pytest.raises(ValueError) as _:
        ngstSpaceKit.WeakH1(mesh, 3, False, facet_conformity_order=4)
