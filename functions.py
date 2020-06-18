import moviepy.editor as movie
import os
import re
import pandas as pd

# open current directory
os.chdir(os.path.dirname(os.path.realpath(__file__)))

global videos

videos = pd.read_excel('videos.xlsx')
clip_intro = movie.VideoFileClip('input/intro.mp4')
clip_action = movie.VideoFileClip('input/call-to-action-up.mp4')
clip_outro = movie.VideoFileClip('input/outro.mp4')


def get_video_path(video_id: int):
    files = os.listdir('input/regi')
    for f_path in files:
        try:
            video_index = int(re.split(' |-', f_path)[0])
        except ValueError:
            video_index = None
        if video_index == video_id:
            return f'input/regi/{f_path}'
    raise ValueError(f'Video #{video_id} not found.')


def get_sec(time_str: str):
    h = m = s = f = 0
    if len(time_str.split(':')) == 3:
        m, s, f = time_str.split(':')
    elif len(time_str.split(':')) == 4:
        h, m, s, f = time_str.split(':')
    sec_float = int(h) * 3600 + int(m) * 60 + int(s) + int(f) / 30
    return round(sec_float, ndigits=2)


def trim_video_clip(video_id: int, clip_id: int, clip_path: str):
    videos.Start = videos.Start.astype(str)
    videos.End = videos.End.astype(str)
    video_path = get_video_path(video_id=video_id)
    video = videos[videos.Id == video_id]
    start_str = video.Start.values[0].split('\n')[clip_id]
    end_str = video.End.values[0].split('\n')[clip_id]
    start = get_sec(start_str)
    end = get_sec(end_str)
    trimmed_clip = movie.VideoFileClip(video_path).subclip(start, end)
    trimmed_clip.write_videofile(clip_path)
    print(f'Clip exported to {clip_path}')
