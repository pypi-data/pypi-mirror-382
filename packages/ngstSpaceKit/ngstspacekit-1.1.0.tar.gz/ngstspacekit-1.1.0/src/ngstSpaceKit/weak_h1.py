from ngsolve import (
    BBND,
    BND,
    H1,
    L2,
    FacetFESpace,
    Mesh,
    dx,
)
from ngstrefftz import EmbeddedTrefftzFES, L2EmbTrefftzFESpace, TrefftzEmbedding

from ngstSpaceKit import bubbles
from ngstSpaceKit.trefftz_formulation import TrefftzFormulation


def WeakH1(
    mesh: Mesh,
    order: int,
    vertex_conforming: bool,
    facet_conformity_order: int,
    trefftz_formulation: TrefftzFormulation | None = None,
    dirichlet: str = "",
    dgjumps: bool = False,
    stats: dict | None = None,
) -> L2EmbTrefftzFESpace:
    """
    The WeakH1 space
    - is continuous on mesh vertices, if `vertex_conforming` is `True`
    - is conforming up to polynomial degree `conformity_order` across facets

    If there are dofs not occupied by the conformity constraints,
    you can provide a Trefftz operator to make use of them.

    `stats`: use the `stats` flag of the `TrefftzEmbeddin` method

    # Raises
    - `ValueError`, if `facet_conformity_order > order`

    # Conforming Trefftz Formulation
    If `vertex_conforming == True`, see `ngstSpaceKit.weak_h1.RelaxedFacetConforming`,
    else see `ngstSpaceKit.weak_h1.RelaxedFacetConforming`.
    """

    if order < facet_conformity_order:
        raise ValueError(
            "facet_conformity_order must not be greater than order"
        )

    return (
        RelaxedFacetConforming(
            mesh,
            order,
            facet_conformity_order,
            trefftz_formulation,
            dirichlet,
            dgjumps,
            stats=stats,
        )
        if vertex_conforming
        else RelaxedCGConformity(
            mesh,
            order,
            facet_conformity_order,
            stats=stats,
        )
    )


def RelaxedCGConformity(
    mesh: Mesh,
    order: int,
    facet_conformity_order: int,
    trefftz_formulation: TrefftzFormulation | None = None,
    dirichlet: str = "",
    dgjumps: bool = False,
    stats: dict | None = None,
) -> L2EmbTrefftzFESpace:
    r"""
    The RelaxedCGConformity space
    is conforming up to polynomial degree `conformity_order` across facets.

    If there are dofs not occupied by the conformity constraints,
    you can provide a Trefftz operator to make use of them.

    `stats`: use the `stats` flag of the `TrefftzEmbeddin` method

    # Conforming Trefftz Formulation
    - $\mathbb{V}_h := \mathbb{P}^{k, \text{disc}}(\mathcal{T}_h)$
    - $\mathbb{Z}_h := \mathbb{P}^{k_f}(\mathcal{T}_h), k_f \leq k$
    - \begin{align}
      \mathcal{C}_K(v_h, z_h) &:=
          \int_{\partial K} v_h z_h \;dx, \\\\
      \mathcal{D}_K(y_h, z_h) &:=
          \int_{\partial K} y_h z_h \;dx \\\\
      \end{align}
    """
    if (
        facet_conformity_order == order - 1
        and order % 2 == 0
        or facet_conformity_order == order
    ):
        raise NotImplementedError(
            f"The relaxed CG Conformity space is currently not implemented for order {order} with conformity_order {facet_conformity_order}"
        )

    fes = L2(mesh, order=order, dgjumps=dgjumps)

    conformity_space = FacetFESpace(
        mesh, order=facet_conformity_order, dirichlet=dirichlet
    )

    u = fes.TrialFunction()
    uc, vc = conformity_space.TnT()

    cop_l = u * vc * dx(element_vb=BND)
    cop_r = uc * vc * dx(element_vb=BND)

    if trefftz_formulation is not None:
        eps = trefftz_formulation.trefftz_cutoff
        top = trefftz_formulation.trefftz_op(fes)
        trhs = trefftz_formulation.trefftz_rhs(fes)
    else:
        eps = 0.0
        top = None
        trhs = None

    embedding = TrefftzEmbedding(
        top=top,
        trhs=trhs,
        cop=cop_l,
        crhs=cop_r,
        eps=eps,
        stats=stats,
    )

    rcg = EmbeddedTrefftzFES(embedding)
    assert type(rcg) is L2EmbTrefftzFESpace, (
        "The relaxed CG Conformity space should always be an L2EmbTrefftzFESpace"
    )

    return rcg


def RelaxedFacetConforming(
    mesh: Mesh,
    order: int,
    facet_conformity_order: int,
    trefftz_formulation: TrefftzFormulation | None = None,
    dirichlet: str = "",
    dgjumps: bool = False,
    stats: dict | None = None,
) -> L2EmbTrefftzFESpace:
    r"""
    The Relaxed Facet Conforming space
    - is continuous on mesh vertices
    - is conforming up to polynomial degree `conformity_order` across facets

    If there are dofs not occupied by the conformity constraints,
    you can provide a Trefftz operator to make use of them.

    `stats`: use the `stats` flag of the `TrefftzEmbeddin` method

    # Conforming Trefftz Formulation
    - $\mathbb{V}_h := \mathbb{P}^{k, \text{disc}}(\mathcal{T}_h)$
    - $\mathbb{Z}_h := \mathbb{P}^1(\mathcal{T}_h) \times \mathbb{P}^{k_f}_\text{bubble}(\mathcal{T}_h), k_f \leq k$
    - \begin{align}
      \mathcal{C}_K(v_h, (z_h^\text{value}, z_h^\text{facet})) &:= \\\\
          &\sum_{p \text{ is vertex}} v_h(p) z_h^\text{value}(p)
          + \int_{\partial K} v_h z_h^\text{facet} \;dx, \\\\
      \mathcal{D}_K((y_h^\text{value}, y_h^\text{facet}), (z_h^\text{value}, z_h^\text{facet})) &:= \\\\
          &\sum_{p \text{ is vertex}} y_h^\text{value}(p) z_h^\text{value}(p)
          + \int_{\partial K} y_h^\text{value} z_h^\text{facet} \;dx \\\\
      \end{align}
    """
    fes = L2(mesh, order=order, dgjumps=dgjumps)

    conformity_space = H1(
        mesh, order=1, dirichlet=dirichlet
    ) * bubbles.EdgeBubble(mesh, facet_conformity_order, dirichlet=dirichlet)

    u = fes.TrialFunction()
    (uc, uc_e), (vc, vc_e) = conformity_space.TnT()

    cop_l = u * vc * dx(element_vb=BBND)
    cop_r = uc * vc * dx(element_vb=BBND)
    cop_l += u * vc_e * dx(element_vb=BND)
    cop_r += uc_e * vc_e * dx(element_vb=BND)

    if trefftz_formulation is not None:
        eps = trefftz_formulation.trefftz_cutoff
        top = trefftz_formulation.trefftz_op(fes)
        trhs = trefftz_formulation.trefftz_rhs(fes)
    else:
        eps = 0.0
        top = None
        trhs = None

    embedding = TrefftzEmbedding(
        top=top,
        trhs=trhs,
        cop=cop_l,
        crhs=cop_r,
        eps=eps,
        stats=stats,
    )

    rfc = EmbeddedTrefftzFES(embedding)
    assert type(rfc) is L2EmbTrefftzFESpace, (
        "The Relaxed Facet Conforming space should always be an L2EmbTrefftzFESpace"
    )

    return rfc
