#!/usr/bin/env python

import pandas as pd
import os

from typing import Union

import editor.dataframe as d
import editor.ffmpeg as ff


def read_media_data(folder='data', f_name='clips.csv') -> pd.DataFrame:
    f_path = os.path.join(folder, f_name)
    df = pd.read_csv(f_path)
    return df


def get_clips(df: pd.DataFrame, video_id: int) -> pd.DataFrame:
    d.has_columns(df, ['VideoId', 'Id'], raise_error=True)
    d.has_duplicates(df, 'Id', raise_error=True)
    df.sort_values(by=['Id'], inplace=True)
    dfc = df.copy()
    mask = dfc['VideoId'] == video_id
    dfc = dfc.loc[mask, :]
    if dfc.empty:
        raise ValueError(f"No clips found for Video ID {video_id}!")
    return dfc


def get_video(video_id: int, column=None) -> Union[pd.DataFrame, str]:
    df_videos = read_media_data(f_name='videos.csv')
    d.has_duplicates(df_videos, 'Id', raise_error=True)
    dfc = df_videos.copy()
    mask = dfc['Id'] == video_id
    dfc = dfc.loc[mask, :]
    if column:
        d.has_column(dfc, column, raise_error=True)
        return dfc.loc[0, column]
    return dfc


def get_input_folder() -> str:
    return os.path.join('data', 'videos')


def get_input_file_path(f_name: str) -> str:
    input_folder = get_input_folder()
    return os.path.join(input_folder, 'raw', f_name)


def get_output_file_path(file_name: str, suffix=None) -> str:
    input_folder = get_input_folder()
    f_name, f_ext = os.path.splitext(file_name)
    if isinstance(suffix, int):
        f_suffix = str(suffix).zfill(2)
    elif isinstance(suffix, str):
        f_suffix = suffix
    else:
        raise ValueError(f'Invalid file suffix: {str(suffix)}')
    f_name_full = f'{f_name}_{f_suffix}{f_ext}'
    return os.path.join(input_folder, 'temp', f_name_full)


def trim_clip(row: pd.Series) -> str:
    d.has_columns(row, ['Id', 'FileName', 'TimeStart', 'TimeEnd'],
                  raise_error=True)
    f_name = row['FileName']
    f_in = get_input_file_path(f_name)
    f_out = get_output_file_path(f_name, suffix=row['Id'])
    trim_cmd = ff.trim_video_cmd(f_in, f_out,
                                 t_start=row['TimeStart'],
                                 t_end=row['TimeEnd'])
    ff.run_command(trim_cmd)
    return f_out


def write_input_files(f_list: list, input_files_path: str) -> bool:
    # create temporary file containing input files
    # https://ma.ttias.be/use-ffmpeg-combine-multiple-videos/
    with open(input_files_path, 'w') as f:
        f_list_str = "\r\n".join(f"file '{f_in}'" for f_in in f_list)
        f.write(f_list_str)
    return True


def merge_clips(f_list: list, video_id: int, input_files_path='temp.txt') -> str:
    write_input_files(f_list, input_files_path)
    f_name = get_video(video_id, "Name")
    f_out = get_output_file_path(f_name, suffix="merged")
    cmd = ff.merge_videos_cmd(input_files_path, f_out)
    ff.run_command(cmd)
    ff.delete_existing_file(input_files_path)
    return f_out
