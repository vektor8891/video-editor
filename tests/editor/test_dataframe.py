#!/usr/bin/env python

import pandas as pd

import editor.dataframe as d


def test(tmp_path):
    f_name = "test.csv"
    f_path = tmp_path / f_name
    df = pd.DataFrame(data={"Col": ["A"]})
    df.to_csv(f_path, index=False)
    assert d.read_clip_data(tmp_path, f_name).equals(df)
