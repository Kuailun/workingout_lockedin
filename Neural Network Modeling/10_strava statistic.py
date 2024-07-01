# -*- coding: utf-8 -*-
# @File       : 10_strava statistic.py
# @Author     : Yuchen Chai
# @Date       : 2024/6/14 16:38
# @Description:

# ------------------------
# define global settings
# ------------------------
SETTING_PIPELINE_NAME = "140_clean version"

# ------------------------
# import packages
# ------------------------
import os
import pandas as pd
from tqdm import tqdm

# ------------------------
# define local settings
# ------------------------


# ------------------------
# folders
# ------------------------
DIR_HOME = "XXXXXX"
DIR_CURRENT = os.getcwd()
DIR_PIPELINE = os.path.join(DIR_HOME, "2_pipeline", SETTING_PIPELINE_NAME)
if not os.path.exists(DIR_PIPELINE):
    os.mkdir(DIR_PIPELINE)
    os.mkdir(os.path.join(DIR_PIPELINE, "out"))
    os.mkdir(os.path.join(DIR_PIPELINE, "store"))
    os.mkdir(os.path.join(DIR_PIPELINE, "temp"))

# ------------------------
# process
# ------------------------
DIR_FEATURE = "XXXXXX"
files = os.listdir(DIR_FEATURE)

ret = {
    "total user": 0,
    "total user-week": 0
}
for file in tqdm(files):
    temp = pd.read_csv(os.path.join(DIR_FEATURE, file), usecols=['user_id'])
    ret['total user-week'] += len(temp)
    ret['total user'] += len(temp['user_id'].unique())

print(ret)