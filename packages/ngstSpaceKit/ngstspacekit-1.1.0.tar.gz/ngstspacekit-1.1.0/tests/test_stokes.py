import itertools
from unittest.mock import patch

import ngsolve.meshes as ngm
import pytest
from ngsolve import GridFunction, Integrate, Mesh, unit_square

import ngstSpaceKit

from .helper import calc_facet_normal_jump, estimate_facet_normal_moment_jump


def test_weak_stokes_no_conformity():
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.4))

    weak_stokes = ngstSpaceKit.stokes.WeakStokes(
        mesh, 3, normal_continuity=None
    )

    gfu = GridFunction(weak_stokes)
    emb = weak_stokes.emb
    gfu_embedded = GridFunction(emb.fes)
    for i in range(weak_stokes.ndof):
        gfu.vec.data[:] = 0
        gfu.vec.data[i] = 100
        gfu_embedded.vec.data = emb.Embed(gfu.vec)

        assert (
            1e-2 < calc_facet_normal_jump(gfu_embedded.components[0])
            or Integrate(gfu_embedded.components[0].Norm(), mesh) == 0
        )


@pytest.mark.parametrize(
    "conformity_order, use_stokes_top",
    itertools.product(range(5), [True, False]),
)
def test_weak_stokes_conformity(conformity_order: int, use_stokes_top: bool):
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.4))

    weak_stokes = ngstSpaceKit.stokes.WeakStokes(
        mesh, 5, conformity_order, use_stokes_top=use_stokes_top
    )

    gfu = GridFunction(weak_stokes)
    emb = weak_stokes.emb
    gfu_embedded = GridFunction(emb.fes)
    for i in range(weak_stokes.ndof):
        gfu.vec.data[:] = 0
        gfu.vec.data[i] = 1
        gfu_embedded.vec.data = emb.Embed(gfu.vec)

        assert 0.0 == pytest.approx(
            estimate_facet_normal_moment_jump(
                gfu_embedded.components[0], conformity_order
            )
        )


@pytest.mark.parametrize("order", range(-1, 2))
def test_weak_stokes_rejects_low_order(order: int):
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))

    with pytest.raises(ValueError):
        ngstSpaceKit.stokes.WeakStokes(mesh, order)


def test_weak_stokes_rejects_quads():
    mesh = ngm.MakeStructured3DMesh(nx=4, ny=4, nz=4)

    with pytest.raises(ValueError):
        ngstSpaceKit.WeakStokes(mesh, 3)


def test_weak_stokes_skips_mesh_check():
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))

    with patch(
        "ngstSpaceKit.stokes.throw_on_wrong_mesh_eltype"
    ) as throw_on_wrong_mesh_eltype_mock:
        ngstSpaceKit.stokes.WeakStokes(mesh, 3, check_mesh=False)
        throw_on_wrong_mesh_eltype_mock.assert_not_called()
