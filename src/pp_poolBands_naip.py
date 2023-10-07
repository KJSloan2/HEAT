import rasterio as rio
from rasterio.plot import show
import csv
import numpy as np
import json
######################################################################################
def normailize_val(val,d_min,d_max):
	return round(((val-d_min)/(d_max-d_min)),4)

def get_tiff_dimensions(file_path):
	try:
		with rio.open(file_path) as src:
			width = src.width
			height = src.height
		return width, height
	except Exception as e:
		print(f"Error: {e}")
		return None
######################################################################################
fNames_data = [
	"naip_roi_75211_2022.tif",
]
######################################################################################
roiRef_ = json.load(open("%s%s" % (r"00_resources\\","roi.json")))
######################################################################################
window_size = (8,8)
for fName in fNames_data:
	subRoiObj = roiRef_["sub_rois"][fName.split("_")[2]]
	roi_bb = subRoiObj["2pt_bb"]
	roi_bb_pt0 = roi_bb[0]
	roi_bb_pt2 = roi_bb[1]
	roi_bb_width = roi_bb_pt2[0] - roi_bb_pt0[0]
	roi_bb_height = roi_bb_pt0[1] - roi_bb_pt2[1]

	fPath = "%s%s" % (r"01_data\\",fName)
	with rio.open(fPath) as src:
		src_width = src.width
		src_height = src.height
		print(f"Width: {src_width} pixels")
		print(f"Height: {src_height} pixels")

		red_ = src.read(1)
		green_ = src.read(2)
		blue_ = src.read(3)

		bands_pooled = {"red":[],"green":[],"blue":[],"coords":[]}

		for i in range(0,src_height-(window_size[1]+1),window_size[1]):
			bands_pooled["red"].append([])
			bands_pooled["green"].append([])
			bands_pooled["blue"].append([])
			bands_pooled["coords"].append([])

			for j in range(0,src_width-(window_size[0]+1),window_size[0]):
				red_window = red_[i:i + window_size[0], j:j + window_size[1]]
				bands_pooled["red"][-1].append(int(np.mean(red_window)))

				green_window = green_[i:i + window_size[0], j:j + window_size[1]]
				bands_pooled["green"][-1].append(int(np.mean(green_window)))

				blue_window = blue_[i:i + window_size[0], j:j + window_size[1]]
				bands_pooled["blue"][-1].append(int(np.mean(blue_window)))

		data_size = [len(bands_pooled["red"][0]),len(bands_pooled["red"])]
		coord_step_width = roi_bb_width/data_size[0]
		coord_step_height = roi_bb_height/(data_size[1]*-1)

		coord_y = roi_bb_pt0[1]
		for i in range(0,data_size[0],1):
			coord_x = roi_bb_pt0[0]
			for j in range(0,data_size[1],1):
				try:
					bands_pooled["coords"][i].append([coord_x,coord_y])
				except:
					continue
				coord_x+=coord_step_width
			coord_y+=coord_step_height
######################################################################################
		output_path = "%s%s%s" % ("02_output\\",fName.split(".")[0],".json")
		with open(output_path, "w", encoding='utf-8') as output_json:
			output_json.write(json.dumps(bands_pooled, indent=2, ensure_ascii=False))
######################################################################################



