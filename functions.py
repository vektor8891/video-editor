import os
import re


def get_video_file(video_id: int):
    files = os.listdir('input/regi')
    for f in files:
        try:
            video_index = int(re.split(' |-', f)[0])
        except ValueError:
            video_index = None
        if video_index == video_id:
            return f
    raise ValueError(f'Video #{video_id} not found.')


def get_sec(time_str: str):
    h = 0
    if len(time_str.split(':')) == 3:
        m, s, f = time_str.split(':')
    elif len(time_str.split(':')) == 4:
        h, m, s, f = time_str.split(':')
    sec_float = int(h) * 3600 + int(m) * 60 + int(s) + int(f) / 30
    return round(sec_float, ndigits=2)
