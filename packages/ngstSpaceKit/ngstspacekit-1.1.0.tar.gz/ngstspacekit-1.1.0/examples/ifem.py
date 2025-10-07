# %% jupyter={"source_hidden": true}, tags=["hide-input"]
import matplotlib.pyplot as plt
import numpy as np
from netgen.occ import Face, Glue, OCCGeometry, WorkPlane, X, Y
from ngsolve import (
    BND,
    CF,
    H1,
    L2,
    BilinearForm,
    GridFunction,
    IfPos,
    Integrate,
    LinearForm,
    Mesh,
    dx,
    grad,
    specialcf,
    sqrt,
    unit_square,
    x,
    y,
)
from ngsolve.meshes import MakeStructured2DMesh
from ngsolve.webgui import Draw
from ngstrefftz import CompoundEmbTrefftzFESpace
from pyngcore import TaskManager
from xfem import (
    IF,
    NEG,
    POS,
    CoefficientFunction,
    CutInfo,
    DrawDC,
    GetFacetsWithNeighborTypes,
    InterpolateToP1,
    dCut,
)

from ngstSpaceKit.immersedfe import (
    ImmersedP1FE,
    ImmersedQ1FE,
    ImmersedQ1Impl,
    straighten_levelset,
)

plt.rcParams["font.family"] = "cmr10"
plt.rcParams["mathtext.fontset"] = "cm"
plt.rcParams["axes.formatter.use_mathtext"] = True

# %% [markdown]
# # Immersed Finite Element Method (IFEM)
#
# We consider the following problem:
# Let $\Omega$ be a domain, which is decomposed by a cut $\Gamma$ into $\Omega = \Omega^- \cup \Gamma \cup \Omega^+$.
# Let $\beta$ be a piecewise constant coefficient
# \begin{align}
# \beta(x) &:=
#     \begin{cases}
#         \beta^-, &\text{if } x \in \Omega^- \\\\
#         \beta^+, &\text{if } x \in \Omega^+ \\\\
#     \end{cases}, \\\\
# \beta^-, \beta^+ &> 0.
# \end{align}
#
# Then, find $u$, s.t.
#
# \begin{align}
#     -\operatorname{div} (\beta \nabla u) &= f \text{ in } \Omega^- \cup \Omega^+, \\\\
#                                     〚u〛 &= 0 \text{ on } \Gamma, \\\\
# 	        〚\beta \nabla u \cdot n_\Gamma〛 &= 0 \text{ on } \Gamma, \\\\
# 	                                       u &= 0 \text{ on } \partial \Gamma. \\\\
# \end{align}
#
#
# ## Triangular mesh
# Let's consider the following cut $\Gamma = \{x + \frac{y}{2} - \frac{3}{4} = 0\}$
# on a triangular mesh

# %%
beta_neg = 1.0
beta_pos = 10.0

small_mesh = Mesh(unit_square.GenerateMesh(maxh=0.5))

lset = x + y / 2 - 3 / 4
lset_gfu = GridFunction(H1(small_mesh, order=1))
InterpolateToP1(lset, lset_gfu)
DrawDC(lset, 1.0, -1.0, small_mesh)


# %% [markdown]
# To solve the problem, we construct a space s.t.
# the functions in this space fulfil the property
# \begin{align}
#                             〚u〛 &= 0 \text{ on } \Gamma, \\\\
# 	〚\beta \nabla u \cdot n_\Gamma〛 &= 0 \text{ on } \Gamma, \\\\
# \end{align}
# as well as being continuous at mesh vertices.
# The space consists of piecewise linear functions.

