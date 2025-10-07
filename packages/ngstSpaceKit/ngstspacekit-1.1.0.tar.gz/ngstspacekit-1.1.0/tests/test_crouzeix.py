import ngsolve.meshes as ngm
import pytest
from ngsolve import GridFunction, Mesh, unit_square

import ngstSpaceKit

from .helper import estimate_facet_moment_jump


def test_crouzeix_falk_runs():
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))

    crouzeix_falk = ngstSpaceKit.CrouzeixFalk(mesh)

    gfu = GridFunction(crouzeix_falk)
    assert len(gfu.vec) > 0


def test_crouzeix_falk_rejects_quads():
    mesh = ngm.MakeStructured2DMesh(nx=4, ny=4)

    with pytest.raises(ValueError):
        ngstSpaceKit.CrouzeixFalk(mesh)


def test_crouzeix_falk_skips_mesh_check():
    mesh = ngm.MakeStructured2DMesh(nx=4, ny=4)

    ngstSpaceKit.CrouzeixFalk(mesh, check_mesh=False)


@pytest.mark.parametrize("conformity_order", range(3))
def test_crouzeix_falk_conformity(conformity_order: int):
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))

    crouzeix_falk = ngstSpaceKit.CrouzeixFalk(mesh)

    gfu = GridFunction(crouzeix_falk)
    for i in range(crouzeix_falk.ndof):
        gfu.vec.data[:] = 0
        gfu.vec.data[i] = 1

        assert 0.0 == pytest.approx(
            estimate_facet_moment_jump(gfu, conformity_order)
        )


def test_crouzeix_ho_runs():
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))

    crouzeix_ho = ngstSpaceKit.CrouzeixHO(mesh, order=5)

    gfu = GridFunction(crouzeix_ho)
    assert len(gfu.vec) > 0


@pytest.mark.parametrize("conformity_order", range(5))
def test_crouzeix_ho_conformity(conformity_order: int):
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))

    crouzeix_ho = ngstSpaceKit.CrouzeixHO(mesh, 5)

    gfu = GridFunction(crouzeix_ho)
    for i in range(crouzeix_ho.ndof):
        gfu.vec.data[:] = 0
        gfu.vec.data[i] = 1

        assert 0.0 == pytest.approx(
            estimate_facet_moment_jump(gfu, conformity_order)
        )


def test_crouzeix_ho_rejects_quads():
    mesh = ngm.MakeStructured2DMesh(nx=4, ny=4)

    with pytest.raises(ValueError):
        ngstSpaceKit.CrouzeixHO(mesh, order=5)


def test_crouzeix_ho_skips_mesh_check():
    mesh = ngm.MakeStructured2DMesh(nx=4, ny=4)

    ngstSpaceKit.CrouzeixHO(mesh, order=5, check_mesh=False)


def test_crouzeix_falk_ho_quads():
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))

    with pytest.raises(ValueError):
        ngstSpaceKit.CrouzeixHO(mesh, order=4)
