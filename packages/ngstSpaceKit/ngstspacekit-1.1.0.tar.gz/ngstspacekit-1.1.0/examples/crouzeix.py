# %% jupyter={"source_hidden": true}
from ngsolve import (
    CF,
    H1,
    BilinearForm,
    GridFunction,
    LinearForm,
    Mesh,
    dx,
    unit_square,
)
from ngsolve.comp import SumOfIntegrals
from ngsolve.utils import grad
from ngsolve.webgui import Draw

from ngstSpaceKit.crouzeix import CrouzeixFalk, CrouzeixHO
from ngstSpaceKit.demo import CrouzeixRaviart

# %% [markdown]
# # Nonconforming Convection-Diffusion
# We are trying to solve the stationary convection-diffusion equation
#
# \begin{align}
#   - \varepsilon \Delta u + \mathrm{div}(w u) &= f \text{ in } \Omega, \\
#   u &= 0 \text{ on } \partial \Omega
# \end{align}
# with $\varepsilon > 0, w \in \mathbb{R}^n$.
#
# We want to solve the case of a convection dominated regime, i.e. $\varepsilon \ll 1, ||w||_2 \simeq 1$.
#
# We use the following variational formulation:
# Find $u_h in V_{h,0}$ s.t. for all $v_h in V_{h,0}$ there holds
#
# \begin{align}
#   \int_\Omega \varepsilon \nabla u \cdot \nabla v - u w \cdot \nabla v \,\mathrm{d}x &= \int_\Omega f v \,\mathrm{d}x,
# \end{align}
# where $V_{h,0}$ incorporates the Dirichlet boundary conditions.
# For a conforming discretization, one chooses $V_{h,0} \subseteq H^1_0$.


# %%
def conv_diff(u: GridFunction, v: GridFunction) -> SumOfIntegrals:
    return 0.05 * grad(u) * grad(v) * dx + -CF((1, 1)) * u * grad(v) * dx


source_term = 1


# %%
mesh = Mesh(unit_square.GenerateMesh(maxh=0.2))
dirichlet = ".*"

# %%
h1 = H1(mesh, order=2, dirichlet=dirichlet)

u_h1, v_h1 = h1.TnT()

a_h1 = BilinearForm(h1)
a_h1 += conv_diff(u_h1, v_h1)
a_h1.Assemble()

f_h1 = LinearForm(h1)
f_h1 += source_term * v_h1 * dx
f_h1.Assemble()

gfu_h1 = GridFunction(h1)
gfu_h1.vec.data = a_h1.mat.Inverse(freedofs=h1.FreeDofs()) * f_h1.vec

# %%
Draw(gfu_h1, deformation=True, euler_angles=[-60, 5, 30], order=2)

# %% [markdown]
# ## Problems with conforming Discretizations
# Conforming discretizations have problems in convection-dominated regimes: they exhibit locking behaviour.
# One possibility of treating the issue is to switch to a nonconforming discretization,
# such as the Crouzeix-Raviart element.

# %%
cr = CrouzeixRaviart(mesh, dirichlet=dirichlet)
gfu_cr_demo = GridFunction(cr)
gfu_cr_demo.vec.data[27] = 0.2
Draw(gfu_cr_demo, deformation=True, euler_angles=[-60, 5, 30])

# %%
u_cr, v_cr = cr.TnT()

a_cr = BilinearForm(cr)
a_cr += conv_diff(u_cr, v_cr)
a_cr.Assemble()

f_cr = LinearForm(cr)
f_cr += source_term * v_cr * dx
f_cr.Assemble()

gfu_cr = GridFunction(cr)
gfu_cr.vec.data = a_cr.mat.Inverse(freedofs=cr.FreeDofs()) * f_cr.vec

# %%
Draw(gfu_cr, deformation=True, euler_angles=[-60, 5, 30])

# %% [markdown]
# The Crouzeix-Raviart element is already implemented in ngsolve:
# ```python
# FESpace(nonconforming, mesh, order=1)
# ```
# The Crouzeix-Raviart element can be extended to higher (odd) degrees $k$. The dofs are traditionally:
# - point evaluation at $k$ Gauß-points on each edge
# - point evaluations in the interior
#
# For the sake of the implementation, we use an equivalent formulation:
# - edge integral moments against polynomials of degree $k-1$
# - integral moments against polynomials of degree $k-3$
#
# For $k=3$, the element is also known as Crouzeix-Falk

# %%
cf = CrouzeixFalk(mesh, dirichlet=dirichlet)
gfu_cf_demo = GridFunction(cf)
gfu_cf_demo.vec.data[50] = 0.1
gfu_cf_demo.vec.data[72] = 0.1
gfu_cf_demo.vec.data[91] = 0.1
gfu_cf_demo.vec.data[290] = 0.1
Draw(gfu_cf_demo, deformation=True, euler_angles=[-60, 5, 30], order=3)

# %%
u_cf, v_cf = cf.TnT()

a_cf = BilinearForm(cf)
a_cf += conv_diff(u_cf, v_cf)
a_cf.Assemble()

f_cf = LinearForm(cf)
f_cf += source_term * v_cf * dx
f_cf.Assemble()

gfu_cf = GridFunction(cf)
gfu_cf.vec.data = a_cf.mat.Inverse(freedofs=cf.FreeDofs()) * f_cf.vec

# %%
Draw(gfu_cf, deformation=True, euler_angles=[-60, 5, 30], order=3)

# %% [markdown]
# We can go even higher
# %%
ho = CrouzeixHO(mesh, order=5, dirichlet=dirichlet)

u_ho, v_ho = ho.TnT()

a_ho = BilinearForm(ho)
a_ho += conv_diff(u_ho, v_ho)
a_ho.Assemble()

f_ho = LinearForm(ho)
f_ho += source_term * v_ho * dx
f_ho.Assemble()

gfu_ho = GridFunction(ho)
gfu_ho.vec.data = a_ho.mat.Inverse(freedofs=ho.FreeDofs()) * f_ho.vec

# %%
Draw(gfu_ho, deformation=True, euler_angles=[-60, 5, 30], order=5)