# %%
ifes_trigs = ImmersedP1FE(
    small_mesh,
    lset_gfu,
    beta_neg,
    beta_pos,
)
gfu = GridFunction(ifes_trigs)
gfu.vec.data[4] = 1.0
gfu_emb = ifes_trigs.emb.Embed(gfu)
DrawDC(
    lset,
    gfu_emb.components[0],
    gfu_emb.components[1],
    small_mesh,
    order=50,
    deformation=CF(
        (x, y, IfPos(lset_gfu, gfu_emb.components[1], gfu_emb.components[0]))
    ),
    euler_angles=[-40, 2, 20],
)

# %% [markdown]
# We consider the following manufactured solution $(u, f, \Gamma)$


# %%
def big_square() -> OCCGeometry:
    r"""
    builds this geometry:

    +--+
    |  |
    |  |
    +--+

    With corners beig (-1, -1), (1, -1), (1, 1), (-1, 1)
    """
    wp = WorkPlane()
    wp.MoveTo(-1.0, -1.0)

    for _ in range(4):
        wp.Line(2.0).Rotate(90)
    square = wp.Face()

    square.name = "square"
    square.edges.Min(X).name = "left"
    square.edges.Max(X).name = "right"
    square.edges.Min(Y).name = "bottom"
    square.edges.Max(Y).name = "top"
    return OCCGeometry(square, dim=2)


def manufactured_solution(
    beta_neg: float, beta_pos: float
) -> tuple[
    tuple[CoefficientFunction, CoefficientFunction],
    tuple[CoefficientFunction, CoefficientFunction],
    CoefficientFunction,
]:
    """
    returns: `((u_neg, u_pos), (f_neg, f_pos), fn)`
    """
    alpha = 5
    r = sqrt(x**2 + y**2)

    fn = r - 1 / 2

    u_pos = (r**alpha) / beta_pos + 0.5**alpha * (
        1.0 / beta_neg - 1.0 / beta_pos
    )
    u_neg = (r**alpha) / beta_neg

    lap_u_neg = 25 * r**3 / beta_neg
    lap_u_pos = 25 * r**3 / beta_pos

    f_neg = -beta_neg * lap_u_neg
    f_pos = -beta_pos * lap_u_pos

    return (u_neg, u_pos), (f_neg, f_pos), fn


big_mesh = Mesh(big_square().GenerateMesh(maxh=0.2))
(u_neg, u_pos), (f_neg, f_pos), lset = manufactured_solution(beta_neg, beta_pos)
lset_gfu = GridFunction(H1(big_mesh, order=1))
InterpolateToP1(lset, lset_gfu)

DrawDC(
    lset_gfu,
    -1.0,
    1.0,
    big_mesh,
)

# %%
DrawDC(
    lset_gfu,
    u_neg,
    u_pos,
    big_mesh,
    order=50,
    deformation=CF((x, y, 5 * IfPos(lset_gfu, u_pos, u_neg))),
    euler_angles=[-40, 2, 20],
)

# %%
DrawDC(
    lset_gfu,
    f_neg,
    f_pos,
    big_mesh,
    order=50,
    deformation=CF((x, y, 0.025 * IfPos(lset_gfu, f_pos, f_neg))),
    euler_angles=[-40, 2, 20],
)


# %% [markdown]
# Then, we can study how well the IFEM solution error scales with $h$.
#
# We compare three methods:#
# - a classical CG method
# - an IFEM method without any penalty
# - an IFEM method with SIP


# %% jupyter={"source_hidden": true}, tags=["hide-input"]
def l2_err_ifem(
    gfu_base: GridFunction,
    u_exact: CoefficientFunction,
    fn: GridFunction,
    mesh: Mesh,
) -> float:
    return sqrt(
        Integrate(
            (gfu_base.components[1] - u_exact) ** 2 * dCut(fn, POS, order=10),
            mesh,
        )
        + Integrate(
            (gfu_base.components[0] - u_exact) ** 2 * dCut(fn, NEG, order=10),
            mesh,
        )
    )


def l2_err_cg(
    gfu: GridFunction,
    u_exact: CoefficientFunction,
    mesh: Mesh,
) -> float:
    return sqrt(Integrate((gfu - u_exact) ** 2, mesh, order=10))


