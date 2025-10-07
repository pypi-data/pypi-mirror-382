from typing import Optional

import ngsolve
from ngsolve import (
    BND,
    TET,
    TRIG,
    NormalFacetFESpace,
    VectorL2,
    dx,
    specialcf,
)
from ngstrefftz import (
    EmbeddedTrefftzFES,
    TrefftzEmbedding,
    VectorL2EmbTrefftzFESpace,
)

from ngstSpaceKit.mesh_properties import (
    throw_on_wrong_mesh_dimension,
    throw_on_wrong_mesh_eltype,
)
from ngstSpaceKit.trefftz_formulation import TrefftzFormulation


def HDiv(
    mesh: ngsolve.comp.Mesh,
    order: int,
    normal_continuity: Optional[int] = None,
    trefftz_formulation: Optional[TrefftzFormulation] = None,
    dirichlet: str = "",
    check_mesh: bool = True,
    stats: dict | None = None,
) -> VectorL2EmbTrefftzFESpace:
    r"""
    The `HDiv` space is H(div)-conforming.

    `mesh`: mesh to build the space on

    `order`: polynomial order of the space

    `normal_continuity`: up to which order the space shall be normally continuous.
        Default: `None`, then `normal_continuity == order` is set.
        It shall hold that `normal_continuity <= order`.

    `check_mesh`: test, if the `mesh` is compatible with this space

    `stats`: use the `stats` flag of the `TrefftzEmbeddin` method

    # Raises
        - ValueError, if `order == 0`
        - ValueError, if `normal_continuity > order`
        - ValueError, if the mesh is not 2D or 3D
        - ValueError, if the mesh is not triangular (2D) or consists of tetrahedra (3D)

    # Conforming Trefftz Formulation
    - $\mathbb{V}_h := [\mathbb{P}^{k, \text{disc}}(\mathcal{T}_h)]^d$
    - $\mathbb{Z}_h := [\mathbb{P}^k(\mathcal{F}_h)]^d$
    - \begin{align}
      \mathcal{C}_K(v_h, z_h) &:=
          \int_{\partial K} v_h \cdot n \; z_h \cdot n \;dS \\\\
      \mathcal{D}_K(y_h, z_h) &:=
          \int_{\partial K} y_h \cdot n \; z_h \cdot n \;dS
      \end{align}
    """
    if check_mesh:
        throw_on_wrong_mesh_dimension(mesh, [2, 3])
        throw_on_wrong_mesh_eltype(mesh, [TRIG, TET])

    if normal_continuity is None:
        normal_continuity = order

    if normal_continuity > order:
        raise ValueError(
            f"normal_continuity == {normal_continuity} > {order} == order is not allowed"
        )

    fes = VectorL2(mesh, order=order)

    conformity_space = NormalFacetFESpace(
        mesh, order=normal_continuity, dirichlet=dirichlet
    )

    u = fes.TrialFunction()

    uc, vc = conformity_space.TnT()

    n = specialcf.normal(mesh.dim)

    cop_l = u * n * vc * n * dx(element_vb=BND)
    cop_r = uc * n * vc * n * dx(element_vb=BND)

    if trefftz_formulation is not None:
        top = trefftz_formulation.trefftz_op(fes)
        trhs = trefftz_formulation.trefftz_rhs(fes)
        trefftz_cutoff = trefftz_formulation.trefftz_cutoff
    else:
        top = None
        trhs = None
        trefftz_cutoff = 0.0

    embedding = TrefftzEmbedding(
        top=top,
        trhs=trhs,
        cop=cop_l,
        crhs=cop_r,
        eps=trefftz_cutoff,
        stats=stats,
    )

    hdiv = EmbeddedTrefftzFES(embedding)
    assert type(hdiv) is VectorL2EmbTrefftzFESpace, (
        "The HDiv space should always be a VectorL2EmbTrefftzFESpace"
    )

    return hdiv
