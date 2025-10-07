# ![ngstSpaceKit](https://codeberg.org/johann-cm/ngstspacekit/raw/commit/ef2998214c4e2e5dccad57022b4e5962954250d6/assets/banner.png)

[![documentation](https://img.shields.io/badge/ngstSpaceKit-documentation-blue?logo=bookstack)](https://johann-cm.codeberg.page/ngstspacekit/docs/index.html)
[![examples](https://img.shields.io/badge/ngstSpaceKit-examples-%23F37626?logo=jupyter&logoColor=%23F37626)](https://johann-cm.codeberg.page/ngstspacekit/examples/index.html)

ngstSpaceKit is an add-on to [ngsolve](https://ngsolve.org/) and [ngstrefftz](https://github.com/paulSt/ngstrefftz),
and provides a collection of finite element spaces.
The goal of this project is to explore possibilities of the conforming Trefftz Method,
and provide concrete example uses for it.

## Implemented Spaces

ngstSpaceKit implements a series of well-known finite elements,
that are not yet implemented in [ngsolve](https://ngsolve.org/):
- [Argyris](https://johann-cm.codeberg.page/ngstspacekit/docs/ngstSpaceKit.html#Argyris)
- [Bogner-Fox-Schmitt](https://johann-cm.codeberg.page/ngstspacekit/docs/ngstSpaceKit.html#BognerFoxSchmitt)
- [Crouzeix-Falk](https://johann-cm.codeberg.page/ngstspacekit/docs/ngstSpaceKit.html#CrouzeixFalk)
- [Hermite](https://johann-cm.codeberg.page/ngstspacekit/docs/ngstSpaceKit.html#HDiv)
- [Morley](https://johann-cm.codeberg.page/ngstspacekit/docs/ngstSpaceKit.html#Morley)

On top of that, there are other exotic spaces defined:
- a [weakly H1-conforming element](https://johann-cm.codeberg.page/ngstspacekit/docs/ngstSpaceKit.html#WeakH1),
  with the option to use the inner dofs with an embedded Trefftz formulation
- an [H(div)-conforming element](https://johann-cm.codeberg.page/ngstspacekit/docs/ngstSpaceKit.html#HDiv),
  with the option to use the inner dofs with an embedded Trefftz formulation
- a [Stokes mixed element](https://johann-cm.codeberg.page/ngstspacekit/docs/ngstSpaceKit.html#WeakStokes),
  where the velocity part is weakly H(div)-conforming, and the remaining dofs adhering to a Stokes embedded Trefftz formulation
- a P1 / Q1 [Immersed Finite Element Space](https://johann-cm.codeberg.page/ngstspacekit/docs/ngstSpaceKit.html#ImmersedP1FE),
  which is suitable
  to solve interface problems on a domain with a cut.
  Refer to [Lin et al.](https://doi.org/10.1137/130912700) for a proper introduction of the
  Immersed Finite Element method.

For demonstration purposes, there are some spaces implemented,
which already have a native [ngsolve](https://ngsolve.org/) implementation:
- [Brezzi-Douglas-Marini](https://johann-cm.codeberg.page/ngstspacekit/docs/ngstSpaceKit/demo.html#BDM)
- [Crouzeix-Raviart](https://johann-cm.codeberg.page/ngstspacekit/docs/ngstSpaceKit/demo.html#CrouzeixRaviart)

## Citing
ngstSpaceKit is published on Zenodo. You may cite it as
> Meyer, J. C., & Lehrenfeld, C. (2025). ngstSpaceKit. Zenodo. <https://doi.org/10.5281/zenodo.17281221>

## License

ngstSpaceKit is available under the [LGPL-3.0](./LICENSE) license.
