# -*- coding: utf-8 -*-
# @File       : 05_clean network.py
# @Author     : Yuchen Chai
# @Date       : 2022/12/27 9:56
# @Description:


# ------------------------
# define global settings
# ------------------------
SETTING_PIPELINE_NAME = "130_strava network experiment"

# ------------------------
# import packages
# ------------------------
import traceback
import requests
import time
import os
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
dta = pd.read_csv(os.path.join(DIR_PIPELINE, 'store\\USA MA Middlesex aggregated.csv'))
dta_user = pd.read_csv(os.path.join(DIR_PIPELINE, 'store\\USA MA Middlesex User List.csv'))
dta_post = pd.read_csv(os.path.join(DIR_PIPELINE, 'store\\USA MA Middlesex post.csv'))

# ------------------------
# process data
# ------------------------
need_approval_user = dta[dta['need_approval'] == True].drop_duplicates(subset=['target_user_id'])
print(f"There are {len(need_approval_user)} needs approval")

dta = dta[['original_user_id','relation_type','target_user_id']]
print(f"There are {len(dta_user)} selected")

temp = dta_post.groupby('user_id').size()
temp = pd.DataFrame({'size':temp})
temp = temp.reset_index()

users_0 = set(temp[temp['size']==128]['user_id'].tolist())
users_1 = set(dta['original_user_id'].tolist())
users_2 = set(dta['target_user_id'].tolist())
user = users_1.union(users_2)
print(f"There are {len(users_1)} original users, {len(dta.drop_duplicates(subset=['target_user_id']))} target users, and {len(dta)} relationships")

dta_1 = dta[dta['relation_type'] == 'Following']
dta_2 = dta[dta['relation_type'] == 'Followed']
dta_2['original_user_id'], dta_2['target_user_id'] = dta_2['target_user_id'], dta_2['original_user_id']
dta_2['relation_type'] = 'Following'
dta = pd.concat([dta_1, dta_2])
dta = dta.drop_duplicates()
dta = dta[(dta['target_user_id'].isin(users_0)) & (dta['original_user_id'].isin(users_0))]
print(f"There are {len(dta)} relationships within given original users")

dta = dta[~dta['target_user_id'].isin(need_approval_user['target_user_id'])]
dta = dta[~dta['original_user_id'].isin(need_approval_user['target_user_id'])]
print(f"There are {len(dta)} relationship after cleaning")

users_1 = set(dta['original_user_id'].tolist())
users_2 = set(dta['target_user_id'].tolist())
user = users_1.union(users_2)
user = users_0.intersection(user)
print(f"There are {len(user)} valid users after cleaning")

dta.to_csv(os.path.join(DIR_PIPELINE, 'store\\USA MA Middlesex cleaned.csv'), index=False)
