import ngsolve.meshes as ngm
import pytest
from ngsolve import ET, Mesh, unit_square

from ngstSpaceKit.mesh_properties import (
    throw_on_wrong_mesh_dimension,
    throw_on_wrong_mesh_eltype,
)


def test_throw_on_wrong_meshtype():
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))

    with pytest.raises(ValueError):
        throw_on_wrong_mesh_eltype(mesh, {ET.HEX, ET.QUAD})


def test_do_not_throw_on_correct_meshtype():
    mesh = ngm.MakeStructured2DMesh(nx=4, ny=4)

    throw_on_wrong_mesh_eltype(mesh, {ET.HEX, ET.QUAD})


def test_thorw_on_wrong_mesh_dim():
    mesh = Mesh(ngm.unit_cube.GenerateMesh(maxh=0.25))

    with pytest.raises(ValueError):
        throw_on_wrong_mesh_dimension(mesh, 2)


def test_do_not_thorw_on_correct_mesh_dim():
    mesh = Mesh(ngm.unit_cube.GenerateMesh(maxh=0.25))

    throw_on_wrong_mesh_dimension(mesh, 3)
