import csv
import json

import pandas as pd
import numpy as np

import fiona
######################################################################################

'''taxpaname_1', 'school', 'city', 'propnam', 'taxpaadd_3', 'prop_cl',
'legal_3', 'st_dir', 'taxpacnty', 'unitid', 'res_com', 'taxpacity', 'objectid',
'legal_4', 'taxpaadd_4', 'county', 'legal_1', 'nscbd', 'st_type', 'taxpaadd_2',
'appraisaly', 'taxpazip', 'gis_acct', 'legal_5', 'busname', 'acct', 'totexempt',
'st_num', 'taxpaname_2', 'legal_2', 'taxpasta', 'mutiacct', 'taxpaadd_1',
'dacouncil', 'sptbcode', 'area_feet', 'st_name', 'mapsco_gr', 'bldg_cl'''

df_parcelTypes = pd.read_csv(str("%s%s" % (r"00_resources/","parcelTypes.csv")),encoding="utf-8")
parcelTypes_category = list(df_parcelTypes["TYPE"])
parcelTypes_desc = list(df_parcelTypes["DESC"])

#get the bounding box of the ROI for roi.json
roi_json = json.load(open("%s%s" % (r"00_resources/","roi.json")))
roi_bb = [list(map(float, roi_json["roi_main"][0])), list(map(float, roi_json["roi_main"][1]))]

bb_center = [(roi_bb[0][0] + roi_bb[1][0])/2, (roi_bb[0][1] + roi_bb[1][1])/2]
roi_bb_pt0 = roi_bb[0]
roi_bb_pt2 = roi_bb[1]
#roi_bb_width = roi_bb_pt2[0] - roi_bb_pt0[0]
#roi_bb_height = roi_bb_pt0[1] - roi_bb_pt2[1]

def is_point_in_bb(bb, pt):
    return bb[0][1] <= pt[1] <= bb[1][1] and bb[0][0] >= pt[0] >= bb[1][0]

filteredParcels = {}
#Use fiona to read the geojson
with fiona.open(r"01_data/parcels.geojson") as src:
	for feature in src:
		properties = feature['properties']
		prop_cl = properties['prop_cl']
		try:
			prop_cl = " ".join(prop_cl.split(","))
			bldg_cl = " ".join(properties['bldg_cl'].split(","))
			area_ft = properties['area_feet']
			objectid = properties['objectid']
			prop_category = parcelTypes_category[parcelTypes_desc.index(prop_cl)]
			geometry = feature['geometry']
			geometry_type = geometry['type']
			if geometry_type.lower() == "multipolygon":
				geometry_coords = geometry['coordinates']
				#cycle through the points in the parcel's polygons and calculate
				#the interpolated center of the polygon
				pool_y = []
				pool_x = []
				for polygon in geometry_coords:
					for coords in polygon:
						for coord in coords:
							pool_y.append(float(coord[1]))
							pool_x.append(float(coord[0]))
				cx = np.mean(pool_x)
				cy = np.mean(pool_y)
				parcelCenter = [cy,cx]
				#test if the point is in the ROI+
				#if the point is in the ROI, write the parcel to the csv
				if is_point_in_bb(roi_bb, parcelCenter):
					print(cy,cx)
					filteredParcels[objectid] = {
						"properties":{
							"prop_cl":prop_cl,
							"bldb_cl":bldg_cl,
							"area_ft":area_ft,
							"calculations":{"lst":None,"ndvi":None}
						},
						"geometry":{
							"center":{"type":"point","coords":[cy,cx]},
							"boundary":{"type":"multipolygon","coords":geometry['coordinates']}
						}
					}
		except:
			pass

with open(r"02_output/filteredParcels.json", "w", encoding='utf-8') as output_json:
	output_json.write(json.dumps(filteredParcels, indent=2, ensure_ascii=False))

print("DONE")
