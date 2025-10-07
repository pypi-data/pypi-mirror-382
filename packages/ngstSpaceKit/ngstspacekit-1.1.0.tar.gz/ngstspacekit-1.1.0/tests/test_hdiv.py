from typing import Optional
from unittest.mock import patch

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

from .helper import calc_facet_normal_jump


@pytest.mark.parametrize(
    "order, normal_continuity",
    [
        (order, normal_cont)
        for order in range(1, 4)
        for normal_cont in range(0, 4)
        if order >= normal_cont
    ],
)
def test_hdiv_runs(order, normal_continuity):
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))

    bdm = ngstSpaceKit.HDiv(
        mesh, order=order, normal_continuity=normal_continuity
    )

    gfu = GridFunction(bdm)
    assert len(gfu.vec) > 0


@pytest.mark.parametrize(
    "order, normal_continuity",
    [
        (order, normal_cont)
        for order in range(1, 4)
        for normal_cont in range(0, 6)
        if order < normal_cont
    ],
)
def test_hdiv_rejects_too_high_normal_continuity(order, normal_continuity):
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))

    with pytest.raises(ValueError):
        _ = ngstSpaceKit.HDiv(
            mesh, order=order, normal_continuity=normal_continuity
        )


@pytest.mark.parametrize(
    "order, abs_tol", [(1, None), (2, None), (3, None), (4, None), (5, None)]
)
def test_hdiv_is_better_than_ngsolve(order: int, abs_tol: Optional[float]):
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))
    target_func = x * y * (x, y) * sin(x * y)

    hdiv_orig = ngsolve.HDiv(mesh, order=order, RT=False)
    gfu_hdiv = GridFunction(hdiv_orig)
    gfu_hdiv.Set(target_func)
    hdiv_err = Integrate((target_func - gfu_hdiv) ** 2, mesh)

    hdiv_ngse = ngstSpaceKit.HDiv(mesh, order=order)
    gfu_ngse = GridFunction(hdiv_ngse)
    gfu_ngse.Set(target_func)
    ngse_hdiv_err = Integrate((target_func - gfu_ngse) ** 2, mesh)

    assert ngse_hdiv_err <= hdiv_err or ngse_hdiv_err == pytest.approx(hdiv_err)


@pytest.mark.parametrize("order", [i for i in range(1, 4)])
def test_hdiv_is_normal_continuous(order):
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))

    hdiv = ngstSpaceKit.HDiv(mesh, order=order)

    gfu = GridFunction(hdiv)

    for i in range(hdiv.ndof):
        gfu.vec.data[:] = 0
        gfu.vec.data[i] = 1

        assert calc_facet_normal_jump(gfu) == pytest.approx(0)


@pytest.mark.parametrize("order", [i for i in range(1, 3)])
def test_hdiv_3d_is_normal_continuous(order):
    with TaskManager():
        mesh = Mesh(unit_cube.GenerateMesh(maxh=0.4))

        hdiv = ngstSpaceKit.HDiv(mesh, order=order)

        gfu = GridFunction(hdiv)

        for i in range(hdiv.ndof):
            gfu.vec.data[:] = 0
            gfu.vec.data[i] = 1

            assert calc_facet_normal_jump(gfu) == pytest.approx(0)


def test_hdiv_rejects_quads():
    mesh = ngm.MakeStructured2DMesh(nx=4, ny=4)

    with pytest.raises(ValueError):
        ngstSpaceKit.HDiv(mesh, 2)


def test_hdiv_skips_mesh_check():
    mesh = Mesh(unit_cube.GenerateMesh(maxh=0.25))

    with patch(
        "ngstSpaceKit.hdiv.throw_on_wrong_mesh_eltype"
    ) as throw_on_wrong_mesh_eltype_mock:
        ngstSpaceKit.HDiv(mesh, 3, check_mesh=False)
        throw_on_wrong_mesh_eltype_mock.assert_not_called()