# %%
def solve_poisson_cg(
    mesh: Mesh,
    rhs: CoefficientFunction,
    beta: CoefficientFunction,
    order=1,
    u_bnd: CoefficientFunction = CF(0),
) -> GridFunction:
    fes = H1(mesh, order=order, dirichlet="left|right|bottom|top")
    u, v = fes.TnT()
    a = BilinearForm(fes)
    a += beta * grad(u) * grad(v) * dx
    a.Assemble()

    f = LinearForm(fes)
    f += rhs * v * dx
    f.Assemble()

    gfu = GridFunction(fes)
    gfu.Set(u_bnd, BND)
    f.vec.data -= a.mat * gfu.vec

    gfu.vec.data += (
        a.mat.Inverse(fes.FreeDofs(), inverse="sparsecholesky") * f.vec
    )
    return gfu


def mean(f: CoefficientFunction) -> CoefficientFunction:
    return (f + f.Other()) / 2


def jump(f: CoefficientFunction) -> CoefficientFunction:
    return f - f.Other()


def solve_poisson_ifem(
    mesh: Mesh,
    rhs: tuple[CoefficientFunction, CoefficientFunction],
    fn: GridFunction,
    beta_neg: float,
    beta_pos: float,
    u_bnd: CoefficientFunction = CF(0),
    do_penalty: bool = False,
    epsilon: float = -1,
    quads: ImmersedQ1Impl | None = None,
) -> GridFunction:
    """
    `fn`: need to be a GridFunction to a `H1(mesh, order=1)` space.

    `rhs`: `(rhs_neg, rhs_pos)`
    """
    sigma = 10 * max(beta_neg, beta_pos)
    fes = (
        ImmersedP1FE(
            mesh,
            fn,
            beta_neg,
            beta_pos,
            dirichlet="left|right|bottom|top",
            dgjumps=do_penalty,
        )
        if quads is None
        else ImmersedQ1FE(
            mesh,
            fn,
            beta_neg,
            beta_pos,
            dirichlet=".*",
            dgjumps=do_penalty,
            impl=quads,
        )
    )
    (u_neg, u_pos), (v_neg, v_pos) = fes.TnT()
    mean_grad_u = 0.5 * IfPos(fn, grad(u_pos), grad(u_neg)) + 0.5 * IfPos(
        fn, grad(u_pos).Other(), grad(u_neg).Other()
    )
    mean_grad_v = 0.5 * IfPos(fn, grad(v_pos), grad(v_neg)) + 0.5 * IfPos(
        fn, grad(v_pos).Other(), grad(v_neg).Other()
    )
    jump_u = IfPos(fn, u_pos - u_pos.Other(), u_neg - u_neg.Other())
    jump_v = IfPos(fn, v_pos - v_pos.Other(), v_neg - v_neg.Other())

    dx_neg = dCut(fn, NEG, order=4)
    dx_pos = dCut(fn, POS, order=4)

    a = BilinearForm(fes)
    a += beta_neg * grad(u_neg) * grad(v_neg) * dx_neg
    a += beta_pos * grad(u_pos) * grad(v_pos) * dx_pos

    if do_penalty:
        ci = CutInfo(mesh, fn)
        n = specialcf.normal(2)
        h = specialcf.mesh_size

        cut_elements = ci.GetElementsOfType(IF)
        cut_facets = GetFacetsWithNeighborTypes(
            mesh,
            a=cut_elements,
            b=cut_elements,
            bnd_val_a=False,
            bnd_val_b=False,
            use_and=True,
        )
        # F^int
        for beta, cut in [(beta_neg, NEG), (beta_pos, POS)]:
            a += (
                -beta
                * mean_grad_u
                * n
                * jump_v
                * dCut(
                    fn,
                    cut,
                    skeleton=True,
                    definedonelements=cut_facets,
                    order=4,
                )
            )
            a += (
                epsilon
                * beta
                * mean_grad_v
                * n
                * jump_u
                * dCut(
                    fn,
                    cut,
                    skeleton=True,
                    definedonelements=cut_facets,
                    order=4,
                )
            )
            alpha = 1
            a += (
                sigma
                / (h**alpha)
                * jump_u
                * jump_v
                * dCut(
                    fn,
                    cut,
                    skeleton=True,
                    definedonelements=cut_facets,
                    order=4,
                )
            )

    a.Assemble()
    # print(f"a.mat: {a.mat}")

    f = LinearForm(fes)
    f += rhs[0] * v_neg * dx_neg
    f += rhs[1] * v_pos * dx_pos
    f.Assemble()

    # gfu doesn't have the appopriate evaluators to be able to use Set directly.
    # Instead, we set the boundary values to the conformity gfu,
    # and copy the vector entries to the beginning of the gfu vector.
    # The first dofs in the conforming Trefftz space are the conformity dofs.
    gfu = GridFunction(fes)
    gfu_conf = GridFunction(fes.emb.fes_conformity)
    gfu_conf.Set(u_bnd, BND)
    gfu.vec.data[: len(gfu_conf.vec)] = gfu_conf.vec
    f.vec.data -= a.mat * gfu.vec

    gfu.vec.data += (
        a.mat.Inverse(fes.FreeDofs(), inverse="sparsecholesky") * f.vec
    )
    return gfu


