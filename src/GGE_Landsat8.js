// Note that the input to simpleComposite is raw data.
//Update the geoid, year, startDateTime and endDateTime to your project specifications
var geoid = "SOCAL";
var year = '2023';
var startDateTime = year+'-06-01T10:00:00'; // Start date and time in UTC
var endDateTime = year+'-09-01T15:00:00';   // End date and time in UTC
var l8_filtered = ee.ImageCollection('LANDSAT/LC08/C02/T1')
  .filterDate(startDateTime, endDateTime);

// The asFloat parameter gives floating-point TOA output instead of
// the UINT8 outputs of the default simpleComposite().
var composite = ee.Algorithms.Landsat.simpleComposite({
  collection: l8_filtered,
  asFloat: true
});

function calculateCenter(lat1, lon1, lat2, lon2) {
  var centerLat = (lat1 + lat2) / 2;
  var centerLon = (lon1 + lon2) / 2;
  return [centerLat, centerLon];
}

var coords = [[39.05960379594523, -95.46043592409647],[38.861841857576934, -95.03653486073641]];

var point1 = coords[0];
var point2 = coords[1];
var mapCenter = calculateCenter(point1[1], point1[0], point2[1], point2[0]);


Map.setCenter(mapCenter[0],mapCenter[1], 10);
var roi = ee.Geometry.BBox(
  coords[0][1],coords[0][0],
  coords[1][1],coords[1][0]
  );
  
// Display a composite with a band combination chosen from:
// https://landsat.usgs.gov/how-do-landsat-8-band-combinations-differ-landsat-7-or-landsat-5-satellite-data
var viz = {bands: ['B5','B4','B3'], max: [0.3, 0.3, 0.3]};
Map.addLayer(composite, viz, 'ee.Algorithms.Landsat.simpleComposite');

// For reference, below is the code equivalent to
// the server-side implementation of ee.Algorithms.simpleComposite().

function TOAComposite(collection,
                      asFloat,
                      percentile,
                      cloudScoreRange,
                      maxDepth) {

  // Select a sufficient set of images, and compute TOA and cloudScore.
  var prepared =
      ee.Algorithms.Landsat.pathRowLimit(collection, maxDepth, 4 * maxDepth)
                   .map(ee.Algorithms.Landsat.TOA)
                   .map(ee.Algorithms.Landsat.simpleCloudScore);

  // Determine the per-pixel cloud score threshold.
  var cloudThreshold = prepared.reduce(ee.Reducer.min())
                               .select('cloud_min')
                               .add(cloudScoreRange);

  // Mask out pixels above the cloud score threshold, and update the mask of
  // the remaining pixels to be no higher than the cloud score mask.
  function updateMask(image) {
    var cloud = image.select('cloud');
    var cloudMask = cloud.mask().min(cloud.lte(cloudThreshold));
    // Drop the cloud band and QA bands.
    image = image.select('B[0-9].*');
    return image.mask(image.mask().min(cloudMask));
  }
  var masked = prepared.map(updateMask);

  // Take the (mask-weighted) median (or other percentile)
  // of the good pixels.
  var result = masked.reduce(ee.Reducer.percentile([percentile]));

  // Force the mask up to 1 if it's non-zero, to hide L7 SLC artifacts.
  result = result.mask(result.mask().gt(0));

  // Clean up the band names by removing the suffix that reduce() added.
  var badNames = result.bandNames();
  var goodNames = badNames.map(
          function(x) { return ee.String(x).replace('_[^_]*$', ''); });
  result = result.select(badNames, goodNames);

  if (!asFloat) {
    // Scale reflective bands by 255, and offset thermal bands by -100.
    // These lists are only correct for Landsat 8; different lists are
    // used for the other instruments.
    var scale = [ 255, 255, 255, 255, 255, 255, 255, 255, 255, 1, 1 ];
    var offset = [ 0, 0, 0, 0, 0, 0, 0, 0, 0, -100, -100 ];
    result = result.multiply(scale).add(offset).round().uint8();
  }
  return result;
}

var firstImage = l8_filtered.first();
//var imageProperties = firstImage.getInfo();
var imageMetadata = firstImage.toDictionary();
print(imageMetadata);

var getImageMetadata = function(image) {
  var date = ee.Date(image.get('system:time_start'));
  var cloudCover = ee.Number(image.get('CLOUD_COVER'));
  return ee.Feature(null, {'date': date, 'cloud_cover': cloudCover});
};

Export.image.toDrive({
  image: composite,
  description: "l8_comp_kansas_2023",
  folder: 'l8_exports_kansas', // Specify your folder in Google Drive
  region: roi,
  scale: 30, // Adjust scale as needed
  maxPixels: 1e9, // Adjust as needed
  fileFormat: 'GEOTIFF'
});
