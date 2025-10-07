from dataclasses import dataclass

import ngsolve
from ngsolve import (
    BBBND,
    BBND,
    BND,
    H1,
    L2,
    TET,
    TRIG,
    IntegrationRule,
    dx,
)
from ngsolve.utils import FacetFESpace
from ngstrefftz import EmbeddedTrefftzFES, L2EmbTrefftzFESpace, TrefftzEmbedding

from ngstSpaceKit.diffops import del_x, del_y, del_z
from ngstSpaceKit.mesh_properties import (
    throw_on_wrong_mesh_dimension,
    throw_on_wrong_mesh_eltype,
)


@dataclass
class HermiteDirichlet:
    """
    Holds the dirichlet instructions for every type of dof in the `Hermite` space separately.

    `deriv_z` is only used in the 3D case.
    """

    vertex_value: str = ""
    deriv_x: str = ""
    deriv_y: str = ""
    deriv_z: str = ""

    @classmethod
    def clamp(cls, bnd: str) -> "HermiteDirichlet":
        """
        `bnd`: boundary where clamp conditions shall be set.
        """
        return cls(vertex_value=bnd, deriv_x=bnd, deriv_y=bnd, deriv_z=bnd)


def Hermite(
    mesh: ngsolve.comp.Mesh,
    dirichlet: str | HermiteDirichlet = "",
    check_mesh: bool = True,
    stats: dict | None = None,
) -> L2EmbTrefftzFESpace:
    r"""
    The Hermite element is implemented for 2D and 3D on triangles and tetrahedrons.

    `check_mesh`: test, if the `mesh` is compatible with this space

    `stats`: use the `stats` flag of the `TrefftzEmbeddin` method

    # Raises
    - ValueError, if the mesh is neither 2D nor 3D
    - ValueError, if the mesh is neither triangular nor tetrahedral

    # Conforming Trefftz Formulation for 2D
    - $\mathbb{V}_h := \mathbb{P}^{3, \text{disc}}(\mathcal{T}_h)$
    - $\mathbb{Z}_h := [\mathbb{P}^{1}(\mathcal{T}_h)]^3 \times \mathbb{P}^{0}(\mathcal{T}_h)$
    - \begin{align}
      \mathcal{C}_K(v_h&, (z_h^\text{value}, z_h^\text{x}, z_h^\text{y}, z_h^\text{mid})) := \\\\
          &\sum_{p \text{ is vertex}} v_h(p) z_h^\text{value}(p)
          + \sum_{p \text{ is vertex}} \partial_x v_h(p) z_h^\text{x}(p) \\\\
          &+ \sum_{p \text{ is vertex}} \partial_y v_h(p) z_h^\text{y}(p)
          + \sum_{m \text{ is element-midpoint}} v_h(m) z_h^\text{mid}(m), \\\\
      \mathcal{D}_K((y_h^\text{value}, y_h^\text{x}, y_h^\text{y}, y_h^\text{mid})&, (z_h^\text{value}, z_h^\text{x}, z_h^\text{y}, z_h^\text{mid})) := \\\\
          &\sum_{p \text{ is vertex}} y_h^\text{value}(p) z_h^\text{value}(p)
          + \sum_{p \text{ is vertex}} y_h^\text{x}(p) z_h^\text{x}(p) \\\\
          &+ \sum_{p \text{ is vertex}} y_h^\text{y}(p) z_h^\text{y}(p)
          + \sum_{m \text{ is element-midpoint}} y_h^\text{mid}(m) z_h^\text{mid}(m)
      \end{align}
    """
    if check_mesh:
        throw_on_wrong_mesh_dimension(mesh, [2, 3])
        throw_on_wrong_mesh_eltype(mesh, [TRIG, TET])

    dirichlet_struct = (
        HermiteDirichlet(vertex_value=dirichlet)
        if type(dirichlet) is str
        else dirichlet
    )
    assert type(dirichlet_struct) is HermiteDirichlet

    if mesh.dim == 2:
        return Hermite2D(
            mesh,
            dirichlet_struct,
            check_mesh=False,
            stats=stats,
        )
    else:
        return Hermite3D(
            mesh,
            dirichlet_struct,
            check_mesh=False,
            stats=stats,
        )


