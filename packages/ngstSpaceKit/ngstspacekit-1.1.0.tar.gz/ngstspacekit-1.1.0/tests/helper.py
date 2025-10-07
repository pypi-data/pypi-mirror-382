import numpy as np
from ngsolve import (
    BND,
    ElementId,
    FacetFESpace,
    Grad,
    GridFunction,
    Integrate,
    dx,
    specialcf,
)


def calc_facet_jump(gfu: GridFunction) -> float:
    """
    Calculates the jump of the `gfu` over facets. If the `gfu` is continuous, the jump is zero.
    """
    return Integrate(
        (gfu - gfu.Other()) ** 2 * dx(element_vb=BND), gfu.space.mesh
    )


def estimate_facet_moment_jump(gfu: GridFunction, order: int) -> float:
    """
    Calculates the jump of `<gfu, p>` over facets, where p are polynomials of order `order`. If the `gfu` is continuous, the jump is zero.
    Not all possible polynomials `p` are tested, only 10 are picked at random.

    Returns the maximum jump on a facet found.
    """
    mesh = gfu.space.mesh
    test_fes = FacetFESpace(mesh, order=order) ** gfu.dim

    p = GridFunction(test_fes)

    # use static seed for deterministic results
    rng = np.random.default_rng(1234567890)

    max_jump = 0.0

    # draw 10 random test functions and return the maximum jump
    for _ in range(10):
        p.vec.data = rng.uniform(0.0, 1.0, len(p.vec.data))
        max_jump = max(
            max_jump,
            np.max(
                np.abs(
                    Integrate(
                        (gfu - gfu.Other())
                        * p
                        * dx(element_vb=BND, bonus_intorder=2 * order),
                        gfu.space.mesh,
                        element_wise=True,
                    )
                )
            ),
        )
    return max_jump


def calc_facet_gradient_jump(gfu: GridFunction) -> float:
    """
    Calculates the jump of the gradient of `gfu` over facets. If the `gfu` is C1-conforming, the jump is zero.
    """
    gfu_grad = Grad(gfu)
    return Integrate(
        (gfu_grad - gfu_grad.Other()) ** 2 * dx(element_vb=BND), gfu.space.mesh
    )


def calc_facet_normal_jump(gfu: GridFunction) -> float:
    """
    Calculates the jump of the vector-valued `gfu` in normal direction over facets.
    If the `gfu` is normal-continuous, the jump is zero.
    """
    n = specialcf.normal(gfu.space.mesh.dim)
    return Integrate(
        (gfu * n + gfu.Other() * n.Other()) ** 2 * dx(element_vb=BND),
        gfu.space.mesh,
    )


def estimate_facet_normal_moment_jump(gfu: GridFunction, order: int) -> float:
    """
    Calculates the jump of `<gfu * n, p>` over facets, where p are polynomials of order `order`. If the `gfu` is continuous, the jump is zero.
    Not all possible polynomials `p` are tested, only 10 are picked at random.

    Returns the maximum jump on a facet found.
    """
    mesh = gfu.space.mesh
    test_fes = FacetFESpace(mesh, order=order)

    p = GridFunction(test_fes)
    n = specialcf.normal(mesh.dim)

    # use static seed for deterministic results
    rng = np.random.default_rng(1234567890)

    max_jump = 0.0

    # draw 10 random test functions and return the maximum jump
    for _ in range(10):
        p.vec.data = rng.uniform(0.0, 1.0, len(p.vec.data))
        max_jump = max(
            max_jump,
            np.max(
                np.abs(
                    Integrate(
                        (gfu - gfu.Other() | n)
                        * p
                        * dx(element_vb=BND, bonus_intorder=2 * order),
                        gfu.space.mesh,
                        element_wise=True,
                    )
                )
            ),
        )
    return max_jump
