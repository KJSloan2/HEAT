import numpy as np
import json
######################################################################################
def normailize_val(val,d_min,d_max):
	return round(((val-d_min)/(d_max-d_min)),6)
######################################################################################
fNames_data = []
with open(r"00_resources/processed_tifs.txt", 'r') as file:
	for line in file:
		fNames_data.append(line.strip()+".json")

######################################################################################
temporalData_ = {}
data_ = json.load(open("%s%s" % (r"02_output/",fNames_data[0])))
data_lst = data_["lstf"]
######################################################################################
data_combined = {"lstf":[],"lstn":[],"ndvi":[]}

for i in range(len(data_lst)):
	for key,obj in data_combined.items():
		obj.append([])
		for j in range(len(data_lst[0])):
			obj[-1].append([])

roi_json = json.load(open("%s%s" % (r"00_resources/","roi.json")))
roi_bb = roi_json["roi_main"]

roi_bb_pt0 = roi_bb[0]
roi_bb_pt2 = roi_bb[1]
roi_bb_width = roi_bb_pt2[0] - roi_bb_pt0[0]
roi_bb_height = roi_bb_pt0[1] - roi_bb_pt2[1]
data_size = [len(data_lst[0]),len(data_lst)]
coord_step_width = roi_bb_width/data_size[0]
coord_step_height = roi_bb_height/(data_size[1]*-1)
print(data_size,coord_step_width,coord_step_height)
######################################################################################
for fName in fNames_data:
	fPath = "%s%s" % (r"02_output/",fName)
	data_ = json.load(open(fPath))
	for i in range(len(data_["lstf"])):
		for j in range(len(data_["lstf"][i])):
			data_combined["lstf"][i][j].append(float(data_["lstf"][i][j]))
			data_combined["lstn"][i][j].append(float(data_["lst_norm"][i][j]))
			data_combined["ndvi"][i][j].append(float(data_["ndvi"][i][j]))
######################################################################################
ndviRanges_ = [
	[-2,-0.28],[-0.28,0.015],
	[0.015,0.14],[0.14,0.18],
	[0.18,0.27],[0.27,0.36],
	[0.36,0.74],[0.74,2]
]
######################################################################################
output_ = {
	"lstf_mean":[],"lstf_delta":[],"lstf_skew":[],
	"lstn_delta":[],"lstf_slope":[],
	"ndvi_mean":[],"ndvi_delta":[],"ndvi_skew":[],"ndvi_class":[],
	"ndvi_slope":[],
	"coord":[]
}
######################################################################################
coord_y = roi_bb_pt0[1]
for i in range(len(data_combined["lstn"])):
	for key,obj in output_.items():
		obj.append([])
	coord_x = roi_bb_pt0[0]
	for j in range(len(data_combined["lstn"][i])):
		try:
			lstn_deltas = []
			lstf_deltas = []
			ndvi_deltas = []

			lstn = data_combined["lstn"][i][j]
			ndvi = data_combined["ndvi"][i][j]
			x = list(range(0, len(lstn)))
			lstf_coefficients = np.polyfit(x, lstn, 1)
			lstf_m = lstf_coefficients[0]
			lstf_b = lstf_coefficients[1]

			ndvi_coefficients = np.polyfit(x, ndvi, 1)
			ndvi_m = ndvi_coefficients[0]
			ndvi_b = ndvi_coefficients[1]

			for k in range(1,len(data_combined["lstn"][i][j])-1,1):
				lstn_deltas.append(data_combined["lstn"][i][j][k]-data_combined["lstn"][i][j][k-1])
				lstf_deltas.append(data_combined["lstf"][i][j][k]-data_combined["lstf"][i][j][k-1])
				ndvi_deltas.append(data_combined["ndvi"][i][j][k]-data_combined["ndvi"][i][j][k-1])
			lstn_delta = np.mean(lstn_deltas)
			lstf_delta = np.mean(lstf_deltas)
			ndvi_delta = np.mean(ndvi_deltas)
			lstf_mean = np.mean(data_combined["lstf"][i][j])
			ndvi_mean = np.mean(data_combined["ndvi"][i][j])

			ndvi_class = None
			
			output_["lstf_mean"][-1].append(lstf_mean)
			lstf_skew = np.mean(((data_combined["lstf"][i][j] - lstf_mean) / np.std(data_combined["lstf"][i][j])) ** 3)
			#lstn_skew = np.mean(((data_combined["lstn"][i][j] - lstn_mean) / np.std(data_combined["lstn"][i][j])) ** 3)
			ndvi_skew = np.mean(((data_combined["ndvi"][i][j] - ndvi_mean) / np.std(data_combined["ndvi"][i][j])) ** 3)

			#print(data_combined["lstf"][i][j],lstf_mean,lstf_delta,lstn_delta,lstf_skew)

			output_["ndvi_mean"][-1].append(ndvi_mean)
			output_["lstn_delta"][-1].append(lstn_delta)
			#output_["lstn_skew"][-1].append(lstn_skew)
			output_["lstf_delta"][-1].append(lstf_delta)
			output_["lstf_skew"][-1].append(lstf_skew)
			output_["ndvi_delta"][-1].append(ndvi_delta)
			output_["ndvi_skew"][-1].append(ndvi_skew)
			output_["ndvi_class"][-1].append(ndvi_class)
			output_["lstf_slope"][-1].append(lstf_m)
			output_["ndvi_slope"][-1].append(ndvi_m)
			output_["ndvi_class"][-1].append(ndvi_class)
			output_["coord"][-1].append([coord_x,coord_y])
			
		except:
			continue
		coord_x+=coord_step_width
	coord_y+=coord_step_height
######################################################################################
output_path = "%s%s" % (r"02_output/","temporal_deltas.json")
with open(output_path, "w", encoding='utf-8') as output_json:
	output_json.write(json.dumps(output_, ensure_ascii=False))
	
print("DONE")
