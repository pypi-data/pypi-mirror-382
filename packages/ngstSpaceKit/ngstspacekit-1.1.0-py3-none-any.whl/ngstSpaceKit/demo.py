"""
Spaces in `ngstSpaceKit.demo` are already natively implemented in NGSolve.
Their implementation here is purely for educational purposeses.
"""

import ngsolve
from ngsolve import (
    BND,
    L2,
    TET,
    TRIG,
    Discontinuous,
    FacetFESpace,
    HCurl,
    NormalFacetFESpace,
    VectorL2,
    dx,
    specialcf,
)
from ngstrefftz import (
    EmbeddedTrefftzFES,
    L2EmbTrefftzFESpace,
    TrefftzEmbedding,
    VectorL2EmbTrefftzFESpace,
)

import ngstSpaceKit
from ngstSpaceKit.mesh_properties import (
    throw_on_wrong_mesh_dimension,
    throw_on_wrong_mesh_eltype,
)


def CrouzeixRaviart(
    mesh: ngsolve.comp.Mesh,
    dirichlet: str = "",
    check_mesh: bool = True,
    stats: dict | None = None,
) -> L2EmbTrefftzFESpace:
    r"""
    This is an implementation of the Crouzeix-Raviart element via an embedded Trefftz FESpace.
    This implementation is done for illustrative purposes,
    as ngsolve already implements the Crouzeix-Raviart element with:
    ```python
    fes_cr = FESpace('nonconforming', mesh)
    ```

    `check_mesh`: test, if the `mesh` is compatible with this space

    `stats`: use the `stats` flag of the `TrefftzEmbeddin` method

    # Raises
    - ValueError, if the mesh is not 2D
    - ValueError, if the mesh is not triangular

    # Conforming Trefftz Formulation
    - $\mathbb{V}_h := \mathbb{P}^{1, \text{disc}}(\mathcal{T}_h)$
    - $\mathbb{Z}_h := \mathbb{P}^0(\mathcal{F}_h)$
    - \begin{align}
      \mathcal{C}_K(v_h, z_h) := \int_{\partial K} v_h z_h \;dx, \\\\
      \mathcal{D}_K(y_h, z_h) := \int_{\partial K} y_h z_h \;dx
      \end{align}
    """
    if check_mesh:
        throw_on_wrong_mesh_dimension(mesh, 2)
        throw_on_wrong_mesh_eltype(mesh, TRIG)

    fes = L2(mesh, order=1)
    conformity_space = FacetFESpace(mesh, order=0, dirichlet=dirichlet)

    u = fes.TrialFunction()

    uc, vc = conformity_space.TnT()

    cop_l = u * vc * dx(element_vb=BND)
    cop_r = uc * vc * dx(element_vb=BND)

    embedding = TrefftzEmbedding(cop=cop_l, crhs=cop_r, stats=stats)

    cr = EmbeddedTrefftzFES(embedding)
    assert type(cr) is L2EmbTrefftzFESpace, (
        "The cr space should always be an L2EmbTrefftzFESpace"
    )
    return cr


def H1(
    mesh: ngsolve.comp.Mesh,
    order: int,
    dirichlet: str = "",
    stats: dict | None = None,
) -> L2EmbTrefftzFESpace:
    r"""
    This is an implementation for illustrative purposes, ngsolve already implements the H1 space.
    The H1 space is implemented via an embedded Trefftz FESpace.
    Note, that the conformity space is the ngsolve.H1 space,
    which is only used for point evaluations the the mesh vertices.

    `stats`: use the `stats` flag of the `TrefftzEmbeddin` method

    # Conforming Trefftz Formulation
    - $\mathbb{V}_h := \mathbb{P}^{k, \text{disc}}(\mathcal{T}_h)$
    - $\mathbb{Z}_h := \mathbb{P}^k(\mathcal{T}_h)$
    - \begin{align}
      \mathcal{C}_K(v_h, z_h) &:= \int_K v_h z_h \;dx, \\\\
      \mathcal{D}_K(y_h, z_h) &:= \int_K y_h z_h \;dx
      \end{align}
    """
    fes = L2(mesh, order=order)
    cfes = ngsolve.H1(mesh, order=order, dirichlet=dirichlet)

    u, v = fes.TnT()
    uc, vc = cfes.TnT()

    # cop_l = u * vc * dx(element_vb=BBND)
    # cop_r = uc * vc * dx(element_vb=BBND)
    cop_l = u * vc * dx()
    cop_r = uc * vc * dx()

    embedding = TrefftzEmbedding(
        cop=cop_l,
        crhs=cop_r,
        ndof_trefftz=0,
        stats=stats,
    )

    h1 = EmbeddedTrefftzFES(embedding)
    assert type(h1) is L2EmbTrefftzFESpace, (
        "The h1 space should always be an L2EmbTrefftzFESpace"
    )

    return h1


