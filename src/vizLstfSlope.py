import json
import numpy as np
import pandas as pd
import plotly.figure_factory as ff
import plotly.express as px
from matplotlib import pyplot as plt

######################################################################################
def calc_delta_threshold(d):
	pool_d_pos = []
	pool_d_neg = []
	for i in range(len(d)):
		for j in range(len(d[i])):
			val = d[i][j]
			if val > 0:
				pool_d_pos.append(val)
			else:
				pool_d_neg.append(val)
	threshold_pos = np.mean(pool_d_pos)+np.std(pool_d_pos)
	threshold_neg = np.mean(pool_d_neg)+np.std(pool_d_neg)
	return threshold_pos,threshold_neg;

def delta_threshold_filter(d,thresh_pos,thresh_neg):
	filtered_pos = []
	filtered_neg = []
	count_pos,count_neg,count_zero = 0,0,0
	for i in range(len(d)):
		for j in range(len(d[i])):
			val = d[i][j]
			if val > 0:
				count_pos+=1
				if val >= thresh_pos:
					filtered_pos.append([i,j])
			elif val == 0:
				count_zero+=1
			elif val < 0:
				count_neg+=1
				if val <= thresh_neg:
					filtered_neg.append([i,j])
	return filtered_pos,filtered_neg,count_pos,count_neg,count_zero;

def normailize_val(val,d_min,d_max):
	return round(((val-d_min)/(d_max-d_min)),6)
######################################################################################

ui_band = "lstf_slope"
data_json = json.load(open("%s%s" % (r"02_output/","temporal_deltas.json")))
threshold_lstfDelta = calc_delta_threshold(data_json[ui_band])
print(threshold_lstfDelta)
filtered_data = delta_threshold_filter(data_json[ui_band],threshold_lstfDelta[0],threshold_lstfDelta[1])

pts_pos = filtered_data[2]
pts_neg = filtered_data[3]
pts_zero = filtered_data[4]
pts_total = sum([pts_pos,pts_neg,pts_zero])

prct_pos = (pts_pos/pts_total)*100
prct_neg = (pts_neg/pts_total)*100

prct_aboveThreshold_pos = (len(filtered_data[0])/pts_total)*100
prct_aboveThreshold_neg = (len(filtered_data[1])/pts_total)*100

print(prct_aboveThreshold_pos,prct_aboveThreshold_neg)
colors_ = []
sizes_ = []
filtered_d = []
for idx_lst,c in zip([filtered_data[0],filtered_data[1]],[(1,0,0),(0,0,1)]):
	for idx in idx_lst:
		lstf_slope = data_json[ui_band][idx[0]][idx[1]]
		lstf_mean = data_json["lstf_mean"][idx[0]][idx[1]]
		colors_.append(c)
		sizes_.append(abs(lstf_slope))
		filtered_d.append([data_json["coord"][idx[0]][idx[1]][0],data_json["coord"][idx[0]][idx[1]][1],abs(lstf_slope),c,lstf_mean,lstf_slope])

output_columns = ["LAT","LON","R","COLOR","LSTF_MEAN","LSTF_SLOPE"]
df_ = pd.DataFrame(filtered_d, columns=output_columns)
fig = px.scatter_mapbox(
	df_,
	lat="LAT",lon="LON",
	#hover_name="CD",
	hover_data=["LSTF_MEAN","LSTF_SLOPE"],color="LSTF_SLOPE",
	#color_continuous_scale=color_scale,
	size="R",zoom=12,
	height=1000,width=2500)

fig.update_geos(center=dict(lon=np.mean(df_["LON"]), lat=np.mean(df_["LAT"])))
fig.update_layout(mapbox_style="carto-darkmatter")
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
fig.show()
