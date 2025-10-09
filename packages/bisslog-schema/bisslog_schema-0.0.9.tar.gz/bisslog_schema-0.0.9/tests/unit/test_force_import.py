
import os
import tempfile
import shutil
import textwrap
import importlib.util
import sys
import pytest

from typing import List
from bisslog_schema.eager_import_module_or_package import EagerImportModulePackage

def create_test_package(package_name: str, files: List[str]):
    temp_dir = tempfile.mkdtemp()
    package_path = os.path.join(temp_dir, package_name)
    os.makedirs(package_path)
    with open(os.path.join(package_path, "__init__.py"), "w"):
        pass
    for file in files:
        with open(os.path.join(package_path, file), "w") as f:
            f.write(textwrap.dedent("marker = True"))
    sys.path.insert(0, temp_dir)
    return temp_dir, f"{package_name}"

def test_force_import_single_module():
    temp_dir, module_name = create_test_package("testmod", ["module1.py"])
    try:
        importer = EagerImportModulePackage()
        importer(f"{module_name}.module1")
        mod = importlib.import_module(f"{module_name}.module1")
        assert hasattr(mod, "marker")
    finally:
        sys.path.remove(temp_dir)
        shutil.rmtree(temp_dir)

def test_force_import_package_recursively():
    temp_dir, package_name = create_test_package("mypkg", ["moda.py", "modb.py"])
    subpkg_path = os.path.join(temp_dir, "mypkg", "subpkg")
    os.makedirs(subpkg_path)
    with open(os.path.join(subpkg_path, "__init__.py"), "w"):
        pass
    with open(os.path.join(subpkg_path, "modsub.py"), "w") as f:
        f.write("marker = True")

    sys.path.insert(0, temp_dir)
    try:
        importer = EagerImportModulePackage()
        importer("mypkg")
        assert hasattr(importlib.import_module("mypkg.moda"), "marker")
        assert hasattr(importlib.import_module("mypkg.modb"), "marker")
        assert hasattr(importlib.import_module("mypkg.subpkg.modsub"), "marker")
    finally:
        sys.path.remove(temp_dir)
        shutil.rmtree(temp_dir)

def test_force_import_with_defaults():
    temp_dir, module_name = create_test_package("defaultpkg", ["initmod.py"])
    sys.path.insert(0, temp_dir)
    try:
        importer = EagerImportModulePackage(defaults=[f"{module_name}.initmod"])
        importer(None)
        mod = importlib.import_module(f"{module_name}.initmod")
        assert hasattr(mod, "marker")
    finally:
        sys.path.remove(temp_dir)
        shutil.rmtree(temp_dir)

def test_force_import_invalid_module():
    importer = EagerImportModulePackage()
    # do nothing
    importer("nonexistent.module")

