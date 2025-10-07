from ngsolve import (
    COUPLING_TYPE,
    H1,
    Compress,
    FESpace,
    Mesh,
)


def VertexBubble(mesh: Mesh, dirichlet: str = "") -> FESpace:
    """
    The `VertexBubble` space is a standard `ngsolve.comp.H1` space of order 1.
    """
    return H1(mesh, order=1, dirichlet=dirichlet)


def EdgeBubble(mesh: Mesh, order: int, dirichlet: str = "") -> FESpace:
    """
    The `EdgeBubble` space only contains the edge bubble basis functions
    of the standard `ngsolve.comp.H1` space with order `order`.

    # Raises
    `ValueError`, if `order < 2`. There are no edge bubbles of order 1 or less.
    """
    if order < 2:
        raise ValueError("order must be >= 2")

    bubble = H1(mesh, order=order, dirichlet=dirichlet)
    for dofNr in range(bubble.ndof):
        bubble.SetCouplingType(dofNr, COUPLING_TYPE.UNUSED_DOF)

    for edge in mesh.edges:
        for dof in bubble.GetDofNrs(edge):
            bubble.SetCouplingType(dof, COUPLING_TYPE.INTERFACE_DOF)
    return Compress(bubble)


def VolumeBubble(mesh: Mesh, order: int) -> FESpace:
    """
    The `VolumeBubble` space only contains the volume bubble basis functions
    of the standard `ngsolve.comp.H1` space with order `order`.

    # Raises
    `ValueError`, if `order < 3`. There are no volume bubbles of order 2 or less.
    """
    if order < 3:
        raise ValueError("order must be >= 2")

    bubble = H1(mesh, order=order)
    for dof in range(bubble.ndof):
        if bubble.CouplingType(dof) != COUPLING_TYPE.LOCAL_DOF:
            bubble.SetCouplingType(dof, COUPLING_TYPE.UNUSED_DOF)
    return Compress(bubble)
