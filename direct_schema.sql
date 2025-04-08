-- Road segments for routing
CREATE TABLE road_segments (
    id SERIAL PRIMARY KEY,
    osm_id BIGINT,
    name TEXT,
    highway_type TEXT,
    oneway BOOLEAN DEFAULT FALSE,
    geometry GEOMETRY(LINESTRING, 4326),
    max_capacity INT DEFAULT 1000
);

-- Journey bookings table
CREATE TABLE journey_bookings (
    booking_id SERIAL PRIMARY KEY,
    user_id VARCHAR(100),
    journey_name VARCHAR(255),
    booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    journey_start TIMESTAMP,
    journey_end TIMESTAMP,
    status VARCHAR(20) DEFAULT 'confirmed'
);

-- Segment bookings table
CREATE TABLE segment_bookings (
    booking_id INT REFERENCES journey_bookings(booking_id) ON DELETE CASCADE,
    segment_id INT REFERENCES road_segments(id),
    direction VARCHAR(10) CHECK (direction IN ('forward', 'backward')),
    PRIMARY KEY (booking_id, segment_id, direction)
);

CREATE INDEX road_segments_geometry_idx ON road_segments USING GIST(geometry);
CREATE INDEX segment_bookings_segment_id_idx ON segment_bookings(segment_id);
