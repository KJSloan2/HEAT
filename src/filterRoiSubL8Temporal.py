import json
from shapely.geometry import Point, Polygon
import re
import csv
import pandas as pd
######################################################################################
df_parcelsFiltered = pd.read_csv("%s%s" % (r"02_output\\","parcelData_filtered.csv"),encoding="utf-8")
#"OBJECTID","PROP_CL","PROP_CT","BLDG_CL","AREA_FT","TABULATION_AREA","LON","LAT"
parcelsFiltered_objId = list(df_parcelsFiltered["OBJECTID"])
parcelsFiltered_propCl = list(df_parcelsFiltered["PROP_CL"])
parcelsFiltered_propCt = list(df_parcelsFiltered["PROP_CT"])
parcelsFiltered_bldgCl = list(df_parcelsFiltered["BLDG_CL"])
parcelsFiltered_area = list(df_parcelsFiltered["AREA_FT"])
parcelsFiltered_lat = list(df_parcelsFiltered["LAT"])
parcelsFiltered_lon = list(df_parcelsFiltered["LON"])

data_temporal = json.load(open("%s%s" % (r"02_output\\","temporal_deltas.json")))
roiRef_ = json.load(open("%s%s" % (r"00_resources\\","roi.json")))
roiRef_["sub_rois"] = {}
######################################################################################
rois_ = {}
with open(str("%s%s" % (r"00_resources\\","selectZctaCoords.txt")),encoding="utf-8") as read_zipcodes:
	zipcodes_lines = read_zipcodes.readlines()
	for l in zipcodes_lines:
		split_l = l.split(",")

		zc = split_l[0].strip()
		cx = float(split_l[2].strip())
		cy = float(split_l[1].strip())
		zone = split_l[3].strip()
		print(zone)

		offset_x = 0.02
		offset_y = 0.02

		roi_polygon = [
			(cx-offset_x,cy+offset_y),
			(cx+offset_x,cy+offset_y),
			(cx+offset_x,cy-offset_y),
			(cx-offset_x,cy-offset_y)
		]
		
		roiRef_["sub_rois"][zc] = {
			"zone":zone,
			"interp_center":[cx,cy],
			"2pt_bb":[
				[cx-offset_x,cy+offset_y],
				[cx+offset_x,cy-offset_y]],
			"polygon":roi_polygon,
		}

		rois_[zc] = {
			"zone":zone,"polygon":roi_polygon,
			"lstf_mean":[],"ndvi_mean":[],
			"lstn_delta":[],"lstf_delta":[],
			"ndvi_delta":[],"ndvi_class":[],
			"coords":[],
			"parcels":{
				"prop_cl":[],"prop_ct":[],"bldg_cl":[],
				"area":[],"coords":[]}
			}
		
with open("%s%s" % (r"00_resources\\","roi.json"), "w", encoding='utf-8') as output_roiRef:
	output_roiRef.write(json.dumps(roiRef_, indent=2, ensure_ascii=False))
######################################################################################
for i in range(len(parcelsFiltered_objId)):
	cx = parcelsFiltered_lon[i]
	cy = parcelsFiltered_lat[i]
	point = Point((cx,cy))
	for roiId,roiObj in rois_.items():
		polygon = Polygon(roiObj["polygon"])
		is_within = point.within(polygon)
		if is_within:
			rois_[roiId]["parcels"]["coords"].append([cx,cy])
			rois_[roiId]["parcels"]["prop_cl"].append(parcelsFiltered_propCl[i])
			rois_[roiId]["parcels"]["area"].append(parcelsFiltered_area[i])
			break
######################################################################################
for i in range(len(data_temporal["coords"])):
	coords = data_temporal["coords"][i]
	cx = coords[0]
	cy = coords[1]
	point = Point((cx,cy))
	for roiId,roiObj in rois_.items():
		polygon = Polygon(roiObj["polygon"])
		is_within = point.within(polygon)
		if is_within:
			rois_[roiId]["coords"].append(coords)
			rois_[roiId]["lstf_mean"].append(data_temporal["lstf_mean"][i])
			rois_[roiId]["ndvi_mean"].append(data_temporal["ndvi_mean"][i])
			rois_[roiId]["lstn_delta"].append(data_temporal["lstn_delta"][i])
			rois_[roiId]["lstf_delta"].append(data_temporal["lstf_delta"][i])
			rois_[roiId]["ndvi_delta"].append(data_temporal["ndvi_delta"][i])
			break
######################################################################################
with open("%s%s" % ("02_output\\","temporal_selectRois.json"), "w", encoding='utf-8') as output_json:
	output_json.write(json.dumps(rois_, indent=2, ensure_ascii=False))

write_dataOut = open("%s%s" % (r"02_output\\","selectRois_roiStats.csv"), 'w',newline='', encoding='utf-8')
writer_dataOut = csv.writer(write_dataOut)
writer_dataOut.writerow(["ROI_ID","ROI_ZONE","X","Y","LSTF_MEAN","LSTF_DELTA","LSTN_DELTA","NDVI_MEAN","NDVI_DELTA"])

for roiId,roiObj in rois_.items():
	for i in range(len(roiObj["coords"])):
		writer_dataOut.writerow([
			roiId,roiObj["zone"],
			roiObj["coords"][i][0],
			roiObj["coords"][i][1],
			roiObj["lstf_mean"][i],
			roiObj["lstf_delta"][i],
			roiObj["lstn_delta"][i],
			roiObj["ndvi_mean"][i],
			roiObj["ndvi_delta"][i]])
		
print("DONE")
