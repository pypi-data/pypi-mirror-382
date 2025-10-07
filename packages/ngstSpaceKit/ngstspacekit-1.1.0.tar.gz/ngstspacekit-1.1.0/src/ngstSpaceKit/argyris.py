from dataclasses import dataclass

import ngsolve
from ngsolve import (
    BBND,
    BND,
    H1,
    L2,
    TRIG,
    FacetFESpace,
    NormalFacetFESpace,
    dx,
    grad,
    specialcf,
    x,
    y,
)
from ngsolve.solve_implementation import CoefficientFunction, GridFunction
from ngstrefftz import EmbeddedTrefftzFES, L2EmbTrefftzFESpace, TrefftzEmbedding

from ngstSpaceKit.diffops import del_x, del_xx, del_xy, del_y, del_yy
from ngstSpaceKit.mesh_properties import (
    throw_on_wrong_mesh_dimension,
    throw_on_wrong_mesh_eltype,
)


@dataclass
class ArgyrisDirichlet:
    """
    Holds the dirichlet instructions for every type of dof in the Argyris space separately.
    """

    vertex_value: str = ""
    deriv_x: str = ""
    deriv_y: str = ""
    deriv_xx: str = ""
    deriv_xy: str = ""
    deriv_yy: str = ""
    deriv_normal_moment: str = ""
    facet_moment: str = ""

    @classmethod
    def clamp_weak(cls, bnd: str) -> "ArgyrisDirichlet":
        """
        `bnd`: boundary where (weak) clamp conditions shall be set.

        By the nature of the Argyris space, the clamp conditions will not apply to the whole boundary,
        but only at certain points along the boundary. Further action is necessary to completely enforce clamp conditions.
        """
        return cls(
            vertex_value=bnd, deriv_normal_moment=bnd, deriv_x=bnd, deriv_y=bnd
        )


