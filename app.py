#!/usr/bin/env python

import editor.clips as c

df_clips = c.read_media_data()

videos = [1]

for video_id in videos:
    clips = c.get_clips(df_clips, video_id)
    file_names = []
    for i, row in clips.iterrows():
        trimmed_file = c.trim_clip(row)
        file_names.append(trimmed_file)
    merged_file = c.merge_clips(file_names, video_id)
    audio_file = c.add_audio(merged_file, video_id)
pass