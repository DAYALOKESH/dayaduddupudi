-- Extract road segments from OSM data
INSERT INTO road_segments (osm_id, name, highway_type, oneway, geometry, max_capacity)
SELECT 
    osm_id,
    COALESCE(tags->'name', 'Unnamed Road') as name,
    tags->'highway' as highway_type,
    CASE 
        WHEN tags->'oneway' = 'yes' THEN true
        ELSE false
    END as oneway,
    way as geometry,
    CASE
        WHEN tags->'highway' = 'motorway' THEN 2000
        WHEN tags->'highway' = 'trunk' THEN 1500
        WHEN tags->'highway' = 'primary' THEN 1000
        WHEN tags->'highway' = 'secondary' THEN 800
        WHEN tags->'highway' = 'tertiary' THEN 500
        WHEN tags->'highway' = 'residential' THEN 300
        ELSE 200
    END as max_capacity
FROM planet_osm_line
WHERE tags->'highway' IN ('motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'residential', 'unclassified', 'service')
AND ST_IsValid(way);
