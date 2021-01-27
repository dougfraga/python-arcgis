"""
Routine to update layer storage in ArcGIS OnLine
OBS: The path must be updated
"""
# Libs
from arcgis.gis import GIS
import pandas as pd
import datetime as dt
import os
from arcgis.features import FeatureLayerCollection
from arcgis.features import FeatureLayer


# User Account
USER = "TestRodriguesDF"
PASSWORD = "********"  # enter with TestRodriguesDF account's password


# Connect to the GIS
gis = GIS("https://www.arcgis.com", username=USER, password=PASSWORD)


# Access the original data set
bancos_item = gis.content.get('1382a35430c34464bb495295440062eb')
bancos_flayer = bancos_item.layers[0]
# Bypass to access FeatureLayer.query outside Jupyter Notebook (https://github.com/Esri/arcgis-python-api/issues/776)
FeatureLayer._token = property(lambda self: self._con.token)
bancos_query = bancos_flayer.query()


# Access item features
bancos_features = bancos_query.features


# Create DataFrame from features
df = pd.read_json(str(bancos_features))
dfk = list(df['attributes'][0].keys())[:-1]
dfv = []
for k, v in enumerate(df['attributes'].items()):
    dfv.append(list(df["attributes"][k].values())[:-1])
bancos_df_1 = pd.DataFrame(dfv, columns=dfk)
bancos_df_1.head()


# Check if exists and create backup folder to storage the original data downloaded from ArcGIS Portal
if not os.path.exists(os.path.join('data', '/home/douglas/FragaLab/AGOL/', 'backup')):
    os.mkdir(os.path.join('data', '/home/douglas/FragaLab/AGOL/', 'backup'))


# Assign variable to current timestamp to make unique file to add to portal
now = int(dt.datetime.now().timestamp())

# Copy original file to backup
bancos_df_1.to_csv(os.path.join('data', '/home/douglas/FragaLab/AGOL/', 'backup',
                                'csv_bancos_backup' + '_' + str(now) + '.csv'))


# Read the second csv set
csv2 = os.path.join('data', '/home/douglas/FragaLab/AGOL/python-arcgis/', 'bancos_2.csv')
bancos_df_2 = pd.read_csv(csv2)
bancos_df_2.head()


# Merge both DataFrames
updated_df = bancos_df_1.append(bancos_df_2)


# Eliminate possible duplicated entries
updated_df.drop_duplicates(subset='banco_id', keep='last', inplace=True)


# Check if exists and create folder to storage the updated csv file
if not os.path.exists(os.path.join('data', '/home/douglas/FragaLab/AGOL/', 'updated_csv_content')):
    os.mkdir(os.path.join('data', '/home/douglas/FragaLab/AGOL/', 'updated_csv_content'))


# Update csv file with the most recent information
updated_df.to_csv(os.path.join('data', '/home/douglas/FragaLab/AGOL/',
                               'updated_csv_content', 'bancos_updated.csv'))


# Update the Feature Collection
bancos_flayer_collection = FeatureLayerCollection.fromitem(bancos_item)


# Overwrite layer at ArcGIS OnLine
bancos_flayer_collection.manager.overwrite(os.path.join('data', '/home/douglas/FragaLab/AGOL/',
                                                        'updated_csv_content', 'bancos_updated.csv'))


# Success message
print(f'Layer "{bancos_item.title}" successfully updated!')
