#!/usr/bin/env python

from typing import Union

import pandas as pd


def has_column(df: Union[pd.DataFrame, pd.Series], column: str,
               raise_error=False) -> bool:
    if isinstance(df, pd.core.series.Series):
        df_new = df.to_frame()
        if len(df_new.index) > 0:
            df_new = df_new.transpose()
        return has_column(df_new, column, raise_error)
    else:
        has_col = column in df.columns
        if raise_error and not has_col:
            raise ValueError(f"Column '{column}' not found!")
        return has_col


def has_columns(df: Union[pd.DataFrame, pd.Series], columns: list,
                raise_error=False) -> bool:
    return all([has_column(df, c, raise_error) for c in columns])


def has_duplicates(df: pd.DataFrame, column: str, raise_error=False) -> bool:
    df_duplicate = df[df.duplicated([column])]
    has_duplicate = not df_duplicate.empty
    if has_duplicate & raise_error:
        raise ValueError(f"Duplicates found in '{column}':", df_duplicate)
    return has_duplicate
