# -*- coding: utf-8 -*-
# @File       : 02_get user list.py
# @Author     : Yuchen Chai
# @Date       : 2022/12/24 17:22
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
dta_target = pd.read_csv(os.path.join(DIR_PIPELINE, 'store\\USA MA Middlesex.csv'))
dta_user = pd.read_csv(os.path.join(DIR_HOME, '2_pipeline\\107_strava\\out\\user location.csv'))
dta_user = dta_user.drop(columns=['count'])
# ------------------------
# process data
# ------------------------
dta_user = pd.merge(dta_user, dta_target, how='left')
dta_user = dta_user.dropna(subset=['count'])
dta_user = dta_user.drop(columns=['count'])
dta_user['loc_id'] = dta_user['NAME_0'] + '_' + dta_user['NAME_1'] + '_' + dta_user['NAME_2']
dta_user.to_csv(os.path.join(DIR_PIPELINE, 'store\\USA MA Middlesex User List.csv'), index=False)