# %% jupyter={"source_hidden": true}, tags=["hide-input"]
(u_neg, u_pos), (f_neg, f_pos), fn = manufactured_solution(beta_neg, beta_pos)
u_ex: CoefficientFunction = IfPos(fn, u_pos, u_neg)
f_ex: CoefficientFunction = IfPos(fn, f_pos, f_neg)
beta: CoefficientFunction = IfPos(fn, beta_pos, beta_neg)

hs = np.logspace(0, -2, num=10, base=10)
errs_penalty = np.zeros_like(hs)
errs_no_penalty = np.zeros_like(hs)
errs_cg = np.zeros_like(hs)
for i, h in enumerate(hs):
    with TaskManager():
        mesh = Mesh(big_square().GenerateMesh(maxh=h))

        fn_gfu = GridFunction(H1(mesh, order=1))
        InterpolateToP1(fn, fn_gfu)

        # ~~ partially penalized ~~
        gfu = solve_poisson_ifem(
            mesh,
            (f_neg, f_pos),
            fn_gfu,
            beta_neg,
            beta_pos,
            do_penalty=True,
            u_bnd=u_ex,
        )
        ifes = gfu.space
        assert type(ifes) is CompoundEmbTrefftzFESpace
        gfu_base = GridFunction(ifes.emb.fes)
        gfu_base.vec.data = ifes.emb.Embed(gfu.vec)

        errs_penalty[i] = l2_err_ifem(gfu_base, u_ex, fn_gfu, mesh)

        # ~~ ifem unpenalized ~~
        gfu = solve_poisson_ifem(
            mesh,
            (f_neg, f_pos),
            fn_gfu,
            beta_neg,
            beta_pos,
            do_penalty=False,
            u_bnd=u_ex,
        )
        ifes = gfu.space
        assert type(ifes) is CompoundEmbTrefftzFESpace
        gfu_base = GridFunction(ifes.emb.fes)
        gfu_base.vec.data = ifes.emb.Embed(gfu.vec)

        errs_no_penalty[i] = l2_err_ifem(gfu_base, u_ex, fn_gfu, mesh)

        # ~~ CG ~~
        gfu = solve_poisson_cg(mesh, f_ex, beta, u_bnd=u_ex)
        errs_cg[i] = l2_err_cg(gfu, u_ex, mesh)
