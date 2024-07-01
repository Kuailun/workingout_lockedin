# -*- coding: utf-8 -*-
# @File       : 03_calculate feature mean std.py
# @Author     : Yuchen Chai
# @Date       : 2024/6/8 19:12
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

x_cols = ['TEMP', 'TEMP2', 'WIND', 'HUMI', 'HUMI2', 'VISI', 'PRES', 'CLOD', 'PRCP', 'DURATION_0']

# Initialize variables to calculate mean and variance
sum_x = {col: 0 for col in x_cols}
sum_x2 = {col: 0 for col in x_cols}
n = 0

ret = []
for file_idx, file in enumerate(tqdm(csv_files)):
    nn_dta = pd.read_csv(file, usecols=['INDEX'] + x_cols)
    nn_train = nn_dta[(nn_dta['INDEX']<3+normal_test_point) | ((nn_dta['INDEX']>=3+covid_train_point) & (nn_dta['INDEX']<3+covid_test_point))]

    n += len(nn_train)
    for col in x_cols:
        sum_x[col] += nn_train[col].sum()
        sum_x2[col] += (nn_train[col] ** 2).sum()

# Calculate mean and standard deviation for each feature
mean = {col: sum_x[col] / n for col in x_cols}
std = {col: np.sqrt((sum_x2[col] / n) - (mean[col] ** 2)) for col in x_cols}

print("Mean:", mean)
print("Std:", std)
