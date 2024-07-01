# -*- coding: utf-8 -*-
# @File       : 07_prepare data.py
# @Author     : Yuchen Chai
# @Date       : 2022/12/28 15:30
# @Description:
import pickle

# ------------------------
# define global settings
# ------------------------
SETTING_PIPELINE_NAME = "130_strava network experiment"

# ------------------------
# import packages
# ------------------------
import os
import numpy as np
import pandas as pd

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
post = pd.read_csv(os.path.join(DIR_PIPELINE, 'store\\USA MA Middlesex post.csv'))
relation = pd.read_csv(os.path.join(DIR_PIPELINE, 'store\\USA MA Middlesex cleaned.csv'))
user_info = pd.read_csv(os.path.join(DIR_PIPELINE, 'store\\city athlete\\United States_Massachusetts_Middlesex.csv'))

# User list and index
user_0 = set(post.groupby('user_id').size())
user_1 = set(relation['original_user_id'].tolist())
user_2 = set(relation['target_user_id'].tolist())
user_list = user_1.union(user_2)
user_list = pd.DataFrame({'user_id':sorted(user_list)})
user_list['user_index'] = user_list.index
post['d1'] = pd.to_datetime(post['timestamp_week'], unit='s')


# User edge weight
user_info = user_info[['user_id','user_follow']].drop_duplicates()
user_info['edge_weight'] = np.log(user_info['user_follow']+1)

# Filter post
post_filter = post[post['user_id'].isin(user_list['user_id'])]
post_filter['TEMP2'] = post_filter['TEMP'] * post_filter['TEMP']
post_filter['HUMI2'] = post_filter['HUMI'] * post_filter['HUMI']
columns = ['user_id','DURATION_0',

           'user_gender',
           'register_index',
           'TEMP',
           'TEMP2',
           'WIND',
           'HUMI',
           'HUMI2',
           'VISI',
           'PRES',
           'CLOD',
           'PRCP',
           'LG_FOLLOW',
           'IS_COVID_START',
           'LG_NEW_CONFIRM',
           'POLICY','INDEX',
           'TEMP_1', 'PRCP_1', 'DURATION_1', 'CITY_GENERAL_ELAPSED_RATIO_1',
           'TEMP_2', 'PRCP_2', 'DURATION_2', 'CITY_GENERAL_ELAPSED_RATIO_2',
           'TEMP_3', 'PRCP_3', 'DURATION_3', 'CITY_GENERAL_ELAPSED_RATIO_3',
               #
               # 'TEMP_1', 'DEWP_1', 'PRCP_1', 'NUM_POST_1', 'ACTIVE_DAY_1','DURATION_1', 'DISTANCE_1', 'KUDOS_1',
               # 'CITY_GENERAL_POST_RATIO_1', 'CITY_GENERAL_ACTIVE_USER_RATIO_1', 'CITY_GENERAL_DISTANCE_RATIO_1',
               # 'CITY_GENERAL_ELAPSED_RATIO_1',
               # # 'CITY_TOTAL_POST_1', 'CITY_TOTAL_ACTIVE_USER_1', 'CITY_AVG_DISTANCE_1', 'CITY_AVG_DURATION_1',
               #
               # 'TEMP_2', 'DEWP_2', 'PRCP_2', 'NUM_POST_2', 'ACTIVE_DAY_2', 'DURATION_2', 'DISTANCE_2', 'KUDOS_2',
               # 'CITY_GENERAL_POST_RATIO_2', 'CITY_GENERAL_ACTIVE_USER_RATIO_2', 'CITY_GENERAL_DISTANCE_RATIO_2',
               # 'CITY_GENERAL_ELAPSED_RATIO_2',
               # # 'CITY_TOTAL_POST_2', 'CITY_TOTAL_ACTIVE_USER_2', 'CITY_AVG_DISTANCE_2', 'CITY_AVG_DURATION_2',
               #
               # 'TEMP_3', 'DEWP_3', 'PRCP_3', 'NUM_POST_3', 'ACTIVE_DAY_3', 'DURATION_3', 'DISTANCE_3', 'KUDOS_3',
               # 'CITY_GENERAL_POST_RATIO_3', 'CITY_GENERAL_ACTIVE_USER_RATIO_3', 'CITY_GENERAL_DISTANCE_RATIO_3',
               # 'CITY_GENERAL_ELAPSED_RATIO_3',
               # # 'CITY_TOTAL_POST_3', 'CITY_TOTAL_ACTIVE_USER_3', 'CITY_AVG_DISTANCE_3', 'CITY_AVG_DURATION_3',
               ]
