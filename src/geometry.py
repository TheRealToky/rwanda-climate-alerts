# Imports and Pre-requisites
import ee

# Fetch the district outline of Rwanda
districts = ee.FeatureCollection("FAO/GAUL/2015/level2") \
            .filter(ee.Filter.eq("ADM0_NAME", "Rwanda"))

# Polygon englobing Rwanda
rwanda = ee.Geometry.Polygon([
    [
        [28.70, -2.85],
        [31.00, -2.85],
        [31.00, -1.00],
        [28.70, -1.00]
    ]
])

# Add a 10km buffer to Rwanda's polygon
rwanda_buffered = rwanda.buffer(10000)  # 10,000 meters