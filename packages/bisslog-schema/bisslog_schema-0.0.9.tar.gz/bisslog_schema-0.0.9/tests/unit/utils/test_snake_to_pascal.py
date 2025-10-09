import pytest

from bisslog_schema.utils.snake_to_pascal_case import snake_to_pascal

@pytest.mark.parametrize("input_str, expected", [
    ("snake_case", "SnakeCase"),
    ("multiple_words_here", "MultipleWordsHere"),
    ("already_pascal", "AlreadyPascal"),
    ("single", "Single"),
    ("", ""),
    ("_leading", "Leading"),
    ("trailing_", "Trailing"),
    ("__double__", "Double"),
    ("with__double__underscores", "WithDoubleUnderscores"),
    ("with_numbers_123", "WithNumbers123"),
])
def test_snake_to_pascal(input_str, expected):
    assert snake_to_pascal(input_str) == expected