post_filter = post_filter[columns]

# Normalize
normalize_data = True
if normalize_data:
    norm_cols = ['DURATION_0',
                 'register_index',
                 'TEMP', 'TEMP2','WIND','HUMI','HUMI2','VISI','PRES','CLOD', 'PRCP',
                 'TEMP_1', 'PRCP_1', 'DURATION_1',
                 'TEMP_2', 'PRCP_2', 'DURATION_2',
                 'TEMP_3', 'PRCP_3', 'DURATION_3',
                ]

    y_mean = post_filter['DURATION_0'].mean()
    y_std = post_filter['DURATION_0'].std()
    day_mean = post_filter['INDEX'].mean()
    day_std = post_filter['INDEX'].std()
    print(f"Mean: {y_mean}")
    print(f"STD: {y_std}")
    print(f"150 min: {(150-y_mean)/y_std}")
    print(f"0 min: {(0-y_mean)/y_std}")
    print(f"111(108) week: {(111 - day_mean) / day_std}")
    print(f"0 week: {(0 - day_mean) / day_std}")
    post_filter[norm_cols] = (post_filter[norm_cols] - post_filter[norm_cols].mean()) / post_filter[norm_cols].std()

# Sort data
drop_cols = ['user_id']
post_filter = pd.merge(post_filter, user_list, how='left')
post_filter = post_filter.drop(columns=drop_cols)

# Edge snapshot
relation_mut = pd.merge(relation, user_list, left_on='original_user_id', right_on='user_id', how='left')
relation_mut = relation_mut.rename(columns={'user_index':'original_index'})
relation_mut = pd.merge(relation_mut, user_list, left_on='target_user_id', right_on='user_id', how='left')
relation_mut = relation_mut.rename(columns={'user_index':'target_index'})
relation_mut = relation_mut.sort_values(by=['original_index', 'target_index'])
relation_mut = relation_mut[relation_mut['original_index'] != relation_mut['target_index']]
relation_mut = pd.merge(relation_mut, user_info, left_on='target_user_id', right_on='user_id', how='left')
edge_snapshot = [relation_mut['original_index'].tolist(), relation_mut['target_index'].tolist()]

# Edge attr
# Option 1: equal weight
edge_attr = [1] * len(edge_snapshot[0])
# Option 2: various weight
edge_attr = relation_mut['edge_weight'].tolist()

# X, y
def generate_gnn_x_y(p):
    week_index = p[['INDEX']].drop_duplicates().sort_values(by=['INDEX'])['INDEX'].tolist()
    retX = []
    rety = []
    for week in week_index:
        pp = p[p['INDEX'] == week]
        pp = pp.sort_values(by=['user_index'])
        # drop_col1 = []
        col1 = [
            'user_gender', 'register_index',
            'TEMP', 'TEMP2', 'WIND', 'HUMI', 'HUMI2', 'VISI', 'PRES', 'CLOD', 'PRCP',
            'IS_COVID_START', 'POLICY',
            'DURATION_1', 'DURATION_2', 'DURATION_3'
        ]
        X = pp[col1]
        X = X.to_numpy()
        y = pp['DURATION_0'].to_numpy()
        retX.append(X)
        rety.append(y)

    return np.array(retX), np.array(rety)


gnnX, gnny = generate_gnn_x_y(post_filter)
dataset = {
    'gnn_X': gnnX,
    'edge_index': edge_snapshot,
    'edge_attr': edge_attr,
    'gnn_y': gnny,
    'nn_data': post_filter
}

with open(os.path.join(DIR_PIPELINE, 'store\\USA MA Middlesex\\USA MA Middlesex data_F16_various weight.pickle'), 'wb') as f:
    pickle.dump(dataset, f)
user_list.to_csv(os.path.join(DIR_PIPELINE, 'store\\USA MA Middlesex\\USA MA Middlesex user.csv'), index=False)
