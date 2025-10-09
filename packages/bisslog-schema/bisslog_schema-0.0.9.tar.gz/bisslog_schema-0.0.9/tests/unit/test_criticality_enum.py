from bisslog_schema.schema.enums.criticality import CriticalityEnum


def test_get_from_int_val_invalid():
    """
    Test that get_from_int_val returns None if the integer value does not correspond to any enum member.
    """
    assert CriticalityEnum.get_from_int_val(999) is None  # Invalid value


def test_cache_usage():
    """
    Test that the cache is used after the first call for a given value.
    """
    # First call (not cached yet)
    CriticalityEnum.get_from_int_val(50)

    # Check if the cache has been populated by checking the cache attribute
    assert hasattr(CriticalityEnum, "_cache_val")
    assert CriticalityEnum._cache_val[50] == CriticalityEnum.MEDIUM

    # Second call (should be faster due to caching)
    CriticalityEnum.get_from_int_val(50)

    # Ensure that the cache is being used by the method
    assert CriticalityEnum._cache_val[50] == CriticalityEnum.MEDIUM
