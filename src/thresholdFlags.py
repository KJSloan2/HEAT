import geopandas as gpd
import numpy as np
import csv
import pandas as pd
from scipy.spatial import cKDTree

def normailize_val(val,d_min,d_max):
	return round(((val-d_min)/(d_max-d_min)),6)

df_ = pd.read_csv(str("%s%s" % (r"02_output\\","temporal_thermal_01.csv")),encoding="utf-8")
#X,Y,LST_F_DELTA,LST_NORM_DELTA,NDVI_DELTA,F1,LST_F_MEAN,NDVI_MEAN,NDVI_CLASS
df_x = list(df_["X"])
df_y = list(df_["Y"])
df_lstFMean = list(df_["LST_F_MEAN"])
df_lstNormDelta = list(df_["LST_NORM_DELTA"])

pnFlags_ = []
lstFMean_pos = []
lstFMean_neg = []
for i in range(len(df_lstNormDelta)):
	val = df_lstNormDelta[i]
	if val < 0:
		pnFlags_.append("N")
		lstFMean_neg.append(val)
	elif val > 0:
		pnFlags_.append("P")
		lstFMean_pos.append(val)
	elif val == 0:
		pnFlags_.append("Z")

min_lstFMean_pos = min(lstFMean_pos)
max_lstFMean_pos = max(lstFMean_pos)
min_lstFMean_neg = min(lstFMean_neg)
max_lstFMean_neg = max(lstFMean_neg)

dataOut_fileName = "temporal_thermal_flagged.csv"
write_dataOut = open("%s%s" % (r"02_output\\",dataOut_fileName), 'w',newline='', encoding='utf-8')
writer_dataOut = csv.writer(write_dataOut)
writer_dataOut.writerow(["X","Y","LST_NORM_DELTA","LST_NORM_DELTA_PN_FLAG","LST_NORM_NORM"])

for i in range(len(df_lstNormDelta)):
	x = df_x[i]
	y = df_y[i]
	val = df_lstNormDelta[i]
	pn = pnFlags_[i]
	if pn == "P":
		val_norm = normailize_val(val,min_lstFMean_pos,max_lstFMean_pos)
	elif pn == "N":
		val_norm = normailize_val(val,min_lstFMean_neg,max_lstFMean_neg)
	elif pn == "Z":
		val_norm = 0
	writer_dataOut.writerow([x,y,val,pn,val_norm*100])
