from typing import Optional

from ngsolve import (
    BND,
    COUPLING_TYPE,
    L2,
    TRIG,
    CoefficientFunction,
    InnerProduct,
    Mesh,
    NormalFacetFESpace,
    VectorL2,
    div,
    dx,
    grad,
    specialcf,
)
from ngstrefftz import (
    CompoundEmbTrefftzFESpace,
    EmbeddedTrefftzFES,
    TrefftzEmbedding,
)

from ngstSpaceKit.diffops import laplace
from ngstSpaceKit.mesh_properties import (
    throw_on_wrong_mesh_dimension,
    throw_on_wrong_mesh_eltype,
)


def WeakStokes(
    mesh: Mesh,
    order: int,
    normal_continuity: Optional[int] = -1,
    rhs: Optional[CoefficientFunction] = None,
    nu: float = 1.0,
    dirichlet: str = "",
    use_stokes_top: bool = True,
    trefftz_test_order_drop: int = 2,
    check_mesh: bool = True,
    stats: dict | None = None,
) -> CompoundEmbTrefftzFESpace:
    r"""
    The weak Stokes space
    - is tailored to be used to solve the Stokes equation
    - is normal continuous up to degree `normal_continuity` in the velocity part
    - has the remaining dofs adhering to the embedded Trefftz condition

    `normal_continuity`: If `-1`, it is set to `order-1`. If `None`, no normal continuity will be enforced.

    `use_stokes_top`: Whether to use the Stokes strong form operator as the Trefftz condition, or not.

    `trefftz_test_order_drop`: specifies the number $X_t$ by which the Trefftz (velocity) test space order is smaller that the trial space order.
        Should not be smaller than 2.

    `check_mesh`: test, if the `mesh` is compatible with this space

    `stats`: use the `stats` flag of the `TrefftzEmbeddin` method

    # Conforming Trefftz Formulation
    - $\mathbb{V}_h := [\mathbb{P}^{k, \text{disc}}(\mathcal{T}_h)]^d \times \mathbb{P}^{k-1, \text{disc}}(\mathcal{T}_h)$
    - $\mathbb{Q}_h := [\mathbb{P}^{k-X_t, \text{disc}}(\mathcal{T}_h)]^d \times \mathbb{P}^{k+1-X_t, \text{disc}}_0(\mathcal{T}_h)$
    - $\mathbb{Z}_h := [\mathbb{P}^{k_n}(\mathcal{F}_h)]^d, k_n \leq k$
    - \begin{align}
      \mathcal{C}_K(v_h, z_h) &:=
          \int_{\partial K} v_h^v \cdot n \; z_h \cdot n \;dx \\\\
      \mathcal{D}_K(y_h, z_h) &:=
          \int_{\partial K} y_h^v \cdot n \; z_h \cdot n \;dx
      \end{align}
    - \begin{align}
      (\mathcal{L}_K v_h, q_h) :=
        -\nu \int_\Omega \Delta v_h^v \cdot q_h^v \;dx + \int_\Omega \nabla v_h^p \cdot q_h^v + \mathrm{div}(v_h^v) q_h^p \;dx
      \end{align}
    """
    if order < trefftz_test_order_drop:
        raise ValueError(f"requires order>={trefftz_test_order_drop}")

    if check_mesh:
        throw_on_wrong_mesh_dimension(mesh, 2)
        throw_on_wrong_mesh_eltype(mesh, TRIG)

    fes = VectorL2(mesh, order=order, dgjumps=True) * L2(
        mesh, order=order - 1, dgjumps=True
    )

    Q_test = L2(mesh, order=order - trefftz_test_order_drop + 1, dgjumps=True)
    for i in range(0, Q_test.ndof, Q_test.ndof // mesh.ne):
        Q_test.SetCouplingType(i, COUPLING_TYPE.UNUSED_DOF)

    fes_test = (
        VectorL2(mesh, order=order - trefftz_test_order_drop, dgjumps=True)
        * Q_test
    )

    (u, p) = fes.TrialFunction()
    (v, q) = fes_test.TestFunction()

    top = None
    trhs = None
    if use_stokes_top:
        top = (
            -nu * InnerProduct(laplace(u), v) * dx
            + InnerProduct(grad(p), v) * dx
            + div(u) * q * dx
        )
        trhs = rhs * v * dx(bonus_intorder=10) if rhs else None

    cop_l = None
    cop_r = None

    if normal_continuity is not None:
        conformity_space = NormalFacetFESpace(
            mesh,
            order=normal_continuity if normal_continuity >= 0 else order - 1,
            dirichlet=dirichlet,
        )

        uc, vc = conformity_space.TnT()

        n = specialcf.normal(mesh.dim)

        cop_l = u * n * vc * n * dx(element_vb=BND)
        cop_r = uc * n * vc * n * dx(element_vb=BND)

    emb = TrefftzEmbedding(
        top=top,
        trhs=trhs,
        cop=cop_l,
        crhs=cop_r,
        stats=stats,
    )
    weak_stokes = EmbeddedTrefftzFES(emb)
    assert type(weak_stokes) is CompoundEmbTrefftzFESpace, (
        "The weak Stokes space should always be an CompoundEmbTrefftzFESpace"
    )

    return weak_stokes
