# ------------------------
# define global settings
# ------------------------
SETTING_PIPELINE_NAME = "140_clean version"

# ------------------------
# import packages
# ------------------------
import os
from utils import process_records
from utils import generate_features, create_path_if_not_exists
from tqdm import tqdm

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


DATA_DIR = "XXXXXX"
DATA_USER = "XXXXXX"
files = os.listdir(os.path.join(DIR_PIPELINE, 'store', 'city athlete'))

create_path_if_not_exists(os.path.join(DATA_DIR, 'city feature'))
existed_files = os.listdir(os.path.join(DATA_DIR, 'city feature'))

# ------------------------
# configuration
# ------------------------

if __name__ == '__main__':

    for file in tqdm(files):
        city_name = file.replace('.csv', '')
        if file in existed_files:
            continue
        print(f"Processing {city_name}")

        ret = process_records(city_name)
        ret = generate_features(ret)

        ret.to_csv(os.path.join(DATA_DIR, 'city feature', city_name + '.csv'), index=False)