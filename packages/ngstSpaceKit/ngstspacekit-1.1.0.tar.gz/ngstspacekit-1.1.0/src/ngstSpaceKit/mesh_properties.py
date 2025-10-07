from collections.abc import Iterable

from ngsolve import ET, Mesh


def mesh_consists_of_element_type(
    mesh: Mesh, element_type: ET | Iterable[ET]
) -> bool:
    """
    Checks, if the given mesh only has elements of type element_type.
    """
    if isinstance(element_type, ET):
        element_type = [element_type]

    return not any(
        element.type not in element_type for element in mesh.Elements()
    )


def throw_on_wrong_mesh_eltype(
    mesh: Mesh, supported_element_type: ET | Iterable[ET]
) -> None:
    """
    Raises a ValueError, if the mesh contains unsupported element types.
    """
    if not mesh_consists_of_element_type(mesh, supported_element_type):
        raise ValueError(
            f"The given mesh shall only consist of elements of type {supported_element_type}. The mesh contains unsupported element types."
        )


def throw_on_wrong_mesh_dimension(mesh: Mesh, dim: int | Iterable[int]) -> None:
    """
    Raises a ValueError, if the mesh has the wrong dimension.
    """
    if isinstance(dim, int):
        dim = [dim]

    if mesh.dim not in dim:
        raise ValueError(
            f"The mesh has dimension {mesh.dim}, but dimension {dim} is required."
        )
