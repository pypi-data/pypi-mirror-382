"""
Geode-SimplexGeosciences Python binding for model
"""
from __future__ import annotations
import geode_common.bin.geode_common_py_metric
import opengeode.bin.opengeode_py_model
import opengeode_geosciences.bin.opengeode_geosciences_py_explicit
__all__: list[str] = ['SimplexGeosciencesModelLibrary', 'structural_model_simplex_remesh']
class SimplexGeosciencesModelLibrary:
    @staticmethod
    def initialize() -> None:
        ...
def structural_model_simplex_remesh(arg0: opengeode_geosciences.bin.opengeode_geosciences_py_explicit.StructuralModel, arg1: geode_common.bin.geode_common_py_metric.Metric3D) -> tuple[opengeode_geosciences.bin.opengeode_geosciences_py_explicit.StructuralModel, opengeode.bin.opengeode_py_model.ModelCopyMapping]:
    ...
