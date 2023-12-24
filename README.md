# Urban Heat Island Analysis
## Process
![Process Overview]([[https://example.com/path/to/your/image.jpg])

## Scripts

### lstNormalize.py

- This will normalize land surface temperature (LST) calculations across all years of the analysis period. This  process was added to reduce the amount of noise caused by fluctuations in annual temperatures. Land surface temperatures will be returned as values between zero and one.

### parcelJson2Csv.py

- This script simplifies large GIS parcel datasets into more easily manageable CSV formats. For the purpose of this project in its current state, the polygon outlines of parcels are not needed. Therefore to reduce the amount of data processed, we can represent a parcel's location with only its interpolated center. This script reads the GIS parcel geoJson and calculates the interpolated center of the parcel from the coordinates of the parcel's polygon perimeter.

### filterParcels.py

- These are used if the project incorporates GIS parcel data.The tools remove parcels whose interpolated centers fall outside the ROI bounding box. These tools were made to reduce the volume of GIS parcel data processed by removing parcels that fall outside the scope of the project. Only parcels within the ROI bounding box will be analyzed.

### filterRoiSubL8Temporal.py
- This is used if the project breaks down the main ROI into smaller, "sub-ROIs". For example, if the overall project scope encompasses an entire city but there is a particular neighborhood or area you wish to isolate, add a sub-ROI to the roi.json. The bounding box coordinates of the sub-ROI will be used to isolate temporally analyzed data within the sub-ROI(s) so it can be visualized and analyzed independent form the main ROI.



