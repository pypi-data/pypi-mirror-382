import enum
from enum import Enum

import ngsolve
from ngsolve import (
    BBND,
    CF,
    H1,
    L2,
    QUAD,
    TRIG,
    BilinearForm,
    Discontinuous,
    IfPos,
    LinearForm,
    Normalize,
    dx,
    specialcf,
)
from ngsolve.solve_implementation import GridFunction
from ngstrefftz import (
    CompoundEmbTrefftzFESpace,
    EmbeddedTrefftzFES,
    TrefftzEmbedding,
)
from xfem import (
    IF,
    NEG,
    POS,
    CutInfo,
    dCut,
)

from ngstSpaceKit.diffops import grad, hesse
from ngstSpaceKit.mesh_properties import (
    throw_on_wrong_mesh_dimension,
    throw_on_wrong_mesh_eltype,
)


def ImmersedP1FE(
    mesh: ngsolve.comp.Mesh,
    lsetp1: ngsolve.CoefficientFunction,
    beta_neg: float,
    beta_pos: float,
    dirichlet: str = "",
    dgjumps: bool = False,
    check_mesh: bool = True,
    stats: dict | None = None,
) -> CompoundEmbTrefftzFESpace:
    r"""
    `check_mesh`: test, if the `mesh` is compatible with this space

    `stats`: use the `stats` flag of the `TrefftzEmbeddin` method

    This Immersed P1 space is tailored towards solving the following interface problem.

    Let $\Omega$ be a domain, which is decomposed by a cut $\Gamma$ into $\Omega = \Omega^- \cup \Gamma \cup \Omega^+$.
    Let $\beta$ be a piecewise constant coefficient
    \begin{align}
    \beta(x) &:=
        \begin{cases}
            \beta^-, &\text{if } x \in \Omega^- \\\\
            \beta^+, &\text{if } x \in \Omega^+ \\\\
        \end{cases}, \\\\
    \beta^-, \beta^+ &> 0.
    \end{align}

    Then, find $u$, s.t.

    \begin{align}
        -\operatorname{div} (\beta \nabla u) &= f \text{ in } \Omega^- \cup \Omega^+, \\\\
                                        〚u〛 &= 0 \text{ on } \Gamma, \\\\
	        〚\beta \nabla u \cdot n_\Gamma〛 &= 0 \text{ on } \Gamma, \\\\
	                                       u &= 0 \text{ on } \partial \Gamma. \\\\
    \end{align}

    In particular, the functions in this space fulfil the property
    \begin{align}
                                〚u〛 &= 0 \text{ on } \Gamma, \\\\
	〚\beta \nabla u \cdot n_\Gamma〛 &= 0 \text{ on } \Gamma, \\\\
    \end{align}
    as well as being continuous at mesh vertices.
    The space consists of piecewise linear functions.

    Actually, the returned space consists of vectorial functions of order $1$,
    that have to be interpreted in the following way: the first component represents the
    piecewise linear function in $\Omega^-$, the second component in $\Omega^+$.
    Formally, for $v = \begin{pmatrix} v^- \\\\ v^+ \end{pmatrix}$ we define the piecewise linear function
    \begin{align}
        \hat{v}(x) &:=
            \begin{cases}
                v^-(x), &\text{if } x \in \Omega^- \\\\
                v^+(x), &\text{if } x \in \Omega^+ \\\\
            \end{cases}.
    \end{align}

    `lsetp1`: The levelset function $p$ used to describe the cut as $\Gamma := \\{x \in \Omega \mid p(x) = 0 \\}$,
        as well as $\Omega^- := \\{x \in \Omega \mid p(x) < 0 \\}$ and $\Omega^- := \\{x \in \Omega \mid p(x) > 0 \\}$.
        $p$ needs to be affine linear on each element. E.g. set `lsetp1` as a `Gridfunction(H1(mesh, order=1))`.

    `beta_neg`: diffusion coefficient for $\Omega^-$. Should be a positive number.

    `beta_pos`: diffusion coefficient for $\Omega^+$. Should be a positive number.

    # Conforming Trefftz Formulation
    - $\mathbb{V}_h := [\mathbb{P}^{1, \text{disc}}(\mathcal{T}_h)]^2$
    - $\mathbb{Q}_h := \mathbb{V}_h$
    - $\mathbb{Z}_h := \mathbb{P}^{1}(\mathcal{T}_h)$
    - \begin{align}
      \mathcal{C}_K(v_h, z_h) &:=
          \sum_{p \text{ is vertex}} \hat{v}_h(p) z_h(p) \\\\
      \mathcal{D}_K(y_h, z_h) &:=
          \sum_{p \text{ is vertex}} y_h(p) z_h(p) \\\\
      \end{align}
    - \begin{align}
      (\mathcal{L}_K v_h, q_h) :=
        \int_\Gamma 〚\hat{v}_h〛 〚\hat{q}_h〛 \;dS + \int_\Gamma〚\beta \nabla \hat{v}_h \cdot n_\Gamma〛 〚\beta \nabla \hat{q}_h \cdot n_\Gamma〛\;dS
      \end{align}
    """

    if check_mesh:
        throw_on_wrong_mesh_dimension(mesh, 2)
        throw_on_wrong_mesh_eltype(mesh, TRIG)

    ci = CutInfo(mesh, lsetp1)
    dS = dCut(lsetp1, IF, definedonelements=ci.GetElementsOfType(IF), order=2)
    n = Normalize(grad(lsetp1, mesh.dim))
    h = specialcf.mesh_size

    fes = L2(mesh, order=1, dgjumps=dgjumps) * L2(
        mesh, order=1, dgjumps=dgjumps
    )
    conformity_space = H1(mesh, order=1, dirichlet=dirichlet)

    (u_neg, u_pos), (v_neg, v_pos) = fes.TnT()

    top = u_neg * v_neg * dx(definedonelements=ci.GetElementsOfType(POS))
    top += u_pos * v_pos * dx(definedonelements=ci.GetElementsOfType(NEG))
    top += 1 / h * (u_pos - u_neg) * (v_pos - v_neg) * dS
    top += (
        h
        * ((beta_pos * grad(u_pos) - beta_neg * grad(u_neg)) * n)
        * ((beta_pos * grad(v_pos) - beta_neg * grad(v_neg)) * n)
        * dS
    )

    uc, vc = conformity_space.TnT()

    cop = IfPos(lsetp1, u_pos, u_neg) * vc * dx(element_vb=BBND)

    crhs = uc * vc * dx(element_vb=BBND)

    emb = TrefftzEmbedding(
        top=top,
        trhs=None,
        cop=cop,
        crhs=crhs,
        ndof_trefftz=0,
        stats=stats,
    )
    imp1fe = EmbeddedTrefftzFES(emb)
    assert type(imp1fe) is CompoundEmbTrefftzFESpace, (
        "The ImmersedP1FESpace space should always be a CompoundEmbTrefftzFESpace"
    )

    return imp1fe


