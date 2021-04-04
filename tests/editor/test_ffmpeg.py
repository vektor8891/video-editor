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


def test_check_time_format():
    # it should work for correct time formats
    t_correct = '00:02:13'
    assert ff.check_time_format(t_correct)
    # it should raise error if time not formatted correctly
    t_incorrect = ['4:5', '0:23:12', '00:99:99']
    for t in t_incorrect:
        with pytest.raises(ValueError) as context_info:
            ff.check_time_format(t)
        assert f"Incorrect time format: '{t}'" in str(context_info.value)


def test_trim_video_cmd(tmp_path):
    f_missing = tmp_path / 'unknown.txt'
    # it should raise error if videos file doesn't exist
    with pytest.raises(ValueError) as context_info:
        ff.trim_video_cmd(f_missing, '', '', '')
    assert "Input file does not exist" in str(context_info.value)
    # it should raise error if videos file has invalid extension
    f_bad = tmp_path / 'test.avi'
    os.mknod(f_bad)
    with pytest.raises(ValueError) as context_info:
        ff.trim_video_cmd(f_bad, '', '', '')
    assert "Unknown extension: 'avi'" in str(context_info.value)
    # it should raise error if output file has invalid extension
    f_in = tmp_path / 'test_in.mp4'
    f_bad = tmp_path / 'test.mov'
    os.mknod(f_in)
    with pytest.raises(ValueError) as context_info:
        ff.trim_video_cmd(f_in, f_bad, '', '')
    assert "Unknown extension: 'mov'" in str(context_info.value)
    # it should raise error if starting time stamp has incorrect format
    f_out = tmp_path / 'test_out.mp4'
    os.mknod(f_out)
    t_bad = "4:5"
    with pytest.raises(ValueError) as context_info:
        ff.trim_video_cmd(f_in, f_out, t_bad, '')
    assert "Incorrect time format: '4:5'" in str(context_info.value)
    # it should raise error if ending time stamp has incorrect format
    t_start = '00:12:56'
    with pytest.raises(ValueError) as context_info:
        ff.trim_video_cmd(f_in, f_out, t_start, t_bad)
    assert "Incorrect time format: '4:5'" in str(context_info.value)
    # it should raise error if ending time is before ending time
    t_end = '00:15:56'
    with pytest.raises(ValueError) as context_info:
        ff.trim_video_cmd(f_in, f_out, t_end, t_start)
    assert f"Ending time ({t_start}) is after start time ({t_end})" in\
           str(context_info.value)
    # it should return command if everything is correct
    assert ff.trim_video_cmd(f_in, f_out, t_start, t_end) == \
           f'ffmpeg -ss {t_start} -i {f_in} -t {t_end} -c copy {f_out}'
