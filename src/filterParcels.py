import json
import geopandas as gpd
import fiona
import time
import numpy as np
import csv
import pandas as pd
from shapely.geometry import Point, Polygon

def calc_dist_3d(x1, y1, z1, x2, y2, z2):
    # Calculate the squared differences in x, y, and z coordinates
    dx = x2 - x1
    dy = y2 - y1
    dz = z2 - z1
    squared_distance = dx**2 + dy**2 + dz**2
    distance = squared_distance**0.5
    return distance

'''taxpaname_1', 'school', 'city', 'propnam', 'taxpaadd_3', 'prop_cl',
'legal_3', 'st_dir', 'taxpacnty', 'unitid', 'res_com', 'taxpacity', 'objectid',
'legal_4', 'taxpaadd_4', 'county', 'legal_1', 'nscbd', 'st_type', 'taxpaadd_2',
'appraisaly', 'taxpazip', 'gis_acct', 'legal_5', 'busname', 'acct', 'totexempt',
'st_num', 'taxpaname_2', 'legal_2', 'taxpasta', 'mutiacct', 'taxpaadd_1',
'dacouncil', 'sptbcode', 'area_feet', 'st_name', 'mapsco_gr', 'bldg_cl'''

df_parcelTypes = pd.read_csv(str("%s%s" % (r"00_resources\\","parcelTypes.csv")),encoding="utf-8")
parcelTypes_category = list(df_parcelTypes["TYPE"])
parcelTypes_desc = list(df_parcelTypes["DESC"])

df_zipcodeRef = pd.read_csv(str("%s%s" % (r"00_resources\\","selectZctaCoords.csv")),encoding="utf-8")
zipcodeRef_zipcode = list(df_zipcodeRef["GEOID"])
zipcodeRef_lat = list(df_zipcodeRef["LAT"])
zipcodeRef_lon = list(df_zipcodeRef["LON"])
######################################################################################

with open(str("%s%s" % (r"01_data\parcels\\","DallasZipCodes_2018.geojson")), 'r') as geojson_file:
	geojson_data = json.load(geojson_file)
# Access GeoJSON features
features = geojson_data['features']
zipcode_geometry = {}
for feature in features:
	properties = feature['properties']
	zc = properties["ZipCode"]
	zipcode_geometry[zc] = {"polygon":[]}
	geometry = feature['geometry']
	polygon_coords = geometry["coordinates"]

	for i in range(len(polygon_coords)):
		for j in range(len(polygon_coords[i])):
			coords = polygon_coords[i][j]
			coord = (coords[0],coords[1])
			zipcode_geometry[zc]["polygon"].append(coord)
######################################################################################
roi_bb = [
	[-96.9479037353143,32.904886901377274],
	[-96.67479253222422,32.71222847422193]]

divisions_ = [6,6]
roi_bb_pt0 = roi_bb[0]
roi_bb_pt2 = roi_bb[1]
roi_bb_width = roi_bb_pt2[0] - roi_bb_pt0[0]
roi_bb_height = roi_bb_pt0[1] - roi_bb_pt2[1]
step_width = (roi_bb_width/divisions_[0])
step_height = (roi_bb_height/divisions_[1])*-1

roi_polygon = [
	(roi_bb_pt0),
	(roi_bb_pt0[0]+roi_bb_width,roi_bb_pt0[1]),
	(roi_bb_pt2),
	(roi_bb_pt0[0],roi_bb_pt2[1])
]

tabulationAreas_ = {}
coord_y = roi_bb_pt0[1]
tabulationAreaId = 0
for i in range(0,divisions_[1],1):
	coord_x = roi_bb_pt0[0]
	for j in range(0,divisions_[0],1):
		#print(coord_x,coord_y)
		tabulationAreas_[tabulationAreaId]={"centroid":[coord_x,coord_y]}
		tabulationAreaId+=1
		coord_x+=step_width
	coord_y+=step_height
taKeys_ = list(tabulationAreas_.keys())
######################################################################################
df_parcels = pd.read_csv(str("%s%s" % (r"02_output\\","parcelData.csv")),encoding="utf-8")
#OBJECTID,PROP_CL,PROP_CAT,BLDG_CL,AREA_FT,X,Y
parcels_objid = list(df_parcels["OBJECTID"])
parcels_propCl = list(df_parcels["PROP_CL"])
parcels_propCt = list(df_parcels["PROP_CAT"])
parcels_bldgCl = list(df_parcels["BLDG_CL"])
parcels_area = list(df_parcels["AREA_FT"])
parcels_cx = list(df_parcels["X"])
parcels_cy = list(df_parcels["Y"])

write_dataOut = open("%s%s" % (r"02_output\\","parcelData_filtered.csv"), 'w',newline='', encoding='utf-8')
writer_dataOut = csv.writer(write_dataOut)
writer_dataOut.writerow(["OBJECTID","PROP_CL","PROP_CT","BLDG_CL","AREA_FT","TABULATION_AREA","LON","LAT"])

for i in range(len(parcels_objid)):
	cx = parcels_cx[i]
	cy = parcels_cy[i]
	point = Point((cx,cy))
	polygon = Polygon(roi_polygon)
	is_within = point.within(polygon)
	if is_within:
		objectid = parcels_objid[i]
		prop_cl = parcels_propCl[i]
		bldg_cl = parcels_bldgCl[i]
		area = parcels_area[i]
		prop_ct = parcels_propCt[i]
		try:
			store_dist = []
			for taKey,taObj in tabulationAreas_.items():
				taObj_centroid = taObj["centroid"]
				dist = calc_dist_3d(cx, cy, 0, taObj_centroid[0], taObj_centroid[1], 0)
				store_dist.append(dist)
			sorted_dist = np.argsort(store_dist)
			ta = taKeys_[sorted_dist[0]]
			writer_dataOut.writerow([objectid,prop_cl,prop_ct,bldg_cl,area,ta,cx,cy])

		except:
			pass
print("DONE")