def BDM(
    mesh: ngsolve.comp.Mesh,
    order: int,
    dirichlet: str = "",
    check_mesh: bool = True,
    stats: dict | None = None,
) -> VectorL2EmbTrefftzFESpace:
    r"""
    This BDM space is tailored to mimic the ngsolve implementation of the BDM space:
    ```python
        fes_bdm = HDiv(mesh, order=order, RT=False)
    ```
    Therefore, this implementation has no practical advantage over the ngsolve implementation,
    and merely serves as a demonstration.

    See `ngstSpaceKit.HDiv` for an H(div) conforming space, that is not implemented by ngsolve.

    `check_mesh`: test, if the `mesh` is compatible with this space

    `stats`: use the `stats` flag of the `TrefftzEmbeddin` method

    # Raises
    - ValueError, if `order == 0`
    - ValueError, if the mesh is not 2D or 3D
    - ValueError, if the mesh is not triangular (2D) or consists of tetrahedra (3D)

    # Conforming Trefftz Formulation
    - $\mathbb{V}_h := [\mathbb{P}^{k, \text{disc}}(\mathcal{T}_h)]^d$
    - $\mathbb{Z}_h := [\mathbb{P}^k(\mathcal{F}_h)]^d \times \mathcal{N}_1^{k-1}(\mathcal{T}_h)$
    - \begin{align}
      \mathcal{C}_K(v_h, (z_h^\text{facet}, z_h^\text{vol})) &:=
          \int_{\partial K} v_h \cdot n \; z_h^\text{facet} \cdot n \;dx + \int_K v_h z_h^\text{vol} \;dx, \\\\
      \mathcal{D}_K((y_h^\text{facet}, y_h^\text{vol}), (z_h^\text{facet}, z_h^\text{vol})) &:=
          \int_{\partial K} y_h^\text{facet} \cdot n \; z_h^\text{facet} \cdot n \;dx + \int_K y_h^\text{vol} z_h^\text{vol} \;dx
      \end{align}
    """

    if check_mesh:
        throw_on_wrong_mesh_dimension(mesh, [2, 3])
        throw_on_wrong_mesh_eltype(mesh, [TRIG, TET])

    if order == 0:
        raise ValueError("BDM needs order >= 1")
    if order == 1:
        return ngstSpaceKit.HDiv(mesh, order=1)

    fes = VectorL2(mesh, order=order)

    conformity_space = NormalFacetFESpace(
        mesh, order=order, dirichlet=dirichlet
    ) * Discontinuous(
        HCurl(mesh, order=order - 1, type1=True, dirichlet=dirichlet)
    )

    u = fes.TrialFunction()

    (uc_edge, uc_vol), (vc_edge, vc_vol) = conformity_space.TnT()

    n = specialcf.normal(mesh.dim)

    cop_l = u * n * vc_edge * n * dx(element_vb=BND)
    cop_r = uc_edge * n * vc_edge * n * dx(element_vb=BND)

    cop_l += u * vc_vol * dx
    cop_r += uc_vol * vc_vol * dx

    embedding = TrefftzEmbedding(cop=cop_l, crhs=cop_r, stats=stats)

    bdm = EmbeddedTrefftzFES(embedding)
    assert type(bdm) is VectorL2EmbTrefftzFESpace, (
        "The bdm space should always be a VectorL2EmbTrefftzFESpace"
    )

    return bdm
