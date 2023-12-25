import csv
import json

import numpy as np

import rasterio as rio
from rasterio.plot import show
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
#set the names of all tifs to be analyized
fNames_data = [
	"l8_comp_lawrenceKs_2013.tif",
	"l8_comp_lawrenceKs_2015.tif",
	"l8_comp_lawrenceKs_2017.tif"
]
'''each tif name will be added to a txt file in the resoueces folder
The txt file will inform other scipts which json files to analyize'''
with open(r'00_resources/processed_tifs.txt', 'w') as file:
	for fName in fNames_data:
		file.write(f'{str(fName).split(".")[0]}\n')
	file.close()
######################################################################################
'''Set the pooling window size. This window will pool and summarize band data within it
by calculating the mean of the distribution. This will reduce the compuational load but
will also reduce fidelity if set too large'''
ui_poolingWindowSize = input("Set the size of the pooling window (in pixels) eg: 3x3: ")
ui_poolingWindowSize = str(ui_poolingWindowSize).split("x")
window_size = (int(ui_poolingWindowSize[0]), int(ui_poolingWindowSize[1]))
for fName in fNames_data:
	print(fName)
	fPath = "%s%s" % (r"01_data/",fName)
	with rio.open(fPath) as src:
		src_width = src.width
		src_height = src.height
		print(f"Width: {src_width} pixels")
		print(f"Height: {src_height} pixels")
		thermal_ = src.read(10)
		nir_ = src.read(5)
		red_ = src.read(4)
		green_ = src.read(3)
		blue_ = src.read(2)

		K1 = 774.8853
		K2 = 1321.0789
		#L_rad = (thermal_ * 0.0003342) + 0.1
		#corrected_rad = (thermal_ - 0.1) / 0.0003342
		#L_rad = (thermal_ * 0.0003342) + 0.1
		#LST = (K2 / np.log((K1 / thermal_) + 1))
		#LST_Celsius = LST - 273.15
		thermal_lst = (thermal_ - 273.15) * 1.8 + 32.0
		bands_pooled = {
			"thermal":[],"nir":[],
			"red":[],"green":[],"blue":[],
		}

		for i in range(0,src_height-(window_size[1]+1),window_size[1]):
			bands_pooled["thermal"].append([])
			bands_pooled["nir"].append([])
			bands_pooled["red"].append([])
			bands_pooled["green"].append([])
			bands_pooled["blue"].append([])

			for j in range(0,src_width-(window_size[0]+1),window_size[0]):
				nir_window = nir_[i:i + window_size[0], j:j + window_size[1]]
				bands_pooled["nir"][-1].append(np.mean(nir_window))

				thermal_window = thermal_lst[i:i + window_size[0], j:j + window_size[1]]
				bands_pooled["thermal"][-1].append(np.mean(thermal_window))

				red_window = red_[i:i + window_size[0], j:j + window_size[1]]
				bands_pooled["red"][-1].append(np.mean(red_window))

				green_window = green_[i:i + window_size[0], j:j + window_size[1]]
				bands_pooled["green"][-1].append(np.mean(green_window))

				blue_window = blue_[i:i + window_size[0], j:j + window_size[1]]
				bands_pooled["blue"][-1].append(np.mean(blue_window))

		bands_pooled["thermal"] = np.array(bands_pooled["thermal"])
		bands_pooled["nir"] = np.array(bands_pooled["nir"])
		bands_pooled["red"] = np.array(bands_pooled["red"])
		bands_pooled["green"] = np.array(bands_pooled["green"])
		bands_pooled["blue"] = np.array(bands_pooled["blue"])

		tempRanges = [
			[50,59.99],[60,69.99],[70,79.99],[80,89.99],
			[90,99.99],[100,109.99],[110,119.99]]

		output_ = {"lstf":[],"lst_range":[],"ndvi":[]}

		for i in range(len(bands_pooled["thermal"])):
			output_["lstf"].append([])
			output_["lst_range"].append([])
			output_["ndvi"].append([])
			for j in range(len(bands_pooled["thermal"][i])):
				NVDI = (bands_pooled["nir"][i][j] - bands_pooled["red"][i][j])/(bands_pooled["nir"][i][j] + bands_pooled["red"][i][j])
				lstf = bands_pooled["thermal"][i][j]
				lstRange = None
				for k in range(len(tempRanges)):
					tempRange = tempRanges[k]
					if tempRange[0] < lstf < tempRange[1]:
						lstRange = k
						break
				output_["lstf"][-1].append(round((float(lstf)),4))
				output_["lst_range"][-1].append(lstRange)
				output_["ndvi"][-1].append(round((float(NVDI)),4))
######################################################################################
		output_path = "%s%s%s" % (r"02_output/",fName.split(".")[0],".json")
		with open(output_path, "w", encoding='utf-8') as output_json:
			output_json.write(json.dumps(output_, indent=2, ensure_ascii=False))
######################################################################################
