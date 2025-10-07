import itertools
from unittest.mock import patch

import ngsolve.meshes as ngm
import numpy
import pytest
from ngsolve import (
    H1,
    CoefficientFunction,
    GridFunction,
    Integrate,
    Mesh,
    Normalize,
    sqrt,
    unit_square,
    x,
    y,
)
from xfem import IF, CutInfo, InterpolateToP1, dCut

from ngstSpaceKit.diffops import grad
from ngstSpaceKit.immersedfe import ImmersedP1FE, ImmersedQ1FE, ImmersedQ1Impl

betas = [0.1, 1.0, 1e2]
lsetfns = [x + y - 0.5, x - y, x - y / 2 - 3 / 4, x - 0.3]


@pytest.mark.parametrize(
    "beta_neg, beta_pos, lsetfn", itertools.product(betas, betas, lsetfns)
)
def test_cut_jump(
    beta_neg: float, beta_pos: float, lsetfn: CoefficientFunction
):
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))

    ife = ImmersedP1FE(mesh, lsetfn, beta_neg, beta_pos)
    gfu = GridFunction(ife)

    for i in range(ife.ndof):
        gfu.vec.data[:] = 0
        gfu.vec.data[i] = 1

        gfu_emb = GridFunction(ife.emb.fes)
        gfu_emb.vec.data = ife.emb.Embed(gfu.vec)

        assert sqrt(
            Integrate(
                (gfu_emb.components[0] - gfu_emb.components[1]) ** 2
                * dCut(lsetfn, IF, order=2),
                mesh,
            )
        ) == pytest.approx(0.0, abs=1e-9)


@pytest.mark.parametrize(
    "beta_neg, beta_pos, lsetfn", itertools.product(betas, betas, lsetfns)
)
def test_cut_normal_deriv_jump(
    beta_neg: float, beta_pos: float, lsetfn: CoefficientFunction
):
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))

    ife = ImmersedP1FE(mesh, lsetfn, beta_neg, beta_pos)
    gfu = GridFunction(ife)

    for i in range(ife.ndof):
        gfu.vec.data[:] = 0
        gfu.vec.data[i] = 1

        gfu_emb = GridFunction(ife.emb.fes)
        gfu_emb.vec.data = ife.emb.Embed(gfu.vec)

        n = Normalize(grad(lsetfn, mesh.dim))
        assert sqrt(
            Integrate(
                (
                    beta_neg * grad(gfu_emb.components[0]) * n
                    - beta_pos * grad(gfu_emb.components[1]) * n
                )
                ** 2
                * dCut(lsetfn, IF, order=2),
                mesh,
            )
        ) == pytest.approx(0.0)


def test_ifes_rejects_quads():
    mesh = ngm.MakeStructured2DMesh(nx=4, ny=4)

    with pytest.raises(ValueError):
        ImmersedP1FE(mesh, x - y, 1.0, 10.0)


def test_ifes_skips_mesh_check():
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))

    with patch(
        "ngstSpaceKit.immersedfe.throw_on_wrong_mesh_eltype"
    ) as throw_on_wrong_mesh_eltype_mock:
        ImmersedP1FE(mesh, x - y, 1.0, 10.0, check_mesh=False)
        throw_on_wrong_mesh_eltype_mock.assert_not_called()


@pytest.mark.parametrize(
    "beta_neg, beta_pos, lsetfn", itertools.product(betas, betas, lsetfns)
)
def test_cut_jump_q1(
    beta_neg: float, beta_pos: float, lsetfn: CoefficientFunction
):
    mesh = ngm.MakeStructured2DMesh(nx=4, ny=4)
    fn_gfu = GridFunction(H1(mesh, order=1))
    InterpolateToP1(lsetfn, fn_gfu)

    ife = ImmersedQ1FE(
        mesh, fn_gfu, beta_neg, beta_pos, impl=ImmersedQ1Impl.Canonical
    )
    gfu = GridFunction(ife)
    ci = CutInfo(mesh, fn_gfu)

    for i in range(ife.ndof):
        gfu.vec.data[:] = 0
        gfu.vec.data[i] = 1

        gfu_emb = GridFunction(ife.emb.fes)
        gfu_emb.vec.data = ife.emb.Embed(gfu.vec)

        assert sqrt(
            Integrate(
                (gfu_emb.components[0] - gfu_emb.components[1]) ** 2
                * dCut(
                    fn_gfu,
                    IF,
                    definedonelements=ci.GetElementsOfType(IF),
                    order=6,
                ),
                mesh,
            )
        ) == pytest.approx(0.0, abs=7e-5)


@pytest.mark.parametrize(
    "beta_neg, beta_pos, lsetfn", itertools.product(betas, betas, lsetfns)
)
def test_cut_normal_deriv_jump_q1(
    beta_neg: float, beta_pos: float, lsetfn: CoefficientFunction
):
    mesh = ngm.MakeStructured2DMesh(nx=4, ny=4)
    fn_gfu = GridFunction(H1(mesh, order=1))
    InterpolateToP1(lsetfn, fn_gfu)

    ife = ImmersedQ1FE(
        mesh, fn_gfu, beta_neg, beta_pos, impl=ImmersedQ1Impl.Canonical
    )
    gfu = GridFunction(ife)
    ci = CutInfo(mesh, fn_gfu)

    for i in range(ife.ndof):
        gfu.vec.data[:] = 0
        gfu.vec.data[i] = 1

        gfu_emb = GridFunction(ife.emb.fes)
        gfu_emb.vec.data = ife.emb.Embed(gfu.vec)

        n = Normalize(grad(fn_gfu, mesh.dim))
        assert numpy.allclose(
            Integrate(
                (
                    beta_neg * grad(gfu_emb.components[0]) * n
                    - beta_pos * grad(gfu_emb.components[1]) * n
                )
                * dCut(
                    fn_gfu,
                    IF,
                    definedonelements=ci.GetElementsOfType(IF),
                    order=4,
                ),
                mesh,
                element_wise=True,
            ),
            0,
            atol=7e-4,
        )
