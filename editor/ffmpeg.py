#!/usr/bin/env python

import subprocess as s
import os
import re

from typing import Tuple, Union

VALID_EXTENSIONS = ['mp4']


def run_command(cmd: str) -> Tuple[str, str]:
    process = s.Popen(cmd.split(), stdout=s.PIPE, stderr=s.PIPE)
    output, error = process.communicate()
    return output.decode("utf-8").strip(), error.decode("utf-8")


def check_extension(f_path: Union[os.PathLike, str]) -> bool:
    f_name, f_ext = os.path.splitext(f_path)
    f_ext_lower = f_ext.lower()[1:]
    if f_ext_lower not in VALID_EXTENSIONS:
        valid_ext = ",".join(VALID_EXTENSIONS)
        raise ValueError(f"Unknown extension: '{f_ext_lower}' (valid "
                         f"extensions: [{valid_ext}]")
    return True


def check_time_format(t_str: str):
    if not re.match(r'^\d\d:[0-5]\d:[0-5]\d$', t_str):
        raise ValueError(f"Incorrect time format: '{t_str}' (valid time "
                         f"format: HH:MM:SS)")
    return True


def trim_video_cmd(f_in: Union[os.PathLike, str], f_out: Union[os.PathLike, str],
                   t_start: str, t_end: str):
    if not os.path.isfile(f_in):
        raise ValueError(f'Input file does not exist: {f_in}')
    check_extension(f_in)
    check_extension(f_out)
    check_time_format(t_start)
    check_time_format(t_end)
    if int(t_start.replace(':', '')) > int(t_end.replace(':', '')):
        raise ValueError(f"Ending time ({t_end}) is after start time ("
                         f"{t_start})")
    return f'ffmpeg -ss {t_start} -i {f_in} -t {t_end} -c copy {f_out}'
