"""
Geode-Hybrid Python binding for brep
"""
from __future__ import annotations
import geode_common.lib64.geode_common_py_metric
import opengeode.lib64.opengeode_py_model
__all__: list[str] = ['HybridBRepLibrary', 'hex_dominant_remesh']
class HybridBRepLibrary:
    @staticmethod
    def initialize() -> None:
        ...
def hex_dominant_remesh(arg0: opengeode.lib64.opengeode_py_model.BRep, arg1: geode_common.lib64.geode_common_py_metric.Metric3D) -> None:
    ...