def Hermite2D(
    mesh: ngsolve.comp.Mesh,
    dirichlet: HermiteDirichlet,
    check_mesh: bool = True,
    stats: dict | None = None,
) -> L2EmbTrefftzFESpace:
    """
    Implementation of the Hermite element in 2D

    `check_mesh`: test, if the `mesh` is compatible with this space

    `stats`: use the `stats` flag of the `TrefftzEmbeddin` method

    # Raises
    - ValueError, if the mesh is not 2D
    - ValueError, if the mesh is not triangular
    """
    if check_mesh:
        throw_on_wrong_mesh_dimension(mesh, 2)
        throw_on_wrong_mesh_eltype(mesh, TRIG)

    fes = L2(mesh, order=3)
    vertex_value_space = H1(mesh, order=1, dirichlet=dirichlet.vertex_value)
    deriv_x_value_space = H1(mesh, order=1, dirichlet=dirichlet.deriv_x)
    deriv_y_value_space = H1(mesh, order=1, dirichlet=dirichlet.deriv_y)
    midpoint_value_space = L2(mesh, order=0)

    conformity_space = (
        vertex_value_space
        * deriv_x_value_space
        * deriv_y_value_space
        * midpoint_value_space
    )

    u = fes.TrialFunction()
    (u_, u_dx, u_dy, u_m) = conformity_space.TrialFunction()
    (v_, v_dx, v_dy, v_m) = conformity_space.TestFunction()

    dVertex = dx(element_vb=BBND)

    midpoint_intrule = IntegrationRule(points=[(1 / 3, 1 / 3)], weights=[1])
    dMidpoint = dx(intrules={TRIG: midpoint_intrule})

    cop_lhs = (
        u * v_ * dVertex
        + del_x(u) * v_dx * dVertex
        + del_y(u) * v_dy * dVertex
        + u * v_m * dMidpoint
    )
    cop_rhs = (
        u_ * v_ * dVertex
        + u_dx * v_dx * dVertex
        + u_dy * v_dy * dVertex
        + u_m * v_m * dVertex
    )

    embedding = TrefftzEmbedding(
        cop=cop_lhs,
        crhs=cop_rhs,
        ndof_trefftz=0,
        stats=stats,
    )

    hermite = EmbeddedTrefftzFES(embedding)
    assert type(hermite) is L2EmbTrefftzFESpace, (
        "The hermite space should always be an L2EmbTrefftzFESpace"
    )

    return hermite


def Hermite3D(
    mesh: ngsolve.comp.Mesh,
    dirichlet: HermiteDirichlet,
    check_mesh: bool = True,
    stats: dict | None = None,
) -> L2EmbTrefftzFESpace:
    """
    Implementation of the Hermite element in 3D

    `check_mesh`: test, if the `mesh` is compatible with this space

    `stats`: use the `stats` flag of the `TrefftzEmbeddin` method

    # Raises
    - ValueError, if the mesh is not 3D
    - ValueError, if the mesh is not tetrahedral
    """
    if check_mesh:
        throw_on_wrong_mesh_dimension(mesh, 3)
        throw_on_wrong_mesh_eltype(mesh, TET)

    fes = L2(mesh, order=3)
    vertex_value_space = H1(mesh, order=1, dirichlet=dirichlet.vertex_value)
    deriv_x_value_space = H1(mesh, order=1, dirichlet=dirichlet.deriv_x)
    deriv_y_value_space = H1(mesh, order=1, dirichlet=dirichlet.deriv_y)
    deriv_z_value_space = H1(mesh, order=1, dirichlet=dirichlet.deriv_z)
    midpoint_value_space = FacetFESpace(mesh, order=0)

    conformity_space = (
        vertex_value_space
        * deriv_x_value_space
        * deriv_y_value_space
        * deriv_z_value_space
        * midpoint_value_space
    )

    u = fes.TrialFunction()
    (u_, u_dx, u_dy, u_dz, u_m) = conformity_space.TrialFunction()
    (v_, v_dx, v_dy, v_dz, v_m) = conformity_space.TestFunction()

    dVertex = dx(element_vb=BBBND)

    midpoint_intrule = IntegrationRule(points=[(1 / 3, 1 / 3)], weights=[1])
    dMidpoint = dx(intrules={TRIG: midpoint_intrule}, element_vb=BND)

    cop_lhs = (
        u * v_ * dVertex
        + del_x(u) * v_dx * dVertex
        + del_y(u) * v_dy * dVertex
        + del_z(u) * v_dz * dVertex
        + u * v_m * dMidpoint
    )
    cop_rhs = (
        u_ * v_ * dVertex
        + u_dx * v_dx * dVertex
        + u_dy * v_dy * dVertex
        + u_dz * v_dz * dVertex
        + u_m * v_m * dVertex
    )

    embedding = TrefftzEmbedding(
        cop=cop_lhs,
        crhs=cop_rhs,
        ndof_trefftz=0,
        stats=stats,
    )

    hermite = EmbeddedTrefftzFES(embedding)
    assert type(hermite) is L2EmbTrefftzFESpace, (
        "The hermite space should always be an L2EmbTrefftzFESpace"
    )

    return hermite