# %% jupyter={"source_hidden": true}, tags=["hide-input"]
plt.loglog(hs, errs_penalty, label="IFEM partially penalized", marker="4")
plt.loglog(hs, errs_no_penalty, label="IFEM w/o penalty", marker="4")
plt.loglog(hs, errs_cg, label="CG", marker="4")
plt.loglog(
    hs,
    hs**2,
    label="$\\mathcal{O}(h^2)$",
    c="gray",
    linestyle="dotted",
)
plt.legend()
plt.xlabel("$h$")
plt.ylabel("$L^2$ error")
plt.tight_layout()
plt.show()

# %% [markdown]
# We see, that the IFEM methods scale with optimal rate, while the CG method does not perform well.
# We also see a hint, that the IFEM method with SIP performs better for finer meshes than without SIP.
# If we would compute for even finer meshes, we would see this trend continue.


# %% jupyter={"source_hidden": true}, tags=["hide-input"]
def cut_square() -> OCCGeometry:
    """
    returns a unit square, with a cut {x + y/2 - 3/4 = 0}
    """
    wp = WorkPlane()
    wp.MoveTo(-0.25, -0.5)
    wp.LineTo(1, -0.5)
    wp.MoveTo(1, -0.5)

    wp.LineTo(-0.25, 2.0)
    wp.MoveTo(-0.25, 2.0)

    wp.LineTo(-0.25, -0.5)
    wp.Close()
    a = wp.Face()

    wp = WorkPlane()
    wp.MoveTo(0.75, 0)

    wp.LineTo(1.0, 0)
    wp.MoveTo(1.0, 0)

    wp.LineTo(1.0, 1.0)
    wp.MoveTo(1.0, 1.0)

    wp.LineTo(0.25, 1.0)
    wp.MoveTo(0.25, 1.0)

    wp.LineTo(0.75, 0.0)
    wp.Close()
    b = wp.Face()

    faces = []

    def make_square(i: int, j: int) -> Face:
        wp = WorkPlane()
        wp.MoveTo(j / 3, i / 3)
        wp.LineTo((j + 1) / 3, i / 3)
        wp.MoveTo((j + 1) / 3, i / 3)

        wp.LineTo((j + 1) / 3, (i + 1) / 3)
        wp.MoveTo((j + 1) / 3, (i + 1) / 3)

        wp.LineTo(j / 3, (i + 1) / 3)
        wp.MoveTo(j / 3, (i + 1) / 3)

        wp.LineTo(j / 3, i / 3)
        wp.Close()
        return wp.Face()

    faces.append(make_square(0, 2) - b)
    for j in range(2):
        for i in range(3):
            faces.append(make_square(i, j) - b)

    faces.append(make_square(2, 0) - a)
    for i in range(3):
        for j in range(1, 3):
            faces.append(make_square(i, j) - a)

    return OCCGeometry(Glue(faces), dim=2)


cut_mesh = Mesh(cut_square().GenerateMesh(maxh=1.0))


# ## Rectangular mesh
# Let's consider the following cut $\Gamma = \{x + \frac{y}{2} - \frac{3}{4} = 0\}$
# on a rectangular mesh

# %%
small_mesh_quad = MakeStructured2DMesh(nx=3, ny=3)

lset = x + y / 2 - 3 / 4
lset_gfu = GridFunction(H1(small_mesh_quad, order=1))
InterpolateToP1(lset, lset_gfu)
DrawDC(lset_gfu, 1.0, -1.0, small_mesh_quad)

# %% [markdown]
# To solve the problem, we can construct a space s.t.
# the functions in this space fulfil the property
# \begin{align}
#                             〚u〛 &= 0 \text{ on } \Gamma, \\\\
# 	〚\beta \nabla u \cdot n_\Gamma〛 &= 0 \text{ on } \Gamma \\\\
# \end{align}
# again, as well as being continuous at mesh vertices.
# The space consists of piecewise bilinear functions.
#
# Note: we draw the basis function on a
# finer mesh that is aligned with the cut.
# This is done purely to get a better illustration (better visualization of kinks)
# and has nothing to do with the definition of the space.
# The space is still defined on a rectangular mesh.

