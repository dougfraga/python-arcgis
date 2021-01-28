# Upload Layer
author: ***Douglas Fraga Rodrigues***, 2021

Script to update an ArcGIS OnLine layer with new entries from a csv file.

### Requirements
1. Linux
1. Pipenv
1. Python 3.8

### Sample data
1. bancos_1.csv (initial set of registers)
1. bancos_2.csv (additional registers to be updated on layer)

### Instructions

1. Clone this repository to a local machine;
1. Open the load_updated_csv.py file and set the password (sent by email);
1. Check if the layer ID was set properly;
1. Run ```pipenv install```;
1. Run ```pipenv shell```
1. Run ```pipenv run python load_updated_csv.py```.

###Congrats!!! The layer is updated...
