#!/usr/bin/env python

import editor.dataframe as d

df_clips = d.read_clips_data()

ids = [1]

for id in ids:
    clip = d.get_clip_data(df_clips, id)

pass