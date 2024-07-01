# ------------------------
# define global settings
# ------------------------
SETTING_PIPELINE_NAME = "140_clean version"

import pandas as pd
import numpy as np
import os

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
dta_env = pd.read_csv(os.path.join(DIR_HOME, '2_pipeline\\110_aggregate data\\out\\all admin 2.csv'))

def process_records(city):
    NAME_0, NAME_1, NAME_2 = city.split('_')
    city_info = dta_env[(dta_env['NAME_0']==NAME_0)&(dta_env['NAME_1']==NAME_1)&(dta_env['NAME_2']==NAME_2)]
    city_info = city_info.drop(columns=['NAME_0','NAME_1','NAME_2','key'])
    dta_city = pd.read_csv(os.path.join(DIR_PIPELINE,'store', 'city athlete', city+'.csv'))
    dta_city_general = pd.read_csv(os.path.join(DIR_PIPELINE,'store', 'city statistic', city+'.csv'))
    dta_city_general = dta_city_general.rename(columns={'post_distance_ratio':'city_general_distance_ratio',
                                                        'post_elapsed_ratio': 'city_general_elapsed_ratio',
                                                        'post_num_ratio': 'city_general_post_ratio',
                                                        'active_user_ratio': 'city_general_active_user_ratio',
                                                        'post_distance':'city_general_distance',
                                                        'post_elapsed': 'city_general_elapsed',
                                                        'n': 'city_general_post',
                                                        })
    dta_ret = pd.merge(dta_city, dta_city_general)
    dta_ret = pd.merge(dta_ret, city_info, left_on=['timestamp_week'], right_on=['TIMESTAMP_WEEK'])
    dta_ret = dta_ret.drop(columns=['TIMESTAMP_WEEK'])
    return dta_ret


def generate_features(post):
    # Generate features
    post['LG_FOLLOW'] = np.log(post['user_follow'] + 1)
    post['LG_FOLLOWED'] = np.log(post['user_followed'] + 1)
    post['POLICY'] = 1 * ((post['Flag'] == 2) & (post['Stay_at_home'] >= 1))
    post['IS_COVID_START'] = 1 * (post['timestamp_week'] >= 1584244800)
    post['TEMP2'] = post['TEMP'] * post['TEMP']
    post['HUMI2'] = post['HUMI'] * post['HUMI']

    post['TEMP'] = post['TEMP'].astype(int)
    post['TEMP2'] = post['TEMP2'].astype(int)
    post['WIND'] = post['WIND'].astype(int)
    post['HUMI'] = post['HUMI'].astype(int)
    post['HUMI2'] = post['HUMI2'].astype(int)
    post['VISI'] = post['VISI'].astype(int)
    post['PRES'] = post['PRES'].astype(int)
    post['CLOD'] = post['CLOD'].astype(int)
    post['PRCP'] = post['PRCP'].astype(int)

    post = post.rename(columns={"n": "NUM_POST_0",
                                "post_duration": "DURATION_0",
                                })

    post = post.sort_values(by=['user_id', 'timestamp_week'])

    # History
    post['INDEX'] = (post['timestamp_week'] - 1546214400) / 604800
    post['DURATION_0'] = post['DURATION_0'].astype(int)
    post['DURATION_1'] = post['DURATION_0'].shift(1)
    post['DURATION_2'] = post['DURATION_0'].shift(2)
    post['DURATION_3'] = post['DURATION_0'].shift(3)

    # Filter post
    post = post[post['register_index']>=0]
    post = post[post['INDEX']>=3]

    # Drop columns
    columns = ['user_follow', 'user_followed',
               'New_Death','New_Recovery','Cum_Confirm','Cum_Death','Cum_Recovery',
               'Flag','Stay_at_home',
               'New_Confirm',
               "post_distance",
               "post_kudos",
               "NUM_POST_0",
               "active_days",
               "city_general_distance",
               "city_general_elapsed",
               "city_general_post",
               "active_user",
               "city_general_distance_ratio",
               "city_general_elapsed_ratio",
               "city_general_post_ratio",
               "city_general_active_user_ratio",
               "GUST",
               "DEWP"

               ]
    post = post.drop(columns=columns)

    return post


def create_path_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)