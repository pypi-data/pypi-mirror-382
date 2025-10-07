import ngsolve.meshes as ngm
import pytest
from ngsolve import GridFunction, Mesh, unit_square

import ngstSpaceKit
from ngstSpaceKit.argyris import ArgyrisDirichlet

from .helper import calc_facet_gradient_jump, calc_facet_jump


def test_argyris_dirichlet_clamp():
    dir = ArgyrisDirichlet.clamp_weak("left")
    assert dir == ArgyrisDirichlet(
        vertex_value="left",
        deriv_x="left",
        deriv_y="left",
        deriv_normal_moment="left",
    )


def test_argyris_runs():
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))

    argyris = ngstSpaceKit.Argyris(mesh)

    gfu = GridFunction(argyris)
    assert len(gfu.vec) > 0


def test_argyris_rejects_quads():
    mesh = ngm.MakeStructured2DMesh(nx=4, ny=4)

    with pytest.raises(ValueError):
        ngstSpaceKit.Argyris(mesh)


@pytest.mark.parametrize("order", [5, 6])
def test_argyris_skips_mesh_check(order):
    mesh = ngm.MakeStructured2DMesh(nx=4, ny=4)

    ngstSpaceKit.Argyris(mesh, order, check_mesh=False)


def test_argyris_rejects_low_order():
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))

    with pytest.raises(ValueError):
        ngstSpaceKit.Argyris(mesh, order=4)


def test_argyris_ho_rejects_low_order():
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))

    with pytest.raises(ValueError):
        ngstSpaceKit.argyris.ArgyrisHO(mesh, order=5)


@pytest.mark.parametrize("order", [5, 6, 7])
def test_argyris_is_continuous(order):
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))
    argyris = ngstSpaceKit.Argyris(mesh, order=order)
    gfu = GridFunction(argyris)

    for i in range(argyris.ndof):
        gfu.vec.data[:] = 0
        gfu.vec.data[i] = 100

        assert calc_facet_jump(gfu) == pytest.approx(0)


@pytest.mark.parametrize("order", [5, 6, 7])
def test_argyris_grad_is_continuous(order):
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))
    argyris = ngstSpaceKit.Argyris(mesh, order=order)
    gfu = GridFunction(argyris)

    for i in range(argyris.ndof):
        gfu.vec.data[:] = 0
        gfu.vec.data[i] = 100

        assert calc_facet_gradient_jump(gfu) == pytest.approx(0)
