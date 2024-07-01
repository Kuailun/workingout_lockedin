# -*- coding: utf-8 -*-
# @File       : 04_calculate active weight.py
# @Author     : Yuchen Chai
# @Date       : 2024/6/8 19:37
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
import numpy as np

# ------------------------
# define local settings
# ------------------------
normal_test_point = 44
covid_train_point = 54
covid_test_point = 118
active_threshold = 150

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
csv_dir = "XXXXXX"
csv_files = [os.path.join(csv_dir, f) for f in os.listdir(csv_dir) if f.endswith('.csv')]

n = 0
n_active = 0

ret = []
for file_idx, file in enumerate(tqdm(csv_files)):
    nn_dta = pd.read_csv(file, usecols=['INDEX', 'DURATION_0'])
    nn_train = nn_dta[(nn_dta['INDEX']<3+normal_test_point) | ((nn_dta['INDEX']>=3+covid_train_point) & (nn_dta['INDEX']<3+covid_test_point))]

    n += len(nn_train)
    nn_train_active = nn_train[nn_train['DURATION_0'] > active_threshold]
    n_active += len(nn_train_active)

print("total:", n)
print("active (>150):", n_active)
print("ratio:", n_active/n)