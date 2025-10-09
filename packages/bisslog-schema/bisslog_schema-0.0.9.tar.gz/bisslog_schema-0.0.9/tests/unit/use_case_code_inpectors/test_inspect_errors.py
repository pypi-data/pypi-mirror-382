import pytest
from bisslog_schema import extract_use_case_obj_from_code, extract_use_case_code_metadata



def test_inspect_errors_not_find_defaults():
    """
    Test the inspect_errors function.
    """

    with pytest.raises(ValueError, match="Could not find any default path for use cases."):
        extract_use_case_obj_from_code()

    with pytest.raises(ValueError, match="Could not find any default path for use cases."):
        extract_use_case_code_metadata()

@pytest.mark.parametrize("path", ["no_existent_path", "no_existent_path/another_path",
                                  "no_existend_path2.something"])
def test_inspect_errors_path_does_not_exists(path):
    with pytest.raises(
            ValueError, match=f"Path '{path}' of use cases does not exist"):
        extract_use_case_obj_from_code(path=path)

    with pytest.raises(
            ValueError, match=f"Path '{path}' of use cases does not exist"):
        extract_use_case_code_metadata(path=path)


@pytest.mark.parametrize("path", ["-invalid-path/something", "something.algo-muajaja"])
def test_inspect_errors_invalid_path(path):

    with pytest.raises(
            ValueError, match=f"Invalid path: '{path}'. Path should be a valid module or folder path."):
        extract_use_case_code_metadata(path=path)
