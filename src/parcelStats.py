import csv

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

df_temporal = pd.read_csv(str("%s%s" % (r"02_output\\","temporal_thermal_01.csv")),encoding="utf-8")
#X,Y,LST_F_DELTA,LST_NORM_DELTA,NDVI_DELTA,F1,LST_F_MEAN,NDVI_MEAN,NDVI_CLASS
temporal_x = list(df_temporal["X"])
temporal_y = list(df_temporal["Y"])
temporal_lstFMean = list(df_temporal["LST_F_MEAN"])
temporal_ = list(df_temporal["LST_F_MEAN"])

df_parcels = pd.read_csv(str("%s%s" % (r"02_output\\","parcelData_filtered.csv")),encoding="utf-8")
#OBJECTID,PROP_CL,PROP_CAT,BLDG_CL,AREA_FT,X,Y
parcels_objid = list(df_parcels["OBJECTID"])
parcels_propCl = list(df_parcels["PROP_CL"])
parcels_propCt = list(df_parcels["PROP_CT"])
parcels_bldgCl = list(df_parcels["BLDG_CL"])
parcels_area = list(df_parcels["AREA_FT"])
parcels_x = list(df_parcels["LON"])
parcels_y = list(df_parcels["LAT"])

l8_points = []
for i in range(len(temporal_x)):
	cx = temporal_x[i]
	cy = temporal_y[i]
	l8_points.append((cx,cy))
kdtree = cKDTree(l8_points)

dataOut_fileName = "parcelStats.csv"
write_dataOut = open("%s%s" % (r"02_output\\",dataOut_fileName), 'w',newline='', encoding='utf-8')
writer_dataOut = csv.writer(write_dataOut)
writer_dataOut.writerow(["OBJECTID","PROP_CL","PROP_CT","BLDG_CL","AREA_FT","LON","LAT","LST_F_MEAN"])
for i in range(len(parcels_objid)):
	qx = parcels_x[i]
	qy = parcels_y[i]
	query_point = (qx, qy)

	cp_idx = kdtree.query(query_point)[1]
	#closest_point = parcel_centroids[closest_point_index]
	lstFMean = temporal_lstFMean[cp_idx]
	writer_dataOut.writerow([
		parcels_objid[i],
		parcels_propCl[i],
		parcels_propCt[i],
		parcels_bldgCl[i],
		parcels_area[i],
		qx,qy,
		lstFMean
		])
	
print("DONE")
