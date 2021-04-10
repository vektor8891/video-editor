#!/usr/bin/env python

import subprocess as s
import os
import re

from typing import Tuple, Union

VALID_EXTENSIONS = ['mp4']


def run_command(cmd: str) -> str:
    process = s.Popen(cmd, shell=True, stdout=s.PIPE, stderr=s.PIPE)
    output, error = process.communicate()
    if error != b'':
        error_str = error.decode("utf-8")
        if not error_str.startswith("ffmpeg version"):
            raise ValueError(error_str)
    return output.decode("utf-8").strip()


def check_existing_file(f_path: Union[os.PathLike, str]) -> bool:
    if not os.path.isfile(f_path):
        raise ValueError(f'Input file does not exist: {f_path}')
    return True


def delete_existing_file(f_path: Union[os.PathLike, str]) -> bool:
    is_file = os.path.isfile(f_path)
    if is_file:
        os.remove(f_path)
    return is_file


def check_extension(f_path: Union[os.PathLike, str]) -> bool:
    f_name, f_ext = os.path.splitext(f_path)
    f_ext_lower = f_ext.lower()[1:]
    if f_ext_lower not in VALID_EXTENSIONS:
        valid_ext = ",".join(VALID_EXTENSIONS)
        raise ValueError(f"Unknown extension: '{f_ext_lower}' (valid "
                         f"extensions: [{valid_ext}]")
    return True


def get_video_length_cmd(f_path: Union[os.PathLike, str]) -> str:
    check_existing_file(f_path)
    cmd = f'ffprobe -i {f_path} -show_entries format=duration -v quiet ' \
          f'-of csv="p=0"'
    return cmd


def get_video_length(f_path: Union[os.PathLike, str]) -> float:
    cmd = get_video_length_cmd(f_path)
    output = run_command(cmd)
    video_length = round(float(output if output != '' else 0), 2)
    return video_length


def get_seconds(time_str: str) -> int:
    if re.match(r'^\d\d:[0-5]\d:[0-5]\d$', time_str):
        h, m, s = time_str.split(':')
        return int(h) * 3600 + int(m) * 60 + int(s)
    else:
        raise ValueError(f"Incorrect time format: '{time_str}' (valid time "
                         f"format: HH:MM:SS)")


def check_time_stamps(f_in: Union[os.PathLike, str], t_start: str,
                      t_end: str) -> bool:
    sec_start = get_seconds(t_start)
    sec_end = get_seconds(t_end)
    sec_total = get_video_length(f_in)
    if sec_start > sec_end:
        raise ValueError(f"Ending time ({t_end}) is after start time ("
                         f"{t_start})")
    if sec_end > sec_total:
        raise ValueError(f"Ending time ({t_end}) is longer then video length ("
                         f"{f_in} - {sec_total} s)")
    return True


def trim_video_cmd(f_in: Union[os.PathLike, str], f_out: Union[os.PathLike, str],
                   t_start: str, t_end: str) -> str:
    check_existing_file(f_in)
    delete_existing_file(f_out)
    check_extension(f_in)
    check_extension(f_out)
    check_time_stamps(f_in, t_start, t_end)
    return f'ffmpeg -ss {t_start} -i {f_in} -t {t_end} -c copy {f_out}'


def merge_videos_cmd(files_path: str, f_out: str) -> str:
    check_existing_file(files_path)
    delete_existing_file(f_out)
    return f'ffmpeg -f concat -safe 0 -i {files_path} -c copy {f_out}'