def Argyris(
    mesh: ngsolve.comp.Mesh,
    order: int = 5,
    dirichlet: str | ArgyrisDirichlet = "",
    check_mesh: bool = True,
    stats: dict | None = None,
) -> L2EmbTrefftzFESpace:
    r"""
    Implementation of the Argyris finite element.

    `order`: requires `order >= 5`

    `dirichlet`: if you provide a string, it will set dirichlet conditions only for vertex value dofs. For more control, use `ArgyrisDirichlet`.

    `check_mesh`: test, if the `mesh` is compatible with this space

    `stats`: use the `stats` flag of the `TrefftzEmbeddin` method

    # Raises
    - ValueError, if the mesh is not 2D
    - ValueError, if the mesh is not triangular
    - ValueError, if `order < 5`

    # Conforming Trefftz Formulation for $k=5$
    - $\mathbb{V}_h := \mathbb{P}^{5, \text{disc}}(\mathcal{T}_h)$
    - $\mathbb{Z}_h := [\mathbb{P}^{1}(\mathcal{T}_h)]^6 \times [\mathbb{P}^{0}(\mathcal{T}_h)]^2$
    - \begin{align}
      \mathcal{C}_K(v_h&, (z_h^\text{value}, z_h^\text{x}, z_h^\text{y}, z_h^\text{xx}, z_h^\text{xy}, z_h^\text{yy}, z_h^\text{n})) := \\\\
          &\sum_{p \text{ is vertex}} v_h(p) z_h^\text{value}(p)
          + \sum_{p \text{ is vertex}} \partial_x v_h(p) z_h^\text{x}(p) \\\\
          &+ \sum_{p \text{ is vertex}} \partial_y v_h(p) z_h^\text{y}(p)
          + \sum_{p \text{ is vertex}} \partial_{xx} v_h(p) z_h^\text{xx}(p) \\\\
          &+ \sum_{p \text{ is vertex}} \partial_{xy} v_h(p) z_h^\text{xy}(p)
          + \sum_{p \text{ is vertex}} \partial_{yy} v_h(p) z_h^\text{yy}(p) \\\\
          &+ \int_{\partial K} \nabla v_h \cdot n \; z_h^\text{n} \cdot n \;dS,\\\\
      \mathcal{D}_K((y_h^\text{value}, y_h^\text{x}, y_h^\text{y}, y_h^\text{xx}, y_h^\text{xy}, y_h^\text{yy}, y_h^\text{n})&, (z_h^\text{value}, z_h^\text{x}, z_h^\text{y}, z_h^\text{xx}, z_h^\text{xy}, z_h^\text{yy}, z_h^\text{n})) := \\\\
          &\sum_{p \text{ is vertex}} y_h^\text{value}(p) z_h^\text{value}(p)
          + \sum_{p \text{ is vertex}} y_h^\text{x}(p) z_h^\text{x}(p) \\\\
          &+ \sum_{p \text{ is vertex}} y_h^\text{y}(p) z_h^\text{y}(p)
          + \sum_{p \text{ is vertex}} y_h^\text{xx}(p) z_h^\text{xx}(p) \\\\
          &+ \sum_{p \text{ is vertex}} y_h^\text{xy}(p) z_h^\text{xy}(p)
          + \sum_{p \text{ is vertex}} y_h^\text{yy}(p) z_h^\text{yy}(p) \\\\
          &+ \int_{\partial K} y_h^\text{n} \cdot n \; z_h^\text{n} \cdot n \;dS
      \end{align}
    """
    if check_mesh:
        throw_on_wrong_mesh_dimension(mesh, 2)
        throw_on_wrong_mesh_eltype(mesh, TRIG)

    dirichlet_struct = (
        ArgyrisDirichlet(vertex_value=dirichlet)
        if type(dirichlet) is str
        else dirichlet
    )
    assert type(dirichlet_struct) is ArgyrisDirichlet

    if order < 5:
        raise ValueError(f"Argyris requires order > 5, but order = {order}")
    elif order > 5:
        return ArgyrisHO(
            mesh,
            order,
            dirichlet_struct,
            check_mesh=False,
            stats=stats,
        )

    # order == 5 from now on

    fes = L2(mesh, order=5)

    vertex_value_space = H1(
        mesh, order=1, dirichlet=dirichlet_struct.vertex_value
    )
    deriv_x_value_space = H1(mesh, order=1, dirichlet=dirichlet_struct.deriv_x)
    deriv_y_value_space = H1(mesh, order=1, dirichlet=dirichlet_struct.deriv_y)
    deriv_xx_value_space = H1(
        mesh, order=1, dirichlet=dirichlet_struct.deriv_xx
    )
    deriv_xy_value_space = H1(
        mesh, order=1, dirichlet=dirichlet_struct.deriv_xy
    )
    deriv_yy_value_space = H1(
        mesh, order=1, dirichlet=dirichlet_struct.deriv_yy
    )
    normal_deriv_moment_space = NormalFacetFESpace(
        mesh, order=0, dirichlet=dirichlet_struct.deriv_normal_moment
    )

    conformity_space = (
        vertex_value_space
        * deriv_x_value_space
        * deriv_y_value_space
        * deriv_xx_value_space
        * deriv_xy_value_space
        * deriv_yy_value_space
        * normal_deriv_moment_space
    )

    u = fes.TrialFunction()
    (u_, u_dx, u_dy, u_dxx, u_dxy, u_dyy, u_n) = (
        conformity_space.TrialFunction()
    )
    (v_, v_dx, v_dy, v_dxx, v_dxy, v_dyy, v_n) = conformity_space.TestFunction()

    dVertex = dx(element_vb=BBND)
    dFace = dx(element_vb=BND)
    n = specialcf.normal(2)

    cop_lhs = (
        u * v_ * dVertex
        + del_x(u) * v_dx * dVertex
        + del_y(u) * v_dy * dVertex
        + del_xx(u) * v_dxx * dVertex
        + del_xy(u) * v_dxy * dVertex
        + del_yy(u) * v_dyy * dVertex
        + grad(u) * n * v_n * n * dFace
    )
    cop_rhs = (
        u_ * v_ * dVertex
        + u_dx * v_dx * dVertex
        + u_dy * v_dy * dVertex
        + u_dxx * v_dxx * dVertex
        + u_dxy * v_dxy * dVertex
        + u_dyy * v_dyy * dVertex
        + u_n * n * v_n * n * dFace
    )

    embedding = TrefftzEmbedding(
        cop=cop_lhs,
        crhs=cop_rhs,
        ndof_trefftz=0,
        stats=stats,
    )

    argyris = EmbeddedTrefftzFES(embedding)
    assert type(argyris) is L2EmbTrefftzFESpace, (
        "The argyris space should always be an L2EmbTrefftzFESpace"
    )

    return argyris