class ImmersedQ1Impl(Enum):
    """
    Represents a Conforming Trefftz implementation
    for the `ImmersedQ1FE` space.
    """

    Canonical = enum.auto()
    """
    Formulation is described by <https://doi.org/10.1002/num.20318>.
    """

    NonConforming = enum.auto()
    """
    Stable formulation, that is not continuous acrosss the cut interface.
    """

    Overloaded = enum.auto()
    """
    Technically overconstrains the Trefftz condition,
    but it may still work.
    """


def ImmersedQ1FE(
    mesh: ngsolve.comp.Mesh,
    lsetq1: ngsolve.GridFunction,
    beta_neg: float,
    beta_pos: float,
    dirichlet: str = "",
    dgjumps: bool = False,
    stats: dict | None = None,
    impl: ImmersedQ1Impl = ImmersedQ1Impl.NonConforming,
) -> CompoundEmbTrefftzFESpace:
    r"""
    This is the version of `ImmersedP1FE` for quadrilateral meshes.
    Refer to the documentation of `ImmersedP1FE` for most details.

    `lsetq1`: The levelset function, as a `GridFunction` over the `H1` space with `order=1`.
        In geleral, the cut may not be piecewise linear, as the `H1` space of `order=1` contains bilinear functions on quads.
        You can use `straighten_levelset` inorder to produce a levelset function
        with a piecewise linear cut.

    `impl`: declare what Trefftz implementation you want to use

    # Canonical Conforming Trefftz Formulation
    This implements the formulation of <https://doi.org/10.1002/num.20318>.
    - $\mathbb{V}_h := [\mathbb{Q}^{1, \text{disc}}(\mathcal{T}_h)]^2$
    - $\mathbb{Q}_h := \mathbb{Q}^{1, \text{disc}}(\mathcal{T}_h) \times \mathbb{Q}^{0, \text{disc}}(\mathcal{T}_h)$
    - $\mathbb{Z}_h := \mathbb{Q}^{1}(\mathcal{T}_h)$
    - \begin{align}
      \mathcal{C}_K(v_h, z_h) &:=
          \sum_{p \text{ is vertex}} \hat{v}_h(p) z_h(p) \\\\
      \mathcal{D}_K(y_h, z_h) &:=
          \sum_{p \text{ is vertex}} y_h(p) z_h(p) \\\\
      \end{align}
    - \begin{align}
      (\mathcal{L}_K (v_h, (q_{h, 1}, q_{h, 0})) :=
        \int_\Gamma 〚\hat{v}_h〛q_{h,1} \;dS + \int_\Gamma〚\beta \nabla \hat{v}_h \cdot n_\Gamma〛 q_{h,0} \;dS
      \end{align}

    # Non-Conforming Conforming Trefftz Formulation
    - $\mathbb{V}_h := [\mathbb{Q}^{1, \text{disc}}(\mathcal{T}_h)]^2$
    - $\mathbb{Q}_h := [\mathbb{Q}^{0, \text{disc}}(\mathcal{T}_h)]^4$
    - $\mathbb{Z}_h := \mathbb{Q}^{1}(\mathcal{T}_h)$
    - \begin{align}
    \mathcal{C}_K(v_h, z_h) &:=
        \sum_{p \text{ is vertex}} \hat{v}_h(p) z_h(p) \\\\
    \mathcal{D}_K(y_h, z_h) &:=
        \sum_{p \text{ is vertex}} y_h(p) z_h(p) \\\\
    \end{align}
    - \begin{align}
    (\mathcal{L}_K v_h, (q_h, q_\tau, q_n, q_{\tau n})) &:=
        \int_\Gamma \frac{1}{h}〚\hat{v}_h〛 q_h \;dS + \int_\Gamma〚\nabla \hat{v}_h \cdot \tau_\Gamma〛 q_\tau \;dS \\\\
        &+ \int_\Gamma〚\beta \nabla \hat{v}_h \cdot n_\Gamma〛 q_n \;dS + \int_\Gamma h〚\beta n_\Gamma^T \mathbf{H}_{\hat{v}_h} \tau_\Gamma〛 q_{\tau n} \;dS
    \end{align}

    # Overloaded Conforming Trefftz Formulation
    - $\mathbb{V}_h := [\mathbb{Q}^{1, \text{disc}}(\mathcal{T}_h)]^2$
    - $\mathbb{Q}_h := \mathbb{V}_h$
    - $\mathbb{Z}_h := \mathbb{Q}^{1}(\mathcal{T}_h)$
    - \begin{align}
    \mathcal{C}_K(v_h, z_h) &:=
        \sum_{p \text{ is vertex}} \hat{v}_h(p) z_h(p) \\\\
    \mathcal{D}_K(y_h, z_h) &:=
        \sum_{p \text{ is vertex}} y_h(p) z_h(p) \\\\
    \end{align}
    - \begin{align}
    (\mathcal{L}_K v_h, q_h) :=
        \int_\Gamma 〚\hat{v}_h〛 〚\hat{q}_h〛 \;dS + \int_\Gamma〚\beta \nabla \hat{v}_h \cdot n_\Gamma〛 〚\beta \nabla \hat{q}_h \cdot n_\Gamma〛\;dS
    \end{align}
    """

    throw_on_wrong_mesh_dimension(mesh, 2)
    throw_on_wrong_mesh_eltype(mesh, QUAD)

    if not (
        (
            isinstance(lsetq1.space, H1)
            or isinstance(lsetq1.space, Discontinuous)
        )
        and lsetq1.space.globalorder == 1
    ):
        raise ValueError(
            f"lsetq1 must be a GridFunction on an H1(order=1) or Discontinuous(H1(order=1)) space. You got: {lsetq1.space}"
        )

    ci = CutInfo(mesh, lsetq1)
    dS = dCut(lsetq1, IF, definedonelements=ci.GetElementsOfType(IF), order=4)
    n = Normalize(grad(lsetq1, mesh.dim))
    h = specialcf.mesh_size

    fes = L2(mesh, order=1, dgjumps=dgjumps) * L2(
        mesh, order=1, dgjumps=dgjumps
    )

    conformity_space = H1(mesh, order=1, dirichlet=dirichlet)

    match impl:
        case ImmersedQ1Impl.Overloaded:
            (u_neg, u_pos), (v_neg, v_pos) = fes.TnT()

            top = (
                u_neg * v_neg * dx(definedonelements=ci.GetElementsOfType(POS))
            )
            top += (
                u_pos * v_pos * dx(definedonelements=ci.GetElementsOfType(NEG))
            )
            top += 1 * (u_pos - u_neg) * (v_pos - v_neg) * dS
            top += (
                h
                * ((beta_pos * grad(u_pos) - beta_neg * grad(u_neg)) * n)
                * ((beta_pos * grad(v_pos) - beta_neg * grad(v_neg)) * n)
                * dS
            )
        case ImmersedQ1Impl.Canonical:  # old
            fes_test = L2(mesh, order=1) * L2(mesh, order=0)

            (u_neg, u_pos) = fes.TrialFunction()
            v_bilin, v_const = fes_test.TestFunction()

            top = (
                u_neg
                * v_bilin
                * dx(definedonelements=ci.GetElementsOfType(POS))
            )
            top += (
                u_pos
                * v_bilin
                * dx(definedonelements=ci.GetElementsOfType(NEG))
            )
            top += 1 / h**2 * (u_pos - u_neg) * v_bilin * dS
            top += (
                h
                * ((beta_pos * grad(u_pos) - beta_neg * grad(u_neg)) * n)
                * v_const
                * dS
            )
        case ImmersedQ1Impl.NonConforming:  # new version
            fes_test = (
                L2(mesh, order=1)
                * L2(mesh, order=0)
                * L2(mesh, order=0)
                * L2(mesh, order=0)
                * L2(mesh, order=0)
            )

            (u_neg, u_pos) = fes.TrialFunction()
            v_bilin, v1, v2, v3, v4 = fes_test.TestFunction()

            top = (
                u_neg
                * v_bilin
                * dx(definedonelements=ci.GetElementsOfType(POS))
            )
            top += (
                u_pos
                * v_bilin
                * dx(definedonelements=ci.GetElementsOfType(NEG))
            )
            t = CF((n[1], -n[0]))
            top += 1 / h * (u_pos - u_neg) * v1 * dS
            top += (grad(u_pos) - grad(u_neg) | t) * v2 * dS
            top += (
                (beta_pos * grad(u_pos) - beta_neg * grad(u_neg) | n) * v3 * dS
            )
            top += (
                h
                * (
                    beta_pos * (hesse(u_pos) * t | n)
                    - beta_neg * (hesse(u_neg) * t | n)
                )
                * v4
                * dS
            )

    uc, vc = conformity_space.TnT()

    cop = IfPos(lsetq1, u_pos, u_neg) * vc * dx(element_vb=BBND)
    crhs = uc * vc * dx(element_vb=BBND)

    emb = TrefftzEmbedding(
        top=top,
        trhs=None,
        cop=cop,
        crhs=crhs,
        ndof_trefftz=0,
        stats=stats,
    )
    imq1fe = EmbeddedTrefftzFES(emb)
    assert type(imq1fe) is CompoundEmbTrefftzFESpace, (
        "The ImmersedQ1FESpace space should always be a CompoundEmbTrefftzFESpace"
    )

    return imq1fe


