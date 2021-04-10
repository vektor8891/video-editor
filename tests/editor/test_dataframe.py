#!/usr/bin/env python

import pandas as pd
import pytest

import editor.dataframe as d


def test_has_column():
    df = pd.DataFrame(columns=["Col"])
    sr = pd.Series(name='Col')
    sr_multi = pd.Series(data={"Col1": ['A'], "Col2": ['B']})
    # it should return True if column exist
    assert d.has_column(df, "Col")
    assert d.has_column(sr, "Col")
    assert d.has_column(sr_multi, "Col1")
    # it should return False if column doesn't exist
    assert not d.has_column(df, "Unknown")
    assert not d.has_column(sr, "Unknown")
    # it should throw error if column is missing and error flag is on
    with pytest.raises(ValueError) as context_info:
        d.has_column(df, "Unknown", True)
    assert "Column 'Unknown' not found" in str(context_info.value)
    with pytest.raises(ValueError) as context_info:
        d.has_column(sr, "Unknown", True)
    assert "Column 'Unknown' not found" in str(context_info.value)


def test_has_columns():
    df = pd.DataFrame(columns=['Name', 'Age'])
    # it should return True if every column exist
    assert d.has_columns(df, ["Name", "Age"])
    # it should return False if any column is missing
    assert not d.has_columns(df, ["Name", "Unknown"])
    # it should throw error if any column is missing and error flag is on
    with pytest.raises(ValueError) as context_info:
        d.has_columns(df, ["Name", "Unknown"], True)
    assert "Column 'Unknown' not found" in str(context_info.value)


def test_has_duplicates():
    df = pd.DataFrame(data={"Name": ["Alex", "Eve"], "Age": [12, 14]})
    assert not d.has_duplicates(df, "Name", raise_error=True)
    df_duplicate = df.copy().append(df)
    with pytest.raises(ValueError) as context_info:
        d.has_duplicates(df_duplicate, "Name", raise_error=True)
    assert "Duplicates found in 'Name'" in str(context_info.value)
