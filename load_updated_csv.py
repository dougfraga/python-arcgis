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


"""User Account information and layer ID"""
USER = "TestRodriguesDF"
PASSWORD = "******"  # enter with TestRodriguesDF account's password
ID = '3258a4b0c97446ada3206c4dc174492b'


BASE_DIR = Path(__file__).resolve().parent


def connect_gis(user, password):
    """Make a connection with ArcGIS OnLine (AGOL) with private credentials"""
    return GIS("https://www.arcgis.com", username=user, password=password)


def access_data(layer_id, conection):
    """Access the original layer at AGOL from a specified connection and layer ID
    and return the layer's information"""
    gis = conection
    bancos_item = gis.content.get(layer_id)
    bancos_flayer = bancos_item.layers[0]
    """Bypass to access FeatureLayer.query outside Jupyter Notebook 
    (https://github.com/Esri/arcgis-python-api/issues/776)"""
    FeatureLayer._token = property(lambda self: self._con.token)
    bancos_query = bancos_flayer.query()
    bancos_features = bancos_query.features
    return bancos_item, bancos_flayer, bancos_features


def json_to_df(bancos_features):
    """Create DataFrame from feature attributes"""
    df = pd.read_json(str(bancos_features))
    dfk = list(df['attributes'][0].keys())[:-1]
    dfv = []
    for k, v in enumerate(df['attributes'].items()):
        dfv.append(list(df["attributes"][k].values())[:-1])
    bancos_df_1 = pd.DataFrame(dfv, columns=dfk)
    return bancos_df_1


def bkp_original_file(bancos_df_1):
    """Check/make dir to write a backup file of the original data
    with the instantaneous timestamp as a suffix file name"""
    if not os.path.exists(os.path.join('data', BASE_DIR, 'backup')):
        os.mkdir(os.path.join('data', BASE_DIR, 'backup'))
    now = int(dt.datetime.now().timestamp())
    return bancos_df_1.to_csv(os.path.join('data', BASE_DIR, 'backup',
                                           'csv_bancos_backup' + '_' + str(now) + '.csv'))


def read_new_csv():
    """Create the second DataFrame from the new csv file """
    csv2 = os.path.join('data', BASE_DIR, 'bancos_2.csv')
    bancos_df_2 = pd.read_csv(csv2)
    return bancos_df_2


def merge_dfs(bancos_df_1, bancos_df_2):
    """Merge both DataFrames and eliminate eventual duplicated entries"""
    updated_df = bancos_df_1.append(bancos_df_2)
    updated_df.drop_duplicates(subset='banco_id', keep='last', inplace=True)
    return updated_df


def bkp_updated_file(updated_df):
    """Check/make dir to storage the updated csv file"""
    if not os.path.exists(os.path.join('data', BASE_DIR, 'updated_csv_content')):
        os.mkdir(os.path.join('data', BASE_DIR, 'updated_csv_content'))
    return updated_df.to_csv(os.path.join('data', BASE_DIR,
                                          'updated_csv_content', 'bancos_updated.csv'))


def overwrite_layer(bancos_item):
    """Update the Feature Collection at AGOL from the updated csv file"""
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
