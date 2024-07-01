
# ------------------------
# define global settings
# ------------------------
SETTING_PIPELINE_NAME = "140_clean version"

# ------------------------
# import packages
# ------------------------
import numpy as np
import traceback
import requests
import time
import os
import glob
import json
import geopandas
import pandas as pd
from tqdm import tqdm
import rasterio as rs
from multiprocessing import Process

DIR_HOME = "XXXXXX"
DIR_CURRENT = os.getcwd()
DIR_PIPELINE = os.path.join(DIR_HOME, "2_pipeline", SETTING_PIPELINE_NAME)
if not os.path.exists(DIR_PIPELINE):
    os.mkdir(DIR_PIPELINE)
    os.mkdir(os.path.join(DIR_PIPELINE, "out"))
    os.mkdir(os.path.join(DIR_PIPELINE, "store"))
    os.mkdir(os.path.join(DIR_PIPELINE, "temp"))

# ------------------------
# read data
# ------------------------
def process_records(city):
    dta_post = pd.read_csv(os.path.join(DATA_DIR, 'post\\Post_data_' + city))
    dta_profile = pd.read_csv(os.path.join(DATA_DIR, 'user\\User_data_' + city))

    # Process profile
    dta_profile = dta_profile[['user_id', 'user_gender', 'user_joinTime', 'user_follow', 'user_followed']]
    dta_profile = dta_profile.dropna(subset=['user_gender'])


    # Statistic
    sta_distance = np.percentile(dta_post['post_distance'].sort_values(),95)
    sta_duration = np.percentile(dta_post['post_elapsed'].sort_values(),95)
    print(f"95% distance is lower than: {sta_distance}")
    print(f"95% duration is lower than: {sta_duration}")


    # Filter post
    wanted_types = ['Ride', 'Run', 'VirtualRide', 'Walk', 'Workout', 'Swim', 'WeightTraining', 'Hike', 'Yoga',
                                           'VirtualRun', 'EBikeRide', 'Cycling']
    dta_post = dta_post[dta_post['post_type'].isin(wanted_types)]
    dta_post = dta_post[dta_post['post_distance']<=sta_distance]
    dta_post = dta_post[dta_post['post_elapsed']<sta_duration]

    dta_post['post_duration'] = dta_post['post_elapsed'] / 60
    dta_post['timestamp_day'] = (dta_post['post_time'] - 1546214400) // 86400 * 86400 + 1546214400
    dta_post['timestamp_week'] = (dta_post['post_time'] - 1546214400) // 604800 * 604800 + 1546214400
    dta_post['n'] = 1

    # user weekly duration
    dta_user = dta_post.groupby(['user_id', 'timestamp_week'])[['post_duration', 'post_distance','post_kudos','n']].sum().reset_index()

    # user active days
    dta_act = dta_post.groupby(['user_id', 'timestamp_day', 'timestamp_week'])['n'].sum().reset_index()
    dta_act['n'] = 1
    dta_act = dta_act.groupby(['user_id', 'timestamp_week'])['n'].sum().reset_index()
    dta_act = dta_act.rename(columns={'n':'active_days'})

    # Generate user week table
    dta_user_list = dta_profile[['user_id']].drop_duplicates()
    dta_week_list = dta_user[['timestamp_week']].drop_duplicates().sort_values(by=['timestamp_week'], ascending=True)
    dta_user_list['key'] = 1
    dta_week_list['key'] = 1
    dta_ret = pd.merge(dta_user_list, dta_week_list, on='key').drop(columns=['key'])

    # Join result
    dta_ret = pd.merge(dta_ret, dta_user, how='left')
    dta_ret = pd.merge(dta_ret, dta_act, how='left')
    dta_ret = dta_ret.fillna(0)
    dta_ret = pd.merge(dta_ret, dta_profile, how='left')

    # Postprocess
    dta_ret['register_index'] = (dta_ret['timestamp_week'] - dta_ret['user_joinTime']) // 604800
    dta_ret.drop(columns=['user_joinTime'])
    dta_ret['user_gender'] = dta_ret['user_gender'].astype(int)
    dta_ret['active_days'] = dta_ret['active_days'].astype(int)
    dta_ret['post_kudos'] = dta_ret['post_kudos'].astype(int)
    dta_ret['n'] = dta_ret['n'].astype(int)
    dta_ret = dta_ret.drop(columns=['user_joinTime'])
    return dta_ret


DATA_DIR = "XXXXXX"
files = glob.glob(os.path.join(DATA_DIR, 'post', 'Post_data_*.csv'))
already_processed = os.listdir(os.path.join(DIR_PIPELINE, 'store\\city athlete'))
for file in files:
    city_name = file.split('\\')[-1][10:]
    if city_name in already_processed:
        continue
    print(f"Processing {city_name}")

    ret = process_records(city_name)
    ret.to_csv(os.path.join(DIR_PIPELINE, 'store\\city athlete', city_name), index=False)
