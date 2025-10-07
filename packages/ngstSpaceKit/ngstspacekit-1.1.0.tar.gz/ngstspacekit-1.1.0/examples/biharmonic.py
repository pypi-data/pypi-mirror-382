# %% jupyter={"source_hidden": true}, tags=["hide-input"]
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
from netgen.occ import OCCGeometry, WorkPlane
from ngsolve import (
    CF,
    BilinearForm,
    CoefficientFunction,
    GridFunction,
    InnerProduct,
    Integrate,
    LinearForm,
    Mesh,
    TaskManager,
    dx,
    pi,
    sin,
    sqrt,
    unit_square,
    x,
    y,
)
from ngsolve.webgui import Draw

from ngstSpaceKit import Argyris
from ngstSpaceKit.argyris import ArgyrisDirichlet, interpolate_to_argyris
from ngstSpaceKit.diffops import grad, hesse, laplace

plt.rcParams["font.family"] = "cmr10"
plt.rcParams["mathtext.fontset"] = "cm"
plt.rcParams["axes.formatter.use_mathtext"] = True

# %% [markdown]
# # The biharmonic equation
#
# The biharmonic equation with clamp boundary conditions reads as
# \begin{align}
# \Delta^2 u &= q \text{ in } \Omega, \\
# u &= 0 \text{ on } \partial \Omega, \\
# \nabla u \cdot n &= 0 \text{ on } \partial \Omega.
# \end{align}
# This equation describes the behaviour of a plate bending under a load force of magnitude $q$.
#
# We arrive at the weak formulation: Find $u_h \in V_h$ s.t. for all $v_h \in V_h$ there holds
# \begin{align}
# \int_\Omega \Delta u_h \Delta v_h \,\mathrm{d} x= \int_\Omega q v_h \,\mathrm{d} x
# \end{align}
#
# For the formulation to make sense, we require $V_h \subseteq H^2_0(\Omega)$.
# One example of an $H^2_0$-conforming element is the Argyris element on the unit square.
#
# We solve for a constant load force of $1$ on the unit square.


# %%
mesh = Mesh(unit_square.GenerateMesh(maxh=0.25))

dir_bnd = "left|right|top|bottom"
dir_lr = "left|right"
dir_tb = "top|bottom"

fes = Argyris(
    mesh,
    order=5,
    dirichlet=ArgyrisDirichlet(
        vertex_value=dir_bnd,
        deriv_x=dir_tb,
        deriv_y=dir_lr,
        deriv_xx=dir_tb,
        deriv_yy=dir_lr,
        deriv_xy=dir_bnd,
        deriv_normal_moment=dir_bnd,
    ),
)
u, v = fes.TnT()

a = BilinearForm(fes)

a += laplace(u) * laplace(v) * dx

a.Assemble()

f = LinearForm(fes)
f += v * dx
f.Assemble()

gfu = GridFunction(fes)

gfu.vec.data = a.mat.Inverse(freedofs=fes.FreeDofs()) * f.vec

# %%
Draw(5e2 * gfu, mesh, deformation=True, euler_angles=[-60, 5, 30], order=5)

# %% [markdown]
# We want to test how well the Argyris element error scales.
# We consider the following manufactured solution


# %%
def exact_solution():
    return sin(pi * x) ** 2 * sin(pi * y) ** 2


def exact_solution_grad():
    return grad(exact_solution(), 2)


def exact_solution_hesse():
    f = exact_solution()
    w_hesse = CF(
        (
            f.Diff(x).Diff(x),
            f.Diff(x).Diff(y),
            f.Diff(x).Diff(y),
            f.Diff(y).Diff(y),
        ),
        dims=(2, 2),
    )
    return w_hesse


def exact_rhs():
    f = exact_solution()
    return laplace(laplace(f))


# %%
u_ex = exact_solution()
# %%
Draw(u_ex, mesh, deformation=True, euler_angles=[-60, 5, 30], order=5)

# %%
Draw(
    exact_solution_grad(),
    mesh,
    order=5,
    vectors={"grid_size": 20, "offset": 0.5},
)

# %%
u_ex_hesse = exact_solution_hesse()
Draw(
    2e-2
    * sqrt(
        u_ex_hesse[0, 0] ** 2
        + 2 * u_ex_hesse[0, 1] ** 2
        + u_ex_hesse[1, 1] ** 2
    ),
    mesh,
    deformation=True,
    euler_angles=[-60, 5, 30],
    order=5,
)

# %%
Draw(
    2e-4 * exact_rhs(),
    mesh,
    deformation=True,
    euler_angles=[-60, 5, 30],
    order=5,
)


# %% [markdown]
# You can study the $L^2$-, $H^1$-, and $H^2$- error of the discrete solution in relation
# to the mesh size.
#
# The results behave as expected.


# %%
def biharmonic_solution(
    mesh: Mesh, dirichlet: ArgyrisDirichlet
) -> GridFunction:
    """
    Solves the biharmonic equation with clamp boundary conditions.
    """
    fes = Argyris(mesh, order=5, dirichlet=dirichlet)
    u, v = fes.TnT()

    a = BilinearForm(fes)

    a += laplace(u) * laplace(v) * dx

    a.Assemble()

    f = LinearForm(fes)
    f += exact_rhs() * v * dx
    f.Assemble()

    gfu = GridFunction(fes)

    gfu.vec.data = a.mat.Inverse(freedofs=fes.FreeDofs()) * f.vec
    return gfu


dirichlet = ArgyrisDirichlet(
    vertex_value=".*",
    deriv_x=".*",
    deriv_y=".*",
    deriv_xx="top|bottom",
    deriv_yy="left|right",
    deriv_xy=".*",
    deriv_normal_moment=".*",
)


# %% jupyter={"source_hidden": true}, tags=["hide-input"]
def l2_err(f: CoefficientFunction, mesh: Mesh):
    return sqrt(Integrate((f - exact_solution()) ** 2, mesh))


def h1_err(gfu: GridFunction, mesh: Mesh):
    sol_grad = exact_solution_grad()
    return sqrt(
        Integrate(
            InnerProduct(grad(gfu) - sol_grad, grad(gfu) - sol_grad), mesh
        )
        + l2_err(gfu, mesh) ** 2
    )


def h2_err(gfu: GridFunction, mesh: Mesh):
    sol_hesse = exact_solution_hesse()
    dif_hesse = hesse(gfu) - sol_hesse
    return sqrt(
        Integrate(
            dif_hesse[0, 0] ** 2 + 2 * dif_hesse[0, 1] + dif_hesse[1, 1] ** 2,
            mesh,
        )
        + h1_err(gfu, mesh) ** 2
    )


def biharmoic_scaling(
    refinements: int = 6,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    errs_l2 = np.zeros(refinements)
    errs_h1 = np.zeros(refinements)
    errs_h2 = np.zeros(refinements)
    hs = np.zeros(refinements)
    for i in range(1, refinements + 1):
        with TaskManager():
            maxh = 0.5 / (2.0**i)
            mesh = Mesh(unit_square.GenerateMesh(maxh=maxh))
            hs[i - 1] = maxh
            sol = biharmonic_solution(mesh, dirichlet)
            errs_l2[i - 1] = l2_err(sol, mesh)
            errs_h1[i - 1] = h1_err(sol, mesh)
            errs_h2[i - 1] = h2_err(sol, mesh)
    return hs, errs_l2, errs_h1, errs_h2


hs, errs_l2, errs_h1, errs_h2 = biharmoic_scaling(4)

# %% jupyter={"source_hidden": true}, tags=["hide-input"]

b = 1e-0
a = 6
plt.loglog(
    hs,
    b * hs**a,
    label="$y \\in \\mathcal{O}(h^{" + f"{a}" + "})" + "$",
    c="gray",
    linestyle="dotted",
)
plt.loglog(hs, errs_l2, label="$L^2$ error", marker="4")
plt.legend()
plt.xlabel("h")
plt.ylabel("$L^2$-error")
plt.show()

# %% jupyter={"source_hidden": true}, tags=["hide-input"]
b = 1e-0
a = 5
plt.loglog(
    hs,
    b * hs**a,
    label="$y \\in \\mathcal{O}(h^{" + f"{a}" + "})" + "$",
    c="gray",
    linestyle="dotted",
)
plt.loglog(hs, errs_h1, label="$H^1$ error", marker="4")
plt.legend()
plt.xlabel("h")
plt.ylabel("$H^1$-error")
plt.show()

# %% jupyter={"source_hidden": true}, tags=["hide-input"]
b = 1e-0
a = 4
plt.loglog(
    hs,
    b * hs**a,
    label="$y \\in \\mathcal{O}(h^{" + f"{a}" + "})" + "$",
    c="gray",
    linestyle="dotted",
)
plt.loglog(hs, errs_h2, label="$H^2$ error", marker="4")
plt.legend()
plt.xlabel("h")
plt.ylabel("$H^2$-error")
plt.show()

# %% [markdown]
# ## Hexagonal Domain
#
# You can also use other geometries.
#
# Let's use a hexagonal domain, with the exact same manufactured solution.


# %%
def mesh_hex(maxh: float = 0.25) -> Mesh:
    wp = WorkPlane().Rotate(0)
    for i in range(6):
        wp.Line(1).Rotate(60)
    hex = wp.Face()
    hex.edges.name = "hex"
    mesh = Mesh(OCCGeometry(hex, dim=2).GenerateMesh(maxh=maxh))
    return mesh


mesh = mesh_hex(maxh=0.25)

Draw(mesh)

# %%
Draw(u_ex, mesh, deformation=True, euler_angles=[-60, 5, 30], order=5)

# %%
Draw(
    exact_solution_grad(),
    mesh,
    order=5,
    vectors={"grid_size": 20, "offset": 0.5},
)

# %%
u_ex_hesse = exact_solution_hesse()
Draw(
    2e-2
    * sqrt(
        u_ex_hesse[0, 0] ** 2
        + 2 * u_ex_hesse[0, 1] ** 2
        + u_ex_hesse[1, 1] ** 2
    ),
    mesh,
    deformation=True,
    euler_angles=[-60, 5, 30],
    order=5,
)

# %%
Draw(
    2e-4 * exact_rhs(),
    mesh,
    deformation=True,
    euler_angles=[-60, 5, 30],
    order=5,
)

# %% [markdown]
# Obviously, the manufactured solution does not adhere to homogeneous
# clamped boundary conditions on this new domain.
# To solve this, we can homogenize the problem.
#
# First, you need to obtain values for all Dirichlet dofs on the boundary.
# For the manufactured solution, we compute them from the exact solution.


# %%
def argyris_ubnd(mesh: Mesh, dirichlet: ArgyrisDirichlet) -> GridFunction:
    fes = Argyris(mesh, order=5, dirichlet=dirichlet)
    return interpolate_to_argyris(u_ex, fes, dirichlet_only=True)


Draw(
    argyris_ubnd(mesh, dirichlet),
    deformation=True,
    euler_angles=[-60, 5, 30],
    order=5,
)


# %% [markdown]
# Then, we can compute the homogenized version.
# Here, we set all types of dofs as Dirichlet dofs
# on the boundary.


# %%
dirichlet = ArgyrisDirichlet(
    vertex_value=".*",
    deriv_x=".*",
    deriv_y=".*",
    deriv_xx=".*",
    deriv_xy=".*",
    deriv_yy=".*",
    deriv_normal_moment=".*",
)


def biharmonic_solution_with_bnd(
    mesh: Mesh,
    dirichlet: ArgyrisDirichlet,
    rhs: CoefficientFunction,
    u_bnd: GridFunction,
) -> GridFunction:
    """
    Solves the biharmonic equation with boundary conditions and a given right-hand-side
    """
    fes = Argyris(
        mesh,
        order=5,
        dirichlet=dirichlet,
    )
    u, v = fes.TnT()

    a = BilinearForm(fes)
    a += laplace(u) * laplace(v) * dx
    a.Assemble()

    f = LinearForm(fes)
    f += rhs * v * dx
    f.Assemble()

    gfu = GridFunction(fes)
    f.vec.data -= a.mat * u_bnd.vec
    gfu.vec.data += u_bnd.vec
    gfu.vec.data += (
        a.mat.Inverse(freedofs=fes.FreeDofs(), inverse="sparsecholesky") * f.vec
    )
    return gfu


# %% [markdown]
# Again, we get optimal error scaling.


# %% jupyter={"source_hidden": true}, tags=["hide-input"]
def biharmoic_scaling_with_bnd(
    refinements: int = 6,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    errs_l2 = np.zeros(refinements)
    errs_h1 = np.zeros(refinements)
    errs_h2 = np.zeros(refinements)
    hs = np.zeros(refinements)
    for i in range(1, refinements + 1):
        with TaskManager():
            maxh = 0.5 / (2.0**i)
            mesh = mesh_hex(maxh)
            hs[i - 1] = maxh
            sol = biharmonic_solution_with_bnd(
                mesh, dirichlet, exact_rhs(), argyris_ubnd(mesh, dirichlet)
            )
            errs_l2[i - 1] = l2_err(sol, mesh)
            errs_h1[i - 1] = h1_err(sol, mesh)
            errs_h2[i - 1] = h2_err(sol, mesh)
    return hs, errs_l2, errs_h1, errs_h2


hs, errs_l2, errs_h1, errs_h2 = biharmoic_scaling_with_bnd(4)

# %% jupyter={"source_hidden": true}, tags=["hide-input"]

b = 1e-0
a = 6
plt.loglog(
    hs,
    b * hs**a,
    label="$y \\in \\mathcal{O}(h^{" + f"{a}" + "})" + "$",
    c="gray",
    linestyle="dotted",
)
plt.loglog(hs, errs_l2, label="$L^2$ error", marker="4")
plt.legend()
plt.xlabel("h")
plt.ylabel("$L^2$-error")
plt.show()

# %% jupyter={"source_hidden": true}, tags=["hide-input"]
b = 1e-0
a = 5
plt.loglog(
    hs,
    b * hs**a,
    label="$y \\in \\mathcal{O}(h^{" + f"{a}" + "})" + "$",
    c="gray",
    linestyle="dotted",
)
plt.loglog(hs, errs_h1, label="$H^1$ error", marker="4")
plt.legend()
plt.xlabel("h")
plt.ylabel("$H^1$-error")
plt.show()

# %% jupyter={"source_hidden": true}, tags=["hide-input"]
b = 1e-0
a = 4
plt.loglog(
    hs,
    b * hs**a,
    label="$y \\in \\mathcal{O}(h^{" + f"{a}" + "})" + "$",
    c="gray",
    linestyle="dotted",
)
plt.loglog(hs, errs_h2, label="$H^2$ error", marker="4")
plt.legend()
plt.xlabel("h")
plt.ylabel("$H^2$-error")
plt.show()