# %%
ifes_quads = ImmersedQ1FE(
    small_mesh_quad, lset_gfu, beta_neg, beta_pos, impl=ImmersedQ1Impl.Canonical
)
gfu = GridFunction(ifes_quads)
gfu.vec.data[6] = 1.0
gfu_emb = ifes_quads.emb.Embed(gfu)
gfu_dg = GridFunction(L2(cut_mesh, order=10))
gfu_dg.Interpolate(
    IfPos(lset_gfu, gfu_emb.components[1], gfu_emb.components[0])
)
Draw(
    gfu_dg,
    cut_mesh,
    order=10,
    deformation=True,
    euler_angles=[-40, 2, 20],
    settings={"Objects": {"Wireframe": False}},
)

# %% [markdown]
# We have observed, that the previous space is instable in some situations.
# Therefore, we offer a non-conforming (in terms of continuity across the cut) variant as well.
#
# Note: we draw the basis function on a
# finer mesh that is aligned with the cut.
# This is done purely to get a better illustration
# (better visualization of kinks and discontinuities)
# and has nothing to do with the definition of the space.
# The space is still defined on a rectangular mesh.

# %%
ifes_quads = ImmersedQ1FE(
    small_mesh_quad,
    lset_gfu,
    beta_neg,
    beta_pos,
    impl=ImmersedQ1Impl.NonConforming,
)
gfu = GridFunction(ifes_quads)
gfu.vec.data[6] = 1.0
gfu_emb = ifes_quads.emb.Embed(gfu)
gfu_dg = GridFunction(L2(cut_mesh, order=10))
gfu_dg.Interpolate(
    IfPos(lset_gfu, gfu_emb.components[1], gfu_emb.components[0])
)
Draw(
    gfu_dg,
    cut_mesh,
    order=10,
    deformation=True,
    euler_angles=[-40, 2, 20],
    settings={"Objects": {"Wireframe": False}},
)

# %% jupyter={"source_hidden": true}, tags=["hide-input"]
(u_neg, u_pos), (f_neg, f_pos), fn = manufactured_solution(beta_neg, beta_pos)
u_ex: CoefficientFunction = IfPos(fn, u_pos, u_neg)
f_ex: CoefficientFunction = IfPos(fn, f_pos, f_neg)
beta: CoefficientFunction = IfPos(fn, beta_pos, beta_neg)

