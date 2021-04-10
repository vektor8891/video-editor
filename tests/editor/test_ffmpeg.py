#!/usr/bin/env python

import editor.ffmpeg as ff
import pytest
import os


def test_run_command(tmp_path):
    # it should run command
    text = "Hello World"
    assert ff.run_command(f"echo {text}") == text
    # it should return error properly
    f_path = tmp_path / "unknown.txt"
    with pytest.raises(ValueError) as context_info:
        ff.run_command(f"cat {f_path}")
    assert f"{f_path}" in str(context_info.value)


def test_check_existing_file(tmp_path):
    f_missing = tmp_path / 'unknown.txt'
    # it should raise error if videos file doesn't exist
    with pytest.raises(ValueError) as context_info:
        ff.check_existing_file(f_missing)
    assert "Input file does not exist" in str(context_info.value)
    # it should return true if file exists
    f_valid = tmp_path / 'file.txt'
    os.mknod(f_valid)
    assert ff.check_existing_file(f_valid)


def test_delete_existing_file(tmp_path):
    f_missing = tmp_path / 'unknown.txt'
    # it should return false if file doesn't exist
    assert not ff.delete_existing_file(f_missing)
    # it should delete existing file and return true
    f_valid = tmp_path / 'file.txt'
    os.mknod(f_valid)
    assert ff.delete_existing_file(f_valid)
    assert not os.path.isfile(f_valid)


def test_check_extension():
    # it should work for files with valid extensions
    f_correct = os.path.join('folder', 'video.mp4')
    assert ff.check_extension(f_correct)
    # it should not be case sensitive
    f_correct_upper = os.path.join('folder', 'video.MP4')
    assert ff.check_extension(f_correct_upper)
    # it should raise error if extension is incorrect
    f_incorrect = os.path.join('folder', 'video.avi')
    with pytest.raises(ValueError) as context_info:
        ff.check_extension(f_incorrect)
    assert "Unknown extension: 'avi'" in str(context_info.value)


def test_get_video_length_cmd(mocker):
    mocker.patch("editor.ffmpeg.check_existing_file", return_value=True)
    f_path = 'test.mp4'
    cmd = f'ffprobe -i {f_path} -show_entries format=duration -v quiet ' \
          f'-of csv="p=0"'
    assert ff.get_video_length_cmd(f_path) == cmd


def test_get_video_length(mocker):
    mocker.patch("editor.ffmpeg.get_video_length_cmd", return_value='')
    mocker.patch("editor.ffmpeg.run_command", return_value=100)
    f_path = 'test.mp4'
    assert ff.get_video_length(f_path) == 100


def test_get_seconds():
    # it should work for correct time formats
    t_correct = '00:02:13'
    assert ff.get_seconds(t_correct) == 133
    # it should raise error if time not formatted correctly
    t_incorrect = ['4:5', '0:23:12', '00:99:99']
    for t in t_incorrect:
        with pytest.raises(ValueError) as context_info:
            ff.get_seconds(t)
        assert f"Incorrect time format: '{t}'" in str(context_info.value)


def test_check_time_stamps(mocker):
    mocker.patch("editor.ffmpeg.get_video_length", return_value=60)
    # it should work return true if time stamps are in order
    f_path = 'test.mp4'
    assert ff.check_time_stamps(f_path, '00:00:01', '00:00:02')
    # it should raise error if time stamps are not in order
    with pytest.raises(ValueError) as context_info:
        ff.check_time_stamps(f_path, '00:00:02', '00:00:01')
    assert "Ending time (00:00:01) is after start time (00:00:02)"\
           in str(context_info.value)
    # it should raise error if end time is too long
    with pytest.raises(ValueError) as context_info:
        ff.check_time_stamps(f_path, '00:00:00', '00:02:00')
    assert f"Ending time (00:02:00) is longer then video length " \
           f"({f_path} - 60 s)" in str(context_info.value)


def test_trim_video_cmd(mocker):
    mocker.patch("editor.ffmpeg.check_existing_file", return_value=True)
    mocker.patch("editor.ffmpeg.delete_existing_file", return_value=False)
    mocker.patch("editor.ffmpeg.check_extension", return_value=True)
    mocker.patch("editor.ffmpeg.check_time_stamps", return_value=True)
    # it should return command if everything is correct
    f_in = "in.mp4"
    f_out = "out.mp4"
    t_start = '00:12:56'
    t_end = '00:15:56'
    assert ff.trim_video_cmd(f_in, f_out, t_start, t_end) == \
           f'ffmpeg -ss {t_start} -i {f_in} -t {t_end} -c copy {f_out}'


def test_merge_videos_cmd(tmp_path, mocker):
    mocker.patch("editor.ffmpeg.check_existing_file", return_value=True)
    mocker.patch("editor.ffmpeg.delete_existing_file", return_value=False)
    # it should return command if everything is correct
    f_path = "files.txt"
    f_out = "out.mp4"
    assert ff.merge_videos_cmd(f_path, f_out) == \
           f'ffmpeg -f concat -safe 0 -i {f_path} -c copy {f_out}'
