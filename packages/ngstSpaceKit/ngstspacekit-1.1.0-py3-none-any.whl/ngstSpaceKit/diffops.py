import ngsolve
from ngsolve import CF, CoefficientFunction, Trace, x, y, z
from ngsolve.meshes import NgException


def grad(
    f: CoefficientFunction, meshdim: int | None = None
) -> CoefficientFunction:
    """
    First tries `ngsolve.grad(f)`. If that fails, symbolic differentiation will be tried. For that, a mesh dimension is needed.
    """
    try:
        return ngsolve.grad(f)
    except NgException:
        assert meshdim is not None, "Please provide a mesh dimension"
        return CF(tuple(f.Diff(coord) for coord in [x, y, z][:meshdim]))


def div(f: CoefficientFunction) -> CoefficientFunction:
    """
    First tries `ngsolve.div(f)`. If that fails, symbolic differentiation will be tried. For that, a mesh dimension is needed.
    """
    try:
        return ngsolve.div(f)
    except AttributeError:
        return CF(
            sum(f[i].Diff(coord) for i, coord in enumerate([x, y, z][: f.dim]))
        )


def hesse(f: CoefficientFunction) -> CoefficientFunction:
    """
    Hesse matrix of a function.
    """
    return f.Operator("hesse")


def laplace(f: CoefficientFunction) -> CoefficientFunction:
    """
    Laplace operator on a function that is scalar or vector valued.
    """
    try:
        f_hesse = hesse(f)
    except NgException:
        # fall back to symbolic differentiation
        if len(f.shape) == 0:
            return CF(sum(f.Diff(coord).Diff(coord) for coord in [x, y, z]))
        elif len(f.shape) == 1:
            return CF(
                tuple(
                    sum(f[i].Diff(coord).Diff(coord) for coord in [x, y, z])
                    for i in range(f.dim)
                )
            )
        else:
            raise ValueError("The function f is not scalar or vector valued.")

    if len(f.shape) == 0:
        # f is scalar valued
        return Trace(f_hesse)
    elif len(f.shape) == 1:
        # f is vector valued

        # see explanitory comment below
        dim = int(f_hesse.shape[1] ** 0.5)
        return CF(
            tuple(
                # f_hesse[j,:] == f[j].Operator("hesse")
                # it would be nicer to sum over all diagonal indices f_hesse[j, i, i] for i in range (dim),
                # but ngsolve ravels dim. 2 and 3 into one dimension, so
                # (i,i) -> i*dim + i
                sum(f_hesse[j, i] for i in range(0, dim * dim, dim + 1))
                for j in range(dim)
            )
        )
    else:
        raise ValueError("The function f is not scalar or vector valued.")


def del_x(f: CoefficientFunction) -> CoefficientFunction:
    """
    partial derivative in first coordinate direction
    """
    return grad(f)[0]


def del_y(f: CoefficientFunction) -> CoefficientFunction:
    """
    partial derivative in second coordinate direction
    """
    return grad(f)[1]


def del_z(f: CoefficientFunction) -> CoefficientFunction:
    """
    partial derivative in third coordinate direction
    """
    return grad(f)[2]


def del_xx(f: CoefficientFunction) -> CoefficientFunction:
    """
    partial derivative of second order, in first and first coordinate direction
    """
    return hesse(f)[0, 0]


def del_xy(f: CoefficientFunction) -> CoefficientFunction:
    """
    partial derivative of second order, in first and second coordinate direction
    """
    return hesse(f)[0, 1]


def del_yy(f: CoefficientFunction) -> CoefficientFunction:
    """
    partial derivative of second order, in second and second coordinate direction
    """
    return hesse(f)[1, 1]