hs = np.logspace(0, -2, num=10, base=10)
errs_penalty_nonconf = np.zeros_like(hs)
errs_no_penalty_nonconf = np.zeros_like(hs)
errs_penalty_canonical = np.zeros_like(hs)
errs_no_penalty_canonical = np.zeros_like(hs)
errs_cg = np.zeros_like(hs)
for i, h in enumerate(hs):
    with TaskManager():
        mesh = MakeStructured2DMesh(
            nx=int(2 / h),
            ny=int(2 / h),
            mapping=lambda x, y: (2 * x - 1, 2 * y - 1),
        )

        fn_gfu = GridFunction(H1(mesh, order=1))
        InterpolateToP1(fn, fn_gfu)
        fn_gfu = straighten_levelset(fn_gfu)

        # ~ nonconforming ~
        # ~~ partially penalized ~~
        gfu = solve_poisson_ifem(
            mesh,
            (f_neg, f_pos),
            fn_gfu,
            beta_neg,
            beta_pos,
            do_penalty=True,
            u_bnd=u_ex,
            quads=ImmersedQ1Impl.NonConforming,
        )
        ifes = gfu.space
        assert type(ifes) is CompoundEmbTrefftzFESpace
        gfu_base = GridFunction(ifes.emb.fes)
        gfu_base.vec.data = ifes.emb.Embed(gfu.vec)

        errs_penalty_nonconf[i] = l2_err_ifem(gfu_base, u_ex, fn_gfu, mesh)

        # ~~ ifem unpenalized ~~
        gfu = solve_poisson_ifem(
            mesh,
            (f_neg, f_pos),
            fn_gfu,
            beta_neg,
            beta_pos,
            do_penalty=False,
            u_bnd=u_ex,
            quads=ImmersedQ1Impl.NonConforming,
        )
        ifes = gfu.space
        assert type(ifes) is CompoundEmbTrefftzFESpace
        gfu_base = GridFunction(ifes.emb.fes)
        gfu_base.vec.data = ifes.emb.Embed(gfu.vec)

        errs_no_penalty_nonconf[i] = l2_err_ifem(gfu_base, u_ex, fn_gfu, mesh)

        # ~ canonical ~
        # ~~ partially penalized ~~
        gfu = solve_poisson_ifem(
            mesh,
            (f_neg, f_pos),
            fn_gfu,
            beta_neg,
            beta_pos,
            do_penalty=True,
            u_bnd=u_ex,
            quads=ImmersedQ1Impl.Canonical,
        )
        ifes = gfu.space
        assert type(ifes) is CompoundEmbTrefftzFESpace
        gfu_base = GridFunction(ifes.emb.fes)
        gfu_base.vec.data = ifes.emb.Embed(gfu.vec)

        errs_penalty_canonical[i] = l2_err_ifem(gfu_base, u_ex, fn_gfu, mesh)

        # ~~ ifem unpenalized ~~
        gfu = solve_poisson_ifem(
            mesh,
            (f_neg, f_pos),
            fn_gfu,
            beta_neg,
            beta_pos,
            do_penalty=False,
            u_bnd=u_ex,
            quads=ImmersedQ1Impl.Canonical,
        )
        ifes = gfu.space
        assert type(ifes) is CompoundEmbTrefftzFESpace
        gfu_base = GridFunction(ifes.emb.fes)
        gfu_base.vec.data = ifes.emb.Embed(gfu.vec)

        errs_no_penalty_canonical[i] = l2_err_ifem(gfu_base, u_ex, fn_gfu, mesh)

        # ~~ CG ~~
        gfu = solve_poisson_cg(mesh, f_ex, beta, u_bnd=u_ex)
        errs_cg[i] = l2_err_cg(gfu, u_ex, mesh)
# %% jupyter={"source_hidden": true}, tags=["hide-input"]
plt.loglog(
    hs, errs_penalty_canonical, label="IFEM partially penalized", marker="4"
)
plt.loglog(hs, errs_no_penalty_canonical, label="IFEM w/o penalty", marker="4")
plt.loglog(hs, errs_cg, label="CG", marker="4")
plt.loglog(
    hs,
    hs**2,
    label="$\\mathcal{O}(h^2)$",
    c="gray",
    linestyle="dotted",
)
plt.legend()
plt.xlabel("$h$")
plt.ylabel("$L^2$ error")
plt.title("IFEM Q1 Canonical")
plt.tight_layout()
plt.show()

# %% jupyter={"source_hidden": true}, tags=["hide-input"]
plt.loglog(
    hs, errs_penalty_nonconf, label="IFEM partially penalized", marker="4"
)
plt.loglog(hs, errs_no_penalty_nonconf, label="IFEM w/o penalty", marker="4")
plt.loglog(hs, errs_cg, label="CG", marker="4")
plt.loglog(
    hs,
    hs**2,
    label="$\\mathcal{O}(h^2)$",
    c="gray",
    linestyle="dotted",
)
plt.legend()
plt.xlabel("$h$")
plt.ylabel("$L^2$ error")
plt.title("IFEM Q1 Non-Conforming")
plt.tight_layout()
plt.show()

# %% [markdown]
# ## Further Ressources
# <https://arxiv.org/abs/1501.00924> describes the IFEM method with SIP.
