import ngsolve.meshes as ngm
import pytest
from ngsolve import GridFunction, Mesh, unit_square

import ngstSpaceKit
from ngstSpaceKit.bfs import BFSDirichlet

from .helper import calc_facet_gradient_jump, calc_facet_jump


def test_bfs_dirichlet_clamp():
    dir = BFSDirichlet.clamp_weak("left")
    assert dir == BFSDirichlet(
        vertex_value="left", deriv_x="left", deriv_y="left"
    )


def test_bfs_runs():
    mesh = ngm.MakeStructured2DMesh(nx=4, ny=4)

    bfs = ngstSpaceKit.BognerFoxSchmitt(mesh)

    gfu = GridFunction(bfs)
    assert len(gfu.vec) > 0


def test_bfs_rejects_triangles():
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))

    with pytest.raises(ValueError):
        ngstSpaceKit.BognerFoxSchmitt(mesh)


def test_bfs_skips_mesh_check():
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))

    ngstSpaceKit.BognerFoxSchmitt(mesh, check_mesh=False)


def test_bfs_is_continuous():
    mesh = ngm.MakeStructured2DMesh(nx=4, ny=4)
    bfs = ngstSpaceKit.BognerFoxSchmitt(mesh)
    gfu = GridFunction(bfs)

    for i in range(bfs.ndof):
        gfu.vec.data[:] = 0
        gfu.vec.data[i] = 1

        assert calc_facet_jump(gfu) == pytest.approx(0)


def test_bfs_grad_is_continuous():
    mesh = ngm.MakeStructured2DMesh(nx=4, ny=4)
    bfs = ngstSpaceKit.BognerFoxSchmitt(mesh)
    gfu = GridFunction(bfs)

    for i in range(bfs.ndof):
        gfu.vec.data[:] = 0
        gfu.vec.data[i] = 1

        assert calc_facet_gradient_jump(gfu) == pytest.approx(0)
