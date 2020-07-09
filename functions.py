import moviepy.editor as movie
import os
import re
import pandas as pd
import datetime
import time

# open current directory
os.chdir(os.path.dirname(os.path.realpath(__file__)))

clip_intro = movie.VideoFileClip('input/intro.mp4')
clip_action = movie.VideoFileClip('input/call-to-action-up.mp4')
clip_outro = movie.VideoFileClip('input/outro.mp4')


def get_videos():
    videos = pd.read_excel('videos.xlsx')
    return videos


def get_video_row(video_id: int):
    videos = get_videos()
    return videos[videos.Id == video_id].squeeze()


def get_video_column(video_id: int, column: str):
    video_row = get_video_row(video_id=video_id)
    video_column = video_row[column]
    return video_column


def get_clips():
    clips = pd.read_excel('clips_final.xlsx')
    return clips


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
    videos = get_videos()
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


def get_clip_data():
    videos = get_videos()
    pd_clips = pd.DataFrame(columns=['Id', 'VideoId', 'ClipId', 'VideoName',
                                     'ClipName', 'ClipPath', 'ExerciseLink',
                                     'ShortLink', 'YoutubeLink',
                                     'CardLinks', 'Tags'])
    clip_index = 0
    for index, video in videos.iterrows():
        for clip_id, clip in enumerate(video.Clips.split('\n')):
            clip_path = f'output/raw/video{video.Id:02}_clip{clip_id:02}.mp4'
            clip_name = video.Clips.split('\n')[clip_id]
            exercise_link = video.ExerciseLink.split('\n')[clip_id]
            short_link = video.ShortLink.split('\n')[clip_id]
            card_links = get_card_links(video_id=video.Id, clip_id=clip_id)
            pd_clip = pd.DataFrame({
                'Id': [clip_index],
                'VideoId': [video.Id],
                'ClipId': [clip_id],
                'VideoName': [video.Name],
                'ClipName': [clip_name],
                'ClipPath': [clip_path],
                'ExerciseLink': [exercise_link],
                'ShortLink': [short_link],
                'YoutubeLink': [video.YoutubeLink],
                'Tags': [video.Tags],
                'CardLinks': ['\n'.join(card_links) if len(card_links) > 0
                              else '']
            })
            clip_index = clip_index + 1
            pd_clips = pd_clips.append(pd_clip, ignore_index=True)
    return pd_clips


def trim_video_clips(video_ids: list):
    videos = get_videos()
    for index, video in videos[videos.Id.isin(video_ids)].iterrows():
        for clip_id, clip in enumerate(video.Clips.split('\n')):
            clip_path = f'output/raw/video{video.Id:02}_clip{clip_id:02}.mp4'
            if not os.path.isfile(clip_path):
                trim_video_clip(video_id=video.Id, clip_id=clip_id,
                                clip_path=clip_path)
            else:
                print(f'Skipping {clip_path} (already done)')


def add_intro_outro(clip_ids: list):
    clips = get_clips()
    for index, clip in clips[clips.Id.isin(clip_ids)].iterrows():
        final_path = f"output/final/{clip.VideoTitle}.mp4"
        if not os.path.isfile(final_path):
            clip_exercise = movie.VideoFileClip(clip.ClipPath)
            final_clip = movie.concatenate_videoclips([clip_intro,
                                                       clip_exercise,
                                                       clip_action,
                                                       clip_outro])
            final_clip.write_videofile(final_path)
            print(f"Clip {clip.Id} exported to {final_path}")
        else:
            print(f'Skipping {final_path} (already done)')


def get_time_diff_seconds(t_start: str, t_end: str, t_middle: str):
    sec_start = get_sec(t_start)
    sec_end = get_sec(t_end)
    sec_middle = get_sec(f'{t_middle}:00')
    if sec_middle < sec_start or sec_middle > sec_end:
        return None
    else:
        return round(sec_middle - sec_start)


def get_card_links(video_id: int, clip_id: int):
    videos = get_videos()
    video = videos[videos.Id == video_id].squeeze()
    clip_start = str(video.Start).split('\n')[clip_id]
    clip_end = str(video.End).split('\n')[clip_id]
    card_links = []
    intro_length = 4
    for link in str(video.Links).split('\n'):
        if len(link.split('-')) > 1:
            link_video_id = int(link.split('-')[1].strip())
            if link_video_id > 0:
                link_timestamp = link.split('-')[0].strip()
                link_diff = get_time_diff_seconds(t_start=clip_start,
                                                  t_end=clip_end,
                                                  t_middle=link_timestamp)
                if link_diff:
                    total_diff = link_diff + intro_length
                    str_diff = str(datetime.timedelta(seconds=total_diff))
                    link_name = get_video_column(video_id=link_video_id,
                                                 column='Name')
                    card_link = f'{str_diff} - {link_video_id}.' \
                                f' {link_name}'
                    card_links.append(card_link)
    return card_links
