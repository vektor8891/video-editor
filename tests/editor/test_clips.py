#!/usr/bin/env python

import pandas as pd
import pytest
import os

import editor.clips as c


def test_read_media_data(tmp_path):
    f_name = "test.csv"
    f_path = tmp_path / f_name
    df = pd.DataFrame(data={"Col": ["A"]})
    df.to_csv(f_path, index=False)
    assert c.read_media_data(tmp_path, f_name).equals(df)


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


def test_get_video(mocker):
    # it should throw error if video ids are duplicated
    df_multi = pd.DataFrame(data={'Id': [1, 1]})
    mocker.patch("editor.clips.read_media_data", return_value=df_multi)
    with pytest.raises(ValueError) as context_info:
        c.get_video(1)
    assert "Duplicates found in 'Id'" in str(context_info.value)
    # it should throw error if column is missing
    df_missing = pd.DataFrame(data={'Id': [1]})
    mocker.patch("editor.clips.read_media_data", return_value=df_missing)
    with pytest.raises(ValueError) as context_info:
        c.get_video(1, 'Missing')
    assert "Column 'Missing' not found" in str(context_info.value)
    # it should return column value
    df_single = pd.DataFrame(data={'Id': [1], 'Col': ['value']})
    mocker.patch("editor.clips.read_media_data", return_value=df_single)
    assert c.get_video(1, 'Col') == 'value'
    # it should return dataframe if column is not specified
    df_full = pd.DataFrame(data={'Id': [1], 'Col': ['value']})
    mocker.patch("editor.clips.read_media_data", return_value=df_full)
    assert c.get_video(1).equals(df_full)


def test_get_input_folder():
    assert c.get_input_folder() == os.path.join('data', 'videos')


def test_get_input_file_path(tmp_path, mocker):
    mocker.patch("editor.clips.get_input_folder", return_value=tmp_path)
    f_name = 'test.txt'
    f_path = tmp_path / f_name
    assert c.get_input_file_path(f_name) == str(f_path)
    folder_name = 'test_folder'
    f_path_folder = tmp_path / folder_name / f_name
    assert c.get_input_file_path(f_name, folder_name) == str(f_path_folder)



def test_get_output_file_path(tmp_path, mocker):
    mocker.patch("editor.clips.get_input_folder", return_value=tmp_path)
    f_name = 'test.txt'
    # it should work without suffix
    f_path = tmp_path / 'temp' / f_name
    assert c.get_output_file_path(f_name) == str(f_path)
    assert c.get_output_file_path(f_name, '') == str(f_path)
    # it should work for integers
    f_name_int = 'test_01.txt'
    f_path_int = tmp_path / 'temp' / f_name_int
    assert c.get_output_file_path(f_name, 1) == str(f_path_int)
    # it should work for strings
    f_name_sfx = 'test_suffix.txt'
    f_path_sfx = tmp_path / 'temp' / f_name_sfx
    assert c.get_output_file_path(f_name, "suffix") == str(f_path_sfx)
    # it should throw error otherwise
    with pytest.raises(ValueError) as context_info:
        c.get_output_file_path(f_name, [''])
    assert "Invalid file suffix: ['']" in str(context_info.value)


def test_trim_clip(mocker):
    mocker.patch("editor.dataframe.has_columns", return_value=True)
    mocker.patch("editor.clips.get_input_file_path", return_value='in.mp4')
    mocker.patch("editor.clips.get_output_file_path", return_value='out.mp4')
    mocker.patch("editor.ffmpeg.trim_video_cmd", return_value='cmd')
    mocker.patch("editor.ffmpeg.run_command", return_value=True)
    row = pd.Series(data={
        'Id': [0],
        'FileName': ['f'],
        'TimeStart': ['00:00:00'],
        'TimeEnd': ['00:00:01'],
    })
    assert c.trim_clip(row) == 'out.mp4'


def test_write_input_files(tmp_path):
    input_files_path = tmp_path / 'temp.txt'
    f_list = ['file1.txt', 'file2.txt']
    # it should return true with corrects parameters
    assert c.write_input_files(f_list, input_files_path)
    # it should create file
    assert os.path.isfile(input_files_path)
    # file content should match
    with open(input_files_path, 'r') as f:
        for i, line in enumerate(f.readlines()):
            assert line.strip() == f"file '{f_list[i]}'"


def test_merge_clips(mocker, tmp_path):
    f_input_list = 'list.txt'
    # create dummy input list file
    if not os.path.isfile(f_input_list):
        os.mknod(f_input_list)
    f_out = 'out.mp4'
    mocker.patch("editor.clips.write_input_files", return_value=True)
    mocker.patch("editor.clips.get_video", return_value=True)
    mocker.patch("editor.clips.get_output_file_path", return_value=f_out)
    mocker.patch("editor.ffmpeg.merge_videos_cmd", return_value='cmd')
    mocker.patch("editor.ffmpeg.run_command", return_value=True)
    # it should return output file name
    assert c.merge_clips([], 1, f_input_list) == f_out
    # it should delete input list file
    assert not os.path.isfile(f_input_list)


def test_add_audio(mocker):
    f_out = 'out.mp4'
    mocker.patch("editor.clips.get_video", return_value=f_out)
    mocker.patch("editor.clips.get_output_file_path", return_value=f_out)
    mocker.patch("editor.ffmpeg.add_audio_cmd", return_value='cmd')
    mocker.patch("editor.ffmpeg.run_command", return_value=True)
    mocker.patch("editor.ffmpeg.delete_existing_file", return_value=True)
    assert c.add_audio('in.mp4', 1) == f_out


def test_add_intro_outro(mocker):
    f_out = 'out.mp4'
    mocker.patch("editor.clips.get_input_file_path", return_value=f_out)
    mocker.patch("editor.clips.merge_clips", return_value=f_out)
    assert c.add_intro_outro('in.mp4', 1) == f_out
