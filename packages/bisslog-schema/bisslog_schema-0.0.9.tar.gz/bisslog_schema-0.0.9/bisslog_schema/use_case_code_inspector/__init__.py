"""Code review use case module."""

from .package_tree_reader import PackageTreeReader
from .strategies.use_case_obj_module_inspector import UseCaseObjectModuleInspector
from .strategies.use_case_metadata_module_inspector import UseCaseMetadataModuleInspector

extract_use_case_code_metadata = PackageTreeReader(UseCaseMetadataModuleInspector())
extract_use_case_obj_from_code = PackageTreeReader(UseCaseObjectModuleInspector())


__all__ = ["extract_use_case_code_metadata", "extract_use_case_obj_from_code",
           "PackageTreeReader"]
