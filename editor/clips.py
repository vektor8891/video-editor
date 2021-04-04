#!/usr/bin/env python

import pandas as pd
import os

from typing import List

import editor.dataframe as d
import editor.ffmpeg as ff


def read_clips_data(folder='data', f_name='clips.csv') -> pd.DataFrame:
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


def get_input_folder() -> str:
    return os.path.join('data', 'videos')


def get_input_file_path(f_name: str) -> str:
    input_folder = get_input_folder()
    return os.path.join(input_folder, 'raw', f_name)


def get_output_file_path(file_name: str, clip_id: int) -> str:
    input_folder = get_input_folder()
    f_name, f_ext = os.path.splitext(file_name)
    f_name_id = f'{f_name}_{str(clip_id).zfill(2)}{f_ext}'
    return os.path.join(input_folder, 'temp', f_name_id)


def trim_clip(row: pd.Series) -> str:
    d.has_columns(row, ['Id', 'FileName', 'TimeStart', 'TimeEnd'],
                  raise_error=True)
    f_name = row['FileName']
    f_in = get_input_file_path(f_name)
    f_out = get_output_file_path(f_name, clip_id=row['Id'])
    trim_cmd = ff.trim_video_cmd(f_in, f_out,
                                 t_start=row['TimeStart'],
                                 t_end=row['TimeEnd'])
    ff.run_command(trim_cmd)
    return f_out
