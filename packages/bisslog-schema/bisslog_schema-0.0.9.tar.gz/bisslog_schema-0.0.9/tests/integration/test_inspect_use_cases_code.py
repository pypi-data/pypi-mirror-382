import os
import pytest

from bisslog_schema import extract_use_case_obj_from_code, extract_use_case_code_metadata
from bisslog_schema.use_case_code_inspector.use_case_code_metadata import UseCaseCodeInfo, \
    UseCaseCodeInfoObject, UseCaseCodeInfoClass


expected_use_case_module_names = ["use_case_1", "use_case_2",
                                  "use_case_3", "use_case_4", "use_case_5"]

@pytest.mark.parametrize("data_path", ["tests/integration/data/use_cases_sample",
                                       "tests.integration.data.use_cases_sample"])
def test_inspect_use_cases_code(data_path: str) -> None:
    """Test the inspection of use cases code."""

    uc_code_metadata = extract_use_case_code_metadata(data_path)
    assert len(uc_code_metadata) == 5
    for k, v in uc_code_metadata.items():
        assert k in expected_use_case_module_names
        assert isinstance(v, UseCaseCodeInfo)
        assert v.name == k
        assert v.docs is not None
        if k == "use_case_1":
            assert isinstance(v, UseCaseCodeInfoObject)
            assert v.var_name == "USE_CASE_1"
            assert not v.is_coroutine
        if k == "use_case_2":
            assert isinstance(v, UseCaseCodeInfoObject)
            assert v.var_name == "use_case_2"
            assert not v.is_coroutine
        if k == "use_case_3":
            assert isinstance(v, UseCaseCodeInfoClass)
            assert v.class_name == "UseCase3"
            assert not v.is_coroutine
        if k == "use_case_4":
            assert isinstance(v, UseCaseCodeInfoObject)
            assert v.var_name == "USE_CASE_4"
            assert not v.is_coroutine
        if k == "use_case_5":
            assert isinstance(v, UseCaseCodeInfoObject)
            assert v.var_name == "use_case_5"
            assert v.is_coroutine
    uc_objects = extract_use_case_obj_from_code(data_path)
    assert len(uc_objects) == 5
    for k, v in uc_objects.items():
        assert k in expected_use_case_module_names
        assert callable(v)
