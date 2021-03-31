#!/usr/bin/env python

import pandas as pd
import os


def has_column(df: pd.DataFrame, column: str, raise_error=False) -> bool:
    has_col = column in df.columns
    if raise_error and not has_col:
        raise ValueError(f"Column '{column}' not found!")
    return has_col


def read_clips_data(folder='data', f_name='clips.csv') -> pd.DataFrame:
    f_path = os.path.join(folder, f_name)
    df = pd.read_csv(f_path)
    return df


def get_clip_data(df_clip: pd.DataFrame, clip_id: int) -> pd.Series:
    has_column(df_clip, 'Id', raise_error=True)
    df_filter = df_clip[df_clip['Id'] == clip_id]
    if df_filter.empty:
        raise ValueError(f"Clip ID {clip_id} not found!")
    elif len(df_filter.index) > 1:
        raise ValueError(f"Multiple clips found with ID {clip_id}!")
    return df_filter.iloc[0]
