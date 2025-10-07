from unittest.mock import patch

import ngsolve.meshes as ngm
import pytest
from ngsolve import GridFunction, Mesh, unit_cube, unit_square

import ngstSpaceKit
from ngstSpaceKit.hermite import HermiteDirichlet

from .helper import calc_facet_jump


def test_hermite_dirichlet_clamp():
    dir = HermiteDirichlet.clamp("left")
    assert dir == HermiteDirichlet(
        vertex_value="left", deriv_x="left", deriv_y="left", deriv_z="left"
    )


def test_hermite_runs():
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))

    hermite = ngstSpaceKit.Hermite(mesh)

    gfu = GridFunction(hermite)
    assert len(gfu.vec) > 0


def test_hermite_3d_runs():
    mesh = Mesh(unit_cube.GenerateMesh(maxh=0.25))

    hermite = ngstSpaceKit.Hermite(mesh)

    gfu = GridFunction(hermite)
    assert len(gfu.vec) > 0


def test_hermite_rejects_quads():
    mesh = ngm.MakeStructured2DMesh(nx=4, ny=4)

    with pytest.raises(ValueError):
        ngstSpaceKit.Hermite(mesh)


def test_hermite_skips_mesh_check():
    mesh = ngm.MakeStructured2DMesh(nx=4, ny=4)

    ngstSpaceKit.Hermite(mesh, check_mesh=False)


def test_hermite_2d_rejects_quads():
    mesh = ngm.MakeStructured2DMesh(nx=4, ny=4)

    with pytest.raises(ValueError):
        ngstSpaceKit.hermite.Hermite2D(mesh, dirichlet=HermiteDirichlet())


def test_hermite_2d_skips_mesh_check():
    mesh = ngm.MakeStructured2DMesh(nx=4, ny=4)

    ngstSpaceKit.hermite.Hermite2D(
        mesh, check_mesh=False, dirichlet=HermiteDirichlet()
    )


def test_hermite_3d_rejects_quads():
    mesh = ngm.MakeStructured3DMesh(nx=4, ny=4, nz=4)

    with pytest.raises(ValueError):
        ngstSpaceKit.hermite.Hermite3D(mesh, dirichlet=HermiteDirichlet())


def test_hermite_3d_skips_mesh_check():
    mesh = Mesh(unit_cube.GenerateMesh(maxh=0.25))

    with patch(
        "ngstSpaceKit.hermite.throw_on_wrong_mesh_eltype"
    ) as throw_on_wrong_mesh_eltype_mock:
        ngstSpaceKit.hermite.Hermite3D(
            mesh, check_mesh=False, dirichlet=HermiteDirichlet()
        )
        throw_on_wrong_mesh_eltype_mock.assert_not_called()


def test_hermite_is_continuous():
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))
    hermite = ngstSpaceKit.Hermite(mesh)
    gfu = GridFunction(hermite)

    for i in range(hermite.ndof):
        gfu.vec.data[:] = 0
        gfu.vec.data[i] = 1

        assert calc_facet_jump(gfu) == pytest.approx(0)
