"""
Routine to update layer storage in ArcGIS OnLine
"""
# Libs
from arcgis.gis import GIS
import pandas as pd
import datetime as dt
import os
from arcgis.features import FeatureLayerCollection
from arcgis.features import FeatureLayer
from pathlib import Path


# User Account
USER = "TestRodriguesDF"
PASSWORD = "*hyr-Ws.*C&A8PU"  # enter with TestRodriguesDF account's password

# Layer ID
ID = '91058a92f70b4ff49aba6ea9354d9f1a'

# Path to base dir
BASE_DIR = Path(__file__).resolve().parent


# Connect to the GIS
def connect_gis(user, password):
    return GIS("https://www.arcgis.com", username=user, password=password)


# Access the original data set
def access_data(layer_id, conection):
    gis = conection
    bancos_item = gis.content.get(layer_id)
    bancos_flayer = bancos_item.layers[0]
    """Bypass to access FeatureLayer.query outside Jupyter Notebook 
    (https://github.com/Esri/arcgis-python-api/issues/776)"""
    FeatureLayer._token = property(lambda self: self._con.token)
    bancos_query = bancos_flayer.query()
    bancos_features = bancos_query.features
    return bancos_item, bancos_flayer, bancos_features


# Create DataFrame from features
def json_to_df(bancos_features):
    df = pd.read_json(str(bancos_features))
    dfk = list(df['attributes'][0].keys())[:-1]
    dfv = []
    for k, v in enumerate(df['attributes'].items()):
        dfv.append(list(df["attributes"][k].values())[:-1])
    bancos_df_1 = pd.DataFrame(dfv, columns=dfk)
    bancos_df_1.head()
    return bancos_df_1


# Check/make dir to write a backup file of the original data
def bkp_original_file(bancos_df_1):
    if not os.path.exists(os.path.join('data', BASE_DIR, 'backup')):
        os.mkdir(os.path.join('data', BASE_DIR, 'backup'))
    # Copy original file to backup
    now = int(dt.datetime.now().timestamp())
    return bancos_df_1.to_csv(os.path.join('data', BASE_DIR, 'backup',
                                           'csv_bancos_backup' + '_' + str(now) + '.csv'))


# Read the second csv set
def read_new_csv():
    csv2 = os.path.join('data', BASE_DIR, 'bancos_2.csv')
    bancos_df_2 = pd.read_csv(csv2)
    bancos_df_2.head()
    return bancos_df_2


# Merge both DataFrames
def merge_dfs(bancos_df_1, bancos_df_2):
    updated_df = bancos_df_1.append(bancos_df_2)
    updated_df.drop_duplicates(subset='banco_id', keep='last', inplace=True)  # Eliminate possible duplicated entries
    return updated_df


# Check if exists and create folder to storage the updated csv file
def bkp_updated_file(updated_df):
    if not os.path.exists(os.path.join('data', BASE_DIR, 'updated_csv_content')):
        os.mkdir(os.path.join('data', BASE_DIR, 'updated_csv_content'))
    return updated_df.to_csv(os.path.join('data', BASE_DIR,
                                          'updated_csv_content', 'bancos_updated.csv'))


# Update the Feature Collection
def overwrite_layer(bancos_item):
    bancos_flayer_collection = FeatureLayerCollection.fromitem(bancos_item)
    return bancos_flayer_collection.manager.overwrite(os.path.join('data', BASE_DIR,
                                                                   'updated_csv_content', 'bancos_updated.csv'))


if __name__ == '__main__':
    gis = connect_gis(USER, PASSWORD)
    bancos_item, bancos_flayer, bancos_features = access_data(ID, gis)
    bancos_df_1 = json_to_df(bancos_features)
    bkp_original_file(bancos_df_1)
    bancos_df_2 = read_new_csv()
    updated_df = merge_dfs(bancos_df_1, bancos_df_2)
    bkp_updated_file(updated_df)
    overwrite_layer(bancos_item)
    print(f'Layer "{bancos_item.title}" successfully updated!')
