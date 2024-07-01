# -*- coding: utf-8 -*-
# @File       : 01_set research area.py
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
dta_area = pd.read_csv(os.path.join(DIR_HOME, '2_pipeline\\107_strava\\store\\user location statistics.csv'))

# ------------------------
# process data
# ------------------------
areas = ['USA']
dta_target = dta_area[(dta_area['NAME_2'] == 'Middlesex') & (dta_area['NAME_1'] == 'Massachusetts')]
dta_target.to_csv(os.path.join(DIR_PIPELINE, 'store', 'USA MA Middlesex.csv'), index=False)
