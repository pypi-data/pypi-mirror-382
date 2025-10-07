from unittest.mock import patch

import ngsolve.meshes as ngm
import pytest
from ngsolve import GridFunction, Mesh, unit_square

import ngstSpaceKit
from ngstSpaceKit.morley import MorleyDirichlet


def test_morley_dirichlet_clamp():
    dir = MorleyDirichlet.clamp("left")
    assert dir == MorleyDirichlet(vertex_value="left", normal_deriv="left")


def test_morley_runs():
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))

    morley = ngstSpaceKit.Morley(mesh)

    gfu = GridFunction(morley)
    assert len(gfu.vec) > 0


def test_morley_rejects_quads():
    mesh = ngm.MakeStructured2DMesh(nx=4, ny=4)

    with pytest.raises(ValueError):
        ngstSpaceKit.Morley(mesh)


def test_morley_skips_mesh_check():
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))

    with patch(
        "ngstSpaceKit.morley.throw_on_wrong_mesh_eltype"
    ) as throw_on_wrong_mesh_eltype_mock:
        ngstSpaceKit.Morley(mesh, check_mesh=False)
        throw_on_wrong_mesh_eltype_mock.assert_not_called()
