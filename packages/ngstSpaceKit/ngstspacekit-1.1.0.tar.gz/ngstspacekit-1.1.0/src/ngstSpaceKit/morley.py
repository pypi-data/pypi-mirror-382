from dataclasses import dataclass

import ngsolve
from ngsolve import (
    BBND,
    BND,
    H1,
    L2,
    TRIG,
    NormalFacetFESpace,
    dx,
    grad,
    specialcf,
)
from ngstrefftz import EmbeddedTrefftzFES, L2EmbTrefftzFESpace, TrefftzEmbedding

from ngstSpaceKit.mesh_properties import (
    throw_on_wrong_mesh_dimension,
    throw_on_wrong_mesh_eltype,
)


@dataclass
class MorleyDirichlet:
    """
    Holds the dirichlet instructions for every type of dof in the `Morley` space separately.
    """

    vertex_value: str = ""
    normal_deriv: str = ""

    @classmethod
    def clamp(cls, bnd: str) -> "MorleyDirichlet":
        """
        `bnd`: boundary where clamp conditions shall be set.
        """
        return cls(vertex_value=bnd, normal_deriv=bnd)


def Morley(
    mesh: ngsolve.comp.Mesh,
    dirichlet: str | MorleyDirichlet = "",
    check_mesh: bool = True,
    stats: dict | None = None,
) -> L2EmbTrefftzFESpace:
    r"""
    Implementation of the Morley element.

    `dirichlet`: if you provide a string, it will set dirichlet conditions only for vertex value dofs. For more control, use `MorleyDirichlet`.

    `check_mesh`: test, if the `mesh` is compatible with this space

    `stats`: use the `stats` flag of the `TrefftzEmbeddin` method

    # Raises
    - ValueError, if the mesh is not 2D
    - ValueError, if the mesh is not triangular

    # Conforming Trefftz Formulation
    - $\mathbb{V}_h := \mathbb{P}^{2, \text{disc}}(\mathcal{T}_h)$
    - $\mathbb{Z}_h := \mathbb{P}^{1}(\mathcal{T}_h) \times \mathbb{P}^{0}(\mathcal{F}_h)$
    - \begin{align}
      \mathcal{C}_K(v_h, (z_h^\text{vertex}, z_h^\text{facet})) &:=
          \sum_{p \text{ is vertex}} v_h(p) z_h^\text{vertex}(p)
          + \int_{\partial K} v_h z_h^\text{facet} dx, \\\\
      \mathcal{D}_K((y_h^\text{vertex}, y_h^\text{facet}), (z_h^\text{vertex}, z_h^\text{facet})) &:=
          \sum_{p \text{ is vertex}} y_h^\text{veretx}(p) z_h^\text{vertex}(p)
          + \int_{\partial K} y_h^\text{facet} z_h^\text{facet} dx
      \end{align}
    """
    if check_mesh:
        throw_on_wrong_mesh_dimension(mesh, 2)
        throw_on_wrong_mesh_eltype(mesh, TRIG)

    dirichlet_struct = (
        MorleyDirichlet(vertex_value=dirichlet)
        if type(dirichlet) is str
        else dirichlet
    )
    assert type(dirichlet_struct) is MorleyDirichlet

    fes = L2(mesh, order=2)

    vertex_value_space = H1(
        mesh, order=1, dirichlet=dirichlet_struct.vertex_value
    )
    normal_deriv_moment_space = NormalFacetFESpace(
        mesh, order=0, dirichlet=dirichlet_struct.normal_deriv
    )

    conformity_space = vertex_value_space * normal_deriv_moment_space

    u = fes.TrialFunction()
    (u_, u_n) = conformity_space.TrialFunction()
    (v_, v_n) = conformity_space.TestFunction()

    dVertex = dx(element_vb=BBND)
    dFace = dx(element_vb=BND)
    n = specialcf.normal(2)

    cop_lhs = u * v_ * dVertex + grad(u) * n * v_n * n * dFace
    cop_rhs = u_ * v_ * dVertex + u_n * n * v_n * n * dFace

    embedding = TrefftzEmbedding(
        cop=cop_lhs,
        crhs=cop_rhs,
        ndof_trefftz=0,
        stats=stats,
    )

    morley = EmbeddedTrefftzFES(embedding)
    assert type(morley) is L2EmbTrefftzFESpace, (
        "The morley space should always be an L2EmbTrefftzFESpace"
    )

    return morley
