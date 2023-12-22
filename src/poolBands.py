import numpy as np
import rasterio as rio
from rasterio.plot import show
import csv
import numpy as np
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
fNames_data = ["LIST OF TIF FILES"]
ui_poolingWindowSize = input("Set the size of the pooling window (in pixels) eg: 10x10: ")

#updare this to read from 00_resources/roi.json
roi_bb = [
	[-96.9479037353143,32.904886901377274],
	[-96.67479253222422,32.71222847422193]]

roi_bb_pt0 = roi_bb[0]
roi_bb_pt2 = roi_bb[1]
roi_bb_width = roi_bb_pt2[0] - roi_bb_pt0[0]
roi_bb_height = roi_bb_pt0[1] - roi_bb_pt2[1]
print(f"ROI_BB_Width: {roi_bb_width}")
print(f"ROI_BB_Height: {roi_bb_height}")
######################################################################################
ui_poolingWindowSize = str(ui_poolingWindowSize).split("x")
window_size = (int(ui_poolingWindowSize[0]), int(ui_poolingWindowSize[1]))
for fName in fNames_data:
	fPath = "%s%s" % (r"01_data\\",fName)
	#dimensions = get_tiff_dimensions(fPath)
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

    #update LST constants to read from TIF metadata
		K1 = 774.8853
		K2 = 1321.0789
		#L_rad = (thermal_ * 0.0003342) + 0.1
		#corrected_rad = (thermal_ - 0.1) / 0.0003342
		#L_rad = (thermal_ * 0.0003342) + 0.1
		LST = (K2 / np.log((K1 / thermal_) + 1))
		#LST_Celsius = LST - 273.15
		#thermal_lst = (LST - 273.15) * 1.8 + 32.0
		thermal_lst = (thermal_ - 273.15) * 1.8 + 32.0
		nir_pooled = []
		thermal_pooled = []
		red_pooled = []
		green_pooled = []
		blue_pooled = []
    
		bands_pooled = {"thermal":[],"nir":[],"red":[],"green":[],"blue":[],}
    
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
		#show(bands_pooled["thermal"], cmap='inferno', title='Land Surface Temperature (°C)')
		#parse_fPath = fPath.split("/")
		#fname = parse_fPath[-1].split(".")[0]
		#plt.savefig("%s%s" % (fname,'_thermal.jpg'), dpi=300, bbox_inches='tight')
		#plt.show()

		coord_step_width = roi_bb_width/int((src_width/window_size[0]))
		coord_step_height = (roi_bb_height/int((src_height/window_size[1])))*-1
		print(coord_step_width,coord_step_height)

		tempRanges = [
			[50,59.99],[60,69.99],[70,79.99],
			[80,89.99],[90,99.99],[100,109.99],
			[110,119.99]]

		output_ = {
			"lst_f":[],"ndvi":[],"coords":[],"idx":[]}

		for i in range(len(thermal_pooled)):
			coord_x = roi_bb_pt0[0]
			for j in range(len(thermal_pooled[i])):

				NVDI = (nir_pooled[i][j] - red_pooled[i][j])/(nir_pooled[i][j] - red_pooled[i][j])
				temp = thermal_pooled[i][j]
				tr = None
				for k in range(len(tempRanges)):
					tempRange = tempRanges[k]
					if tempRange[0] < temp < tempRange[1]:
						tr = k
						break
				writer.writerow([
					coord_x,coord_y,temp,nir_pooled[i][j],NVDI,
					red_pooled[i][j],green_pooled[i][j],blue_pooled[i][j],tr])
				
				coord_x+=coord_step_width
			coord_y+=coord_step_height

		with open("thermals.csv", mode='w', newline='') as file:
			writer = csv.writer(file)
			coord_y = roi_bb_pt0[1]
			for i in range(len(thermal_pooled)):
				coord_x = roi_bb_pt0[0]
				for j in range(len(thermal_pooled[i])):

					NVDI = (nir_pooled[i][j] - red_pooled[i][j])/(nir_pooled[i][j] - red_pooled[i][j])
					temp = thermal_pooled[i][j]
					tr = None
					for k in range(len(tempRanges)):
						tempRange = tempRanges[k]
						if tempRange[0] < temp < tempRange[1]:
							tr = k
							break
					writer.writerow([
						coord_x,coord_y,temp,nir_pooled[i][j],NVDI,
						red_pooled[i][j],green_pooled[i][j],blue_pooled[i][j],tr])
					
					coord_x+=coord_step_width
				coord_y+=coord_step_height
				
######################################################################################
