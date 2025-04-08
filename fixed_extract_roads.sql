-- Extract road segments from OSM data (adjusted for direct columns)
INSERT INTO road_segments (osm_id, name, highway_type, oneway, geometry, max_capacity)
SELECT 
    osm_id,
    COALESCE(name, 'Unnamed Road') as name,
    highway as highway_type,
    CASE 
        WHEN oneway = 'yes' THEN true
        ELSE false
    END as oneway,
    ST_Transform(way, 4326) as geometry,  -- Transform to WGS84 (EPSG:4326)
    CASE
        WHEN highway = 'motorway' THEN 2000
        WHEN highway = 'trunk' THEN 1500
        WHEN highway = 'primary' THEN 1000
        WHEN highway = 'secondary' THEN 800
        WHEN highway = 'tertiary' THEN 500
        WHEN highway = 'residential' THEN 300
        ELSE 200
    END as max_capacity
FROM planet_osm_line
WHERE highway IN ('motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'residential', 'unclassified', 'service')
AND ST_IsValid(way);
