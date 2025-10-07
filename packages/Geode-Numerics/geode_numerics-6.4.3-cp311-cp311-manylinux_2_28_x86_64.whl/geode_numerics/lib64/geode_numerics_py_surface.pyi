"""
Geode-Numerics Python binding for surface
"""
from __future__ import annotations
import opengeode.lib64.opengeode_py_mesh
__all__: list[str] = ['NumericsSurfaceLibrary', 'compute_LSCM_parameterization', 'convert_surface3d_into_2d']
class NumericsSurfaceLibrary:
    @staticmethod
    def initialize() -> None:
        ...
def compute_LSCM_parameterization(arg0: opengeode.lib64.opengeode_py_mesh.TriangulatedSurface3D, arg1: str) -> None:
    ...
def convert_surface3d_into_2d(arg0: opengeode.lib64.opengeode_py_mesh.TriangulatedSurface3D, arg1: str) -> opengeode.lib64.opengeode_py_mesh.TriangulatedSurface2D:
    ...
