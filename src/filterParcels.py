import csv
import json

import pandas as pd
import numpy as np

import geopandas as gpd
import fiona
from shapely.geometry import Point, Polygon
######################################################################################

'''taxpaname_1', 'school', 'city', 'propnam', 'taxpaadd_3', 'prop_cl',
'legal_3', 'st_dir', 'taxpacnty', 'unitid', 'res_com', 'taxpacity', 'objectid',
'legal_4', 'taxpaadd_4', 'county', 'legal_1', 'nscbd', 'st_type', 'taxpaadd_2',
'appraisaly', 'taxpazip', 'gis_acct', 'legal_5', 'busname', 'acct', 'totexempt',
'st_num', 'taxpaname_2', 'legal_2', 'taxpasta', 'mutiacct', 'taxpaadd_1',
'dacouncil', 'sptbcode', 'area_feet', 'st_name', 'mapsco_gr', 'bldg_cl'''

write_dataOut = open("%s%s" % (r"02_output/","parcels.csv"), 'w',newline='', encoding='utf-8')
writer_dataOut = csv.writer(write_dataOut)
writer_dataOut.writerow(["OBJECTID","PROP_CL","BLDG_CL","AREA_FT","X","Y"])

df_parcelTypes = pd.read_csv(str("%s%s" % (r"00_resources/","parcelTypes.csv")),encoding="utf-8")
parcelTypes_category = list(df_parcelTypes["TYPE"])
parcelTypes_desc = list(df_parcelTypes["DESC"])

#get the bounding box of the ROI for roi.json
roi_json = json.load(open("%s%s" % (r"00_resources/","roi.json")))
roi_bb = roi_json["roi_main"]
roi_bb_pt0 = roi_bb[0]
roi_bb_pt2 = roi_bb[1]
roi_bb_width = roi_bb_pt2[0] - roi_bb_pt0[0]
roi_bb_height = roi_bb_pt0[1] - roi_bb_pt2[1]
#make a polygon from the ROI bounding box
#The polygon will be used to determine if a parcel is in the ROI
roi_polygon = [
	(roi_bb_pt0),
	(roi_bb_pt0[0]+roi_bb_width,roi_bb_pt0[1]),
	(roi_bb_pt2),
	(roi_bb_pt0[0],roi_bb_pt2[1])
]
#Make the polygon using the Polygon methon from shapely.geometry
roi_polygon = Polygon(roi_polygon)

#Use fiona to read the geojson
with fiona.open(r"01_data/parcels.geojson") as src:
	for feature in src:
		properties = feature['properties']
		prop_cl = properties['prop_cl']
		try:
			prop_cl = " ".join(prop_cl.split(","))
			bldg_cl = " ".join(properties['bldg_cl'].split(","))
			area_feet = properties['area_feet']
			objectid = properties['objectid']
			prop_category = parcelTypes_category[parcelTypes_desc.index(prop_cl)]
			geometry = feature['geometry']
			geometry_type = geometry['type']
			if geometry_type.lower() == "multipolygon":
				geometry_coords = geometry['coordinates']
				'''cycle through the points in the parcel's polygons and calculate
				the interpolated center of the polygon'''
				pool_x = []
				pool_y = []
				for polygon in geometry_coords:
					for coords in polygon:
						for coord in coords:
							pool_x.append(float(coord[0]))
							pool_y.append(float(coord[1]))
				cx = np.mean(pool_x)
				cy = np.mean(pool_y)
				#Use the interpolated center of the parcel to make a point with shapely.geometry
				point = Point((cy,cx))
				#test if the point is in the ROI
				is_within = point.within(roi_polygon)
				#if the point is in the ROI, write the parcel to the csv
				if is_within:
					print(cy,cx)
					writer_dataOut.writerow([objectid,prop_cl,prop_category,bldg_cl,area_feet,cx,cy])
		except:
			pass

print("DONE")
