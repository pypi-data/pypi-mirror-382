import pytest
import pandas as pd
from fairml_datasets.processing.datasets import (
    binarize_column,
    parse_feature_column_filter,
)


def test_binarize_column_direct_match():
    column = pd.Series(["a", "b", "a", "c"])
    condition = "a"
    result = binarize_column(column, condition)
    expected = pd.Series([1, 0, 1, 0])
    pd.testing.assert_series_equal(result, expected)


def test_binarize_column_list_match():
    column = pd.Series(["a", "b", "a", "c"])
    condition = "a,b"
    result = binarize_column(column, condition)
    expected = pd.Series([1, 1, 1, 0])
    pd.testing.assert_series_equal(result, expected)


def test_binarize_column_greater_than():
    column = pd.Series([1, 2, 3, 4])
    condition = ">2"
    result = binarize_column(column, condition)
    expected = pd.Series([0, 0, 1, 1])
    pd.testing.assert_series_equal(result, expected)


def test_binarize_column_greater_than_equal():
    column = pd.Series([1, 2, 3, 4])
    condition = ">=3"
    result = binarize_column(column, condition)
    expected = pd.Series([0, 0, 1, 1])
    pd.testing.assert_series_equal(result, expected)


def test_binarize_column_less_than():
    column = pd.Series([1, 2, 3, 4])
    condition = "<3"
    result = binarize_column(column, condition)
    expected = pd.Series([1, 1, 0, 0])
    pd.testing.assert_series_equal(result, expected)


def test_binarize_column_less_than_equal():
    column = pd.Series([1, 2, 3, 4])
    condition = "<=2"
    result = binarize_column(column, condition)
    expected = pd.Series([1, 1, 0, 0])
    pd.testing.assert_series_equal(result, expected)


def test_binarize_column_direct_match_despite_syntax():
    column = pd.Series(["1", "2", ">=3", "4"])
    condition = ">=3"
    result = binarize_column(column, condition)
    expected = pd.Series([0, 0, 1, 0])
    pd.testing.assert_series_equal(result, expected)


def test_binarize_column_range():
    column = pd.Series([1, 2, 3, 4])
    condition = "2-3"
    result = binarize_column(column, condition)
    expected = pd.Series([0, 1, 1, 0])
    pd.testing.assert_series_equal(result, expected)


def test_binarize_column_strip_strings():
    column = pd.Series([" a ", " b ", " a ", " c "])
    condition = "a"
    result = binarize_column(column, condition)
    expected = pd.Series([1, 0, 1, 0])
    pd.testing.assert_series_equal(result, expected)


def test_binarize_column_no_match():
    column = pd.Series(["a", "b", "a", "c"])
    condition = "d"
    with pytest.raises(ValueError):
        binarize_column(column, condition)


def test_binarize_column_invalid_condition():
    column = pd.Series([1, 2, 3, 4])
    condition = "invalid"
    with pytest.raises(ValueError):
        binarize_column(column, condition)


def test_parse_feature_column_filter_all_columns():
    all_columns = {"col1", "col2", "col3", "col4"}
    target_column = {"col1"}
    sensitive_columns = {"col2"}
    filter = "-"
    result = parse_feature_column_filter(
        all_columns, target_column, sensitive_columns, filter
    )
    expected = {"col2", "col3", "col4"}
    assert result == expected


def test_parse_feature_column_filter_exclude_columns():
    all_columns = {"col1", "col2", "col3", "col4"}
    target_column = {"col1"}
    sensitive_columns = {"col2"}
    filter = "-col3;col4"
    result = parse_feature_column_filter(
        all_columns, target_column, sensitive_columns, filter
    )
    expected = {"col2"}
    assert result == expected


def test_parse_feature_column_filter_include_columns():
    all_columns = {"col1", "col2", "col3", "col4"}
    target_column = {"col1"}
    sensitive_columns = {"col2"}
    filter = "col3;col4"
    result = parse_feature_column_filter(
        all_columns, target_column, sensitive_columns, filter
    )
    expected = {"col3", "col4"}
    assert result == expected


def test_parse_feature_column_filter_empty_filter():
    all_columns = {"col1", "col2", "col3", "col4"}
    target_column = {"col1"}
    sensitive_columns = {"col2"}
    filter = ""
    result = parse_feature_column_filter(
        all_columns, target_column, sensitive_columns, filter
    )
    expected = {"col3", "col4"}
    assert result == expected


def test_parse_feature_column_filter_unknown_target_column():
    all_columns = {"col1", "col2", "col3", "col4"}
    target_column = {"col5"}
    sensitive_columns = {"col2"}
    filter = "-"
    with pytest.raises(AssertionError):
        parse_feature_column_filter(
            all_columns, target_column, sensitive_columns, filter
        )


def test_parse_feature_column_filter_unknown_sensitive_column():
    all_columns = {"col1", "col2", "col3", "col4"}
    target_column = {"col1"}
    sensitive_columns = {"col5"}
    filter = "-"
    with pytest.raises(AssertionError):
        parse_feature_column_filter(
            all_columns, target_column, sensitive_columns, filter
        )


def test_parse_feature_column_filter_unknown_feature_column():
    all_columns = {"col1", "col2", "col3", "col4"}
    target_column = {"col1"}
    sensitive_columns = {"col2"}
    filter = "col5"
    with pytest.raises(AssertionError):
        parse_feature_column_filter(
            all_columns, target_column, sensitive_columns, filter
        )


def test_parse_feature_column_filter_no_feature_columns_selected():
    all_columns = {"col1", "col2", "col3", "col4"}
    target_column = {"col1"}
    sensitive_columns = {"col2"}
    filter = "-col2;col3;col4"
    with pytest.raises(AssertionError):
        parse_feature_column_filter(
            all_columns, target_column, sensitive_columns, filter
        )
