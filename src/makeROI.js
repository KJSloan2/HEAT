let previousDownloadLink = null;
mapboxgl.accessToken = 'YOUR MAPBOX TOKEN';
//mapbox://styles/mapbox/satellite-v9
//mapbox.mapbox-streets-v8
const map = new mapboxgl.Map({
    container: 'map', // container ID
    // Choose from Mapbox's core styles, or make your own style with Mapbox Studio
    style: 'mapbox://styles/mapbox/light-v11', // style URL
    center: [-96.84985325278977,32.845989192711265], // starting position [lng, lat]
    zoom: 12 // starting zoom
});

// Add the control to the map.
map.addControl(
    new MapboxGeocoder({
    accessToken: mapboxgl.accessToken,
    mapboxgl: mapboxgl
    })
);
const draw = new MapboxDraw({displayControlsDefault: false,
    // Select which mapbox-gl-draw control buttons to add to the map.
    controls: {
        polygon: true,
        trash: true
    },
    // Set mapbox-gl-draw to draw by default.
    // The user does not have to click the polygon control button first.
    defaultMode: 'draw_polygon'
});
map.addControl(draw);
map.on('draw.create', updateArea);
map.on('draw.delete', updateArea);
map.on('draw.update', updateArea);

function updateArea(e) {
    // Remove the previous download link if it exists
    if (previousDownloadLink) {
        previousDownloadLink.remove();
    }

    const queryResults = new Object();
    const data = draw.getAll();
    const answer = document.getElementById('calculated-area');
    var coords = data.features[0].geometry.coordinates[0];
    
    var coords_parsed = [[],[]]
    var coords_output = [];
    for (let i = 0; i < coords.length; i++) {
        coords_parsed[0].push(coords[i][0])
        coords_parsed[1].push(coords[i][1])
        coords_output.push([coords[i][0],coords[i][1]])
    };
    
    Array.prototype.max = function() {
        return Math.max.apply(null, this);
    };

    Array.prototype.min = function() {
        return Math.min.apply(null, this);
    };

    if (data.features.length > 0) {
        const area = turf.area(data);
        const bbox = [coords_parsed[0].min(), coords_parsed[0].max(), coords_parsed[1].min(), coords_parsed[1].max()];
        const geometry_json = {
            "polygon":coords_output,
            "bbox":{
                "pt1_x": bbox[0],"pt1_y": bbox[2],
                "pt2_x": bbox[1],"pt2_y": bbox[3]
            },
            "area":area
        };
        
        const filename = document.getElementById('filename').value || 'data.json';
        const jsonString = JSON.stringify(geometry_json);
        const blob = new Blob([jsonString], { type: 'application/json' });
        const downloadLink = document.createElement('a');
        downloadLink.href = URL.createObjectURL(blob);
        downloadLink.download = filename;
        downloadLink.textContent = 'Download ROI';

        // Append the new download link to the download link container
        document.getElementById('download-link-container').appendChild(downloadLink);

        // Update the previousDownloadLink variable
        previousDownloadLink = downloadLink;
    } else {
        if (e.type !== 'draw.delete')
            alert('Click the map to draw a polygon.');
    };
};
