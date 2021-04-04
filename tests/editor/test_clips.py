#!/usr/bin/env python

import pandas as pd
import pytest
import os

import editor.clips as c


def test_read_clips_data(tmp_path):
    f_name = "test.csv"
    f_path = tmp_path / f_name
    df = pd.DataFrame(data={"Col": ["A"]})
    df.to_csv(f_path, index=False)
    assert c.read_clips_data(tmp_path, f_name).equals(df)


def test_get_clips():
    video_id = 1
    # it should raise error if columns are missing
    with pytest.raises(ValueError) as context_info:
        c.get_clips(pd.DataFrame(), video_id)
    assert "Column 'VideoId' not found" in str(context_info.value)
    with pytest.raises(ValueError) as context_info:
        c.get_clips(pd.DataFrame(columns=['VideoId']), video_id)
    assert "Column 'Id' not found" in str(context_info.value)
    # it should raise error if ID is missing
    with pytest.raises(ValueError) as context_info:
        c.get_clips(pd.DataFrame(columns=['VideoId', 'Id']), video_id)
    assert f"No clips found for Video ID {video_id}!" in str(
        context_info.value)
    # it should raise error if IDs are not unique
    with pytest.raises(ValueError) as context_info:
        c.get_clips(pd.DataFrame(data={
            'VideoId': [1, 1],
            'Id': [1, 1]
        }), video_id)
    assert "Duplicates found in 'Id'" in str(context_info.value)
    # it should return clip data
    df_single = pd.DataFrame(data={'Id': [1], 'VideoId': [video_id]})
    assert c.get_clips(df_single, 1).equals(df_single)
    # it should sort clips by id in case of multiple match
    df_multi = pd.DataFrame(data={
        'Id': [3, 2, 1],
        'VideoId': [video_id, video_id, video_id]})
    df_multi_sorted = df_multi.sort_values(by=['Id'])
    assert c.get_clips(df_multi, video_id).equals(df_multi_sorted)


def test_get_input_folder():
    assert c.get_input_folder() == os.path.join('data', 'videos')


def test_get_input_file_path(tmp_path, mocker):
    mocker.patch("editor.clips.get_input_folder", return_value=tmp_path)
    f_name = 'test.txt'
    f_path = tmp_path / 'raw' / f_name
    assert c.get_input_file_path(f_name) == str(f_path)


def test_get_output_file_path(tmp_path, mocker):
    mocker.patch("editor.clips.get_input_folder", return_value=tmp_path)
    f_name = 'test.txt'
    f_name_id = 'test_01.txt'
    f_path = tmp_path / 'temp' / f_name_id
    assert c.get_output_file_path(f_name, 1) == str(f_path)


def test_trim_clip(mocker):
    # it should raise error if columns are missing
    df = pd.DataFrame(data={
        'Id': [1],
        'FileName': ['test.mp4'],
        'TimeStart': ['00:00:00'],
        'TimeEnd': ['00:00:01']
    })
    for col in df.columns:
        df_missing = df.copy()
        del df_missing[col]
        with pytest.raises(ValueError) as context_info:
            c.trim_clip(df_missing.iloc[0])
        assert f"Column '{col}' not found" in str(context_info.value)
