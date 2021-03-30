#!/usr/bin/env python

import pandas as pd
import os


def read_clip_data(folder='data', f_name='clips.csv'):
    f_path = os.path.join(folder, f_name)
    df = pd.read_csv(f_path)
    return df
