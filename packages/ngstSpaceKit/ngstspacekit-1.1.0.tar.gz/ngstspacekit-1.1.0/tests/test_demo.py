from typing import Optional

import ngsolve
import ngsolve.meshes as ngm
import pytest
from ngsolve import (
    GridFunction,
    Integrate,
    Mesh,
    TaskManager,
    sin,
    unit_cube,
    unit_square,
    x,
    y,
)

import ngstSpaceKit
import ngstSpaceKit.demo

from .helper import calc_facet_jump, estimate_facet_moment_jump


def test_crouzeix_raviart_runs():
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))

    crouzeix_raviart = ngstSpaceKit.demo.CrouzeixRaviart(mesh)

    gfu = GridFunction(crouzeix_raviart)
    assert len(gfu.vec) > 0


def test_crouzeix_raviart_rejects_quads():
    mesh = ngm.MakeStructured2DMesh(nx=4, ny=4)

    with pytest.raises(ValueError):
        ngstSpaceKit.demo.CrouzeixRaviart(mesh)


def test_crouzeix_raviart_skips_mesh_check():
    mesh = ngm.MakeStructured2DMesh(nx=4, ny=4)

    ngstSpaceKit.demo.CrouzeixRaviart(mesh, check_mesh=False)


def test_crouzeix_raviart_conformity():
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))

    crouzeix_raviart = ngstSpaceKit.demo.CrouzeixRaviart(mesh)

    gfu = GridFunction(crouzeix_raviart)
    for i in range(crouzeix_raviart.ndof):
        gfu.vec.data[:] = 0
        gfu.vec.data[i] = 1

        assert 0.0 == pytest.approx(estimate_facet_moment_jump(gfu, 0))


@pytest.mark.parametrize("order", [1, 2, 3])
def test_h1_runs(order: int):
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))

    h1 = ngstSpaceKit.demo.H1(mesh, order=order)

    gfu = GridFunction(h1)
    assert len(gfu.vec) > 0


@pytest.mark.parametrize("order", [1, 2, 3])
def test_h1_conformity(order: int):
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))

    h1 = ngstSpaceKit.demo.H1(mesh, order=order)

    gfu = GridFunction(h1)
    for i in range(h1.ndof):
        gfu.vec.data[:] = 0
        gfu.vec.data[i] = 1

        assert 0.0 == pytest.approx(calc_facet_jump(gfu))


@pytest.mark.parametrize("order", [i for i in range(1, 4)])
def test_bdm_runs_2d(order):
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))

    bdm = ngstSpaceKit.demo.BDM(mesh, order=order)

    gfu = GridFunction(bdm)
    assert len(gfu.vec) > 0


@pytest.mark.parametrize("order", [i for i in range(1, 4)])
def test_bdm_runs_3d(order):
    with TaskManager():
        mesh = Mesh(unit_cube.GenerateMesh(maxh=0.25))

        bdm = ngstSpaceKit.demo.BDM(mesh, order=order)

        gfu = GridFunction(bdm)
    assert len(gfu.vec) > 0


@pytest.mark.parametrize("order", [i for i in range(1, 4)])
def test_bdm_rejects_quads(order):
    mesh = ngm.MakeStructured2DMesh(nx=4, ny=4)

    with pytest.raises(ValueError):
        ngstSpaceKit.demo.BDM(mesh, order=order)


def test_bdm_skips_mesh_check():
    mesh = ngm.MakeStructured2DMesh(nx=4, ny=4)

    ngstSpaceKit.demo.BDM(mesh, order=2, check_mesh=False)


def test_bdm_rejects_order_0():
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))

    with pytest.raises(ValueError):
        ngstSpaceKit.demo.BDM(mesh, order=0)


@pytest.mark.parametrize(
    "order, abs_tol", [(1, None), (2, 6e-08), (3, 3e-10), (4, None), (5, None)]
)
def test_bdm_is_close_to_ngsolve(order: int, abs_tol: Optional[float]):
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))
    target_func = x * y * (x, y) * sin(x * y)

    hdiv_ngs = ngsolve.HDiv(mesh, order=order, RT=False)
    gfu_hdiv = GridFunction(hdiv_ngs)
    gfu_hdiv.Set(target_func)
    hdiv_err = Integrate((target_func - gfu_hdiv) ** 2, mesh)

    bdm = ngstSpaceKit.demo.BDM(mesh, order=order)
    gfu_bdm = GridFunction(bdm)
    gfu_bdm.Set(target_func)
    bdm_err = Integrate((target_func - gfu_bdm) ** 2, mesh)

    assert bdm_err == pytest.approx(hdiv_err, abs=abs_tol)