def straighten_levelset(lsetq1: GridFunction) -> GridFunction:
    """
    Produces a new levelset function with an element-wise
    straight cut.

    This is interesting for straightening of levelset functions
    on quad meshes.
    """
    eps = 1e-9
    fes = L2(lsetq1.space.mesh, order=1)
    u, v = fes.TnT()
    op = (hesse(u) | hesse(v)) * dx + u * v * dCut(
        lsetq1, IF, element_boundary=True
    )
    emb = TrefftzEmbedding(op, eps=eps)

    etfes = EmbeddedTrefftzFES(emb)
    u, v = etfes.TnT()
    a = BilinearForm(u * v * dx).Assemble()
    f = LinearForm(lsetq1 * v * dx).Assemble()
    inv = a.mat.Inverse(inverse="sparsecholesky")
    lsetp1_straight_trefftz = GridFunction(etfes)
    lsetp1_straight_trefftz.vec.data = inv * f.vec

    lsetp1_straight = GridFunction(fes)
    lsetp1_straight.vec.data = emb.Embed(lsetp1_straight_trefftz.vec)

    lsetp1_straight_final = GridFunction(
        Discontinuous(H1(lsetq1.space.mesh, order=1))
    )
    lsetp1_straight_final.Set(lsetp1_straight)
    return lsetp1_straight_final
