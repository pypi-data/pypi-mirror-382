import pytest
from ngsolve import (
    CF,
    H1,
    GridFunction,
    Integrate,
    Mesh,
    VectorH1,
    unit_square,
    x,
    y,
)

from ngstSpaceKit.diffops import div, grad, laplace


def test_grad_cf():
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.2))

    cf = x * y
    cf_grad = CF((y, x))

    assert Integrate((grad(cf, 2) - cf_grad) ** 2, mesh) == pytest.approx(0.0)


def test_grad_cf_needs_meshdim():
    cf = x * y

    with pytest.raises(AssertionError):
        grad(cf)


def test_div_cf_linear():
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.2))

    cf = CF((x + y, 2 * y - x))
    cf_div = CF(1 + 2)

    assert Integrate((div(cf) - cf_div) ** 2, mesh) == pytest.approx(0.0)


def test_div_cf_polynomial():
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.2))

    cf = CF((x**2 + y**3, x**2 + y**3))
    cf_div = CF(2 * x + 3 * y**2)

    assert Integrate((div(cf) - cf_div) ** 2, mesh) == pytest.approx(0.0)


def test_grad_gfu():
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.2))

    cf = x**2 * y
    fes = H1(mesh, order=3)
    gfu = GridFunction(fes)
    gfu.Set(cf)

    cf_grad = CF((2 * x * y, x**2))
    fes_grad = VectorH1(mesh, order=2)
    gfu_grad = GridFunction(fes_grad)
    gfu_grad.Set(cf_grad)

    assert Integrate((grad(gfu) - gfu_grad) ** 2, mesh) == pytest.approx(0.0)


def test_laplace_cf_scalar():
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.2))

    cf = x**2 + y**3
    cf_laplace = 2 + 6 * y

    assert Integrate((laplace(cf) - cf_laplace) ** 2, mesh) == pytest.approx(
        0.0
    )


def test_laplace_cf_vectorial():
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.2))

    cf = CF((x**2 + y**3, x**3 + y**2))
    cf_laplace = CF((2 + 6 * y, 6 * x + 2))

    assert Integrate((laplace(cf) - cf_laplace) ** 2, mesh) == pytest.approx(
        0.0
    )


def test_laplace_gfu_scalar():
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.2))

    cf = x**2 + y**3
    fes = H1(mesh, order=3)
    gfu = GridFunction(fes)
    gfu.Set(cf)

    cf_laplace = 2 + 6 * y
    fes_laplace = H1(mesh, order=1)
    gfu_laplace = GridFunction(fes_laplace)
    gfu_laplace.Set(cf_laplace)

    assert Integrate((laplace(gfu) - gfu_laplace) ** 2, mesh) == pytest.approx(
        0.0
    )


def test_laplace_gfu_vectorial():
    mesh = Mesh(unit_square.GenerateMesh(maxh=0.2))

    cf = CF((x**2 + y**3, x**3 + y**2))
    fes = VectorH1(mesh, order=3)
    gfu = GridFunction(fes)
    gfu.Set(cf)

    cf_laplace = CF((2 + 6 * y, 6 * x + 2))
    fes_laplace = VectorH1(mesh, order=1)
    gfu_laplace = GridFunction(fes_laplace)
    gfu_laplace.Set(cf_laplace)

    assert Integrate((laplace(gfu) - gfu_laplace) ** 2, mesh) == pytest.approx(
        0.0
    )
