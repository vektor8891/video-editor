#!/usr/bin/env python

import pandas as pd
import pytest

import editor.dataframe as d


def test_has_column():
    df = pd.DataFrame(data={"Col": ["Value"]})
    # it should return True if column exist
    assert d.has_column(df, "Col")
    # it should return False if column doesn't exist
    assert not d.has_column(df, "Unknown")
    # it should throw error if column is missing and error flag is on
    with pytest.raises(ValueError) as context_info:
        d.has_column(df, "Unknown", True)
    assert "Column 'Unknown' not found" in str(context_info.value)


def test_read_clips_data(tmp_path):
    f_name = "test.csv"
    f_path = tmp_path / f_name
    df = pd.DataFrame(data={"Col": ["A"]})
    df.to_csv(f_path, index=False)
    assert d.read_clips_data(tmp_path, f_name).equals(df)


def test_get_clip_data():
    # it should raise error if 'Id' column is missing
    with pytest.raises(ValueError) as context_info:
        d.get_clip_data(pd.DataFrame(), 1)
    assert "Column 'Id' not found" in str(context_info.value)
    # it should raise error if ID is missing
    with pytest.raises(ValueError) as context_info:
        d.get_clip_data(pd.DataFrame(data={'Id': [0]}), 1)
    assert "Clip ID 1 not found!" in str(context_info.value)
    # it should raise error if IDs are not unique
    with pytest.raises(ValueError) as context_info:
        d.get_clip_data(pd.DataFrame(data={'Id': [1, 1]}), 1)
    assert "Multiple clips found with ID 1!" in str(context_info.value)
    # it should return clip data
    df = pd.DataFrame(data={'Id': [1], 'Col': ['Value']})
    assert d.get_clip_data(df, 1).equals(df.iloc[0])