def ArgyrisHO(
    mesh: ngsolve.comp.Mesh,
    order: int = 6,
    dirichlet: ArgyrisDirichlet = ArgyrisDirichlet(),
    check_mesh: bool = True,
    stats: dict | None = None,
) -> L2EmbTrefftzFESpace:
    """
    The volume moments are not implemented as moments against a Lagrange space of order k = order-6.
    Since they do not add to the C1-conformity of the element, their purpose is just to fill the remaining dofs
    of the polynomial space. So, we use the conforming Trefftz method to just fill the remaining dofs with suitable
    basis functions dynamically.

    # Raises
    - ValueError, if the mesh is not 2D
    - ValueError, if the mesh is not triangular
    """
    if check_mesh:
        throw_on_wrong_mesh_dimension(mesh, 2)
        throw_on_wrong_mesh_eltype(mesh, TRIG)

    if order < 6:
        raise ValueError(
            f"Argyris higher order requires order > 6, but order = {order}"
        )

    fes = L2(mesh, order=order)

    vertex_value_space = H1(mesh, order=1, dirichlet=dirichlet.vertex_value)
    deriv_x_value_space = H1(mesh, order=1, dirichlet=dirichlet.deriv_x)
    deriv_y_value_space = H1(mesh, order=1, dirichlet=dirichlet.deriv_y)
    deriv_xx_value_space = H1(mesh, order=1, dirichlet=dirichlet.deriv_xx)
    deriv_xy_value_space = H1(mesh, order=1, dirichlet=dirichlet.deriv_xy)
    deriv_yy_value_space = H1(mesh, order=1, dirichlet=dirichlet.deriv_yy)
    normal_deriv_moment_space = NormalFacetFESpace(
        mesh, order=order - 5, dirichlet=dirichlet.deriv_normal_moment
    )
    facet_moment_space = FacetFESpace(
        mesh, order=order - 6, dirichlet=dirichlet.facet_moment
    )
    # Usually, Argyris requires a volume moment against a Lagrange space of k = order-6,
    # but we use conforming Trefftz here to dynamically add suitable basis functions.

    conformity_space = (
        vertex_value_space
        * deriv_x_value_space
        * deriv_y_value_space
        * deriv_xx_value_space
        * deriv_xy_value_space
        * deriv_yy_value_space
        * normal_deriv_moment_space
        * facet_moment_space
    )

    u = fes.TrialFunction()
    (u_, u_dx, u_dy, u_dxx, u_dxy, u_dyy, u_n, u_f) = (
        conformity_space.TrialFunction()
    )
    (v_, v_dx, v_dy, v_dxx, v_dxy, v_dyy, v_n, v_f) = (
        conformity_space.TestFunction()
    )

    dVertex = dx(element_vb=BBND)
    dFace = dx(element_vb=BND)
    n = specialcf.normal(2)

    cop_lhs = (
        u * v_ * dVertex
        + del_x(u) * v_dx * dVertex
        + del_y(u) * v_dy * dVertex
        + del_xx(u) * v_dxx * dVertex
        + del_xy(u) * v_dxy * dVertex
        + del_yy(u) * v_dyy * dVertex
        + grad(u) * n * v_n * n * dFace
        + u * v_f * dFace
    )
    cop_rhs = (
        u_ * v_ * dVertex
        + u_dx * v_dx * dVertex
        + u_dy * v_dy * dVertex
        + u_dxx * v_dxx * dVertex
        + u_dxy * v_dxy * dVertex
        + u_dyy * v_dyy * dVertex
        + u_n * n * v_n * n * dFace
        + u_f * v_f * dFace
    )

    # `op = None` fills the remaining dofs (which are not already covered by the conformity constraints)
    # with suitable basis functions
    embedding = TrefftzEmbedding(
        cop=cop_lhs,
        crhs=cop_rhs,
        ndof_trefftz=0,
        stats=stats,
    )

    argyris = EmbeddedTrefftzFES(embedding)
    assert type(argyris) is L2EmbTrefftzFESpace, (
        "The argyris space should always be an L2EmbTrefftzFESpace"
    )

    return argyris


def interpolate_to_argyris(
    cf: CoefficientFunction,
    argyris: L2EmbTrefftzFESpace,
    dirichlet_only: bool = False,
) -> GridFunction:
    """
    `dirichlet_only`: only do the interpolation for Dirichlet dofs
    """
    if argyris.globalorder != 5:
        raise NotImplementedError(
            "At the moment, this method is only implemented for order 5"
        )

    gfu_global = GridFunction(argyris)

    # backup for the missing normal moment interpolation
    gfu_global.Interpolate(cf)

    (
        vertex_value_space,
        deriv_x_value_space,
        deriv_y_value_space,
        deriv_xx_value_space,
        deriv_xy_value_space,
        deriv_yy_value_space,
        normal_deriv_moment_space,
    ) = argyris.emb.fes_conformity.components

    gfu_val = GridFunction(vertex_value_space)
    gfu_dx = GridFunction(deriv_x_value_space)
    gfu_dy = GridFunction(deriv_y_value_space)
    gfu_dxx = GridFunction(deriv_xx_value_space)
    gfu_dxy = GridFunction(deriv_xy_value_space)
    gfu_dyy = GridFunction(deriv_yy_value_space)
    # gfu_dn = GridFunction(normal_deriv_moment_space)

    gfu_val.Interpolate(cf)
    gfu_dx.Interpolate(cf.Diff(x))
    gfu_dy.Interpolate(cf.Diff(y))
    gfu_dxx.Interpolate(cf.Diff(x).Diff(x))
    gfu_dxy.Interpolate(cf.Diff(x).Diff(y))
    gfu_dyy.Interpolate(cf.Diff(y).Diff(y))
    # gfu_dn.Set(CF((cf.Diff(x), cf.Diff(y))), BND)

    idx = 0
    for gfu in [
        gfu_val,
        gfu_dx,
        gfu_dy,
        gfu_dxx,
        gfu_dxy,
        gfu_dyy,
    ]:  # , gfu_dn]:
        gfu_global.vec.data[idx : idx + len(gfu.vec)] = gfu.vec
        idx += len(gfu.vec)

    if dirichlet_only:
        for i in range(argyris.ndof):
            if argyris.FreeDofs()[i]:
                gfu_global.vec.data[i] = 0.0
    return gfu_global
