import numpy as np
import json
######################################################################################
def normailize_val(val,d_min,d_max):
	return round(((val-d_min)/(d_max-d_min)),6)
######################################################################################
fNames_data = ["LIST OF TIF FILES"]
######################################################################################
pool_lst=[]
for fName in fNames_data:
	fPath = "%s%s" % (r"02_output\\",fName)
	data_ = json.load(open(fPath))
	for val in data_["lst_f"]:
		if len(pool_lst) == 0:
			pool_lst.append(val)
		else:
			if val > max(pool_lst) or val < min(pool_lst):
				pool_lst.append(val)

lst_min = min(pool_lst)
lst_max = max(pool_lst)

for fName in fNames_data:
	print(fName)
	fPath = "%s%s" % (r"02_output\\",fName)
	data_ = json.load(open(fPath))
	data_["lst_norm"] = []
	for val in data_["lst_f"]:
		data_["lst_norm"].append(normailize_val(val,lst_min,lst_max))
		
	output_path = "%s%s" % ("02_output\\",fName)
	with open(output_path, "w", encoding='utf-8') as output_json:
		output_json.write(json.dumps(data_, indent=2, ensure_ascii=False))
		
######################################################################################
