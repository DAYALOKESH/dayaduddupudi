import requests
import psycopg2
import json
from datetime import datetime
from shapely.geometry import LineString, Point
from shapely.wkt import loads
import socket

def get_route(start_lat, start_lon, end_lat, end_lon):
    """Get route from OSRM"""
    # For Docker networking, use host.docker.internal
    try:
        host_ip = socket.gethostbyname('host.docker.internal')
    except:
        # Fallback to localhost if host.docker.internal doesn't resolve
        host_ip = 'localhost'
        
    url = f"http://{host_ip}:5000/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=full&geometries=geojson"
    print(f"Requesting route from: {url}")
    response = requests.get(url)
    return response.json()

def route_to_segments(route_geometry):
    """Convert route geometry to list of segment IDs"""
    # Connect to the database
    try:
        # Try host.docker.internal first
        host_ip = socket.gethostbyname('host.docker.internal')
    except:
        # Fallback to localhost
        host_ip = 'localhost'
        
    conn = psycopg2.connect(
        dbname="road_network",
        user="postgres",
        password="mysecretpassword",
        host=host_ip
    )
    cursor = conn.cursor()
    
    # Convert route to a shapely LineString
    route_line = LineString(route_geometry['coordinates'])
    
    # Find segments that intersect with the route
    query = """
    SELECT id, osm_id, name, highway_type, geometry, ST_AsText(geometry) as geom_wkt 
    FROM road_segments
    WHERE ST_Intersects(geometry, ST_SetSRID(ST_GeomFromText(%s), 4326))
    ORDER BY ST_Distance(geometry, ST_StartPoint(ST_SetSRID(ST_GeomFromText(%s), 4326)))
    """
    
    # Convert route to WKT
    route_wkt = route_line.wkt
    cursor.execute(query, (route_wkt, route_wkt))
    
    segments = []
    for id_val, osm_id, name, highway_type, geometry, geom_wkt in cursor.fetchall():
        # Determine direction (simplified)
        segment_line = loads(geom_wkt)
        direction = 'forward'  # Default
        
        # Basic direction detection
        if len(segments) > 0:
            seg_start = Point(segment_line.coords[0])
            seg_end = Point(segment_line.coords[-1])
            if route_line.distance(seg_end) < route_line.distance(seg_start):
                direction = 'forward'
            else:
                direction = 'backward'
        
        segments.append({
            'id': id_val,
            'osm_id': osm_id,
            'name': name,
            'highway_type': highway_type,
            'direction': direction
        })
    
    conn.close()
    return segments

def book_journey(user_id, journey_name, start_time, end_time, segment_directions):
    """Book a journey"""
    # Connect to the database
    try:
        # Try host.docker.internal first
        host_ip = socket.gethostbyname('host.docker.internal')
    except:
        # Fallback to localhost
        host_ip = 'localhost'
        
    conn = psycopg2.connect(
        dbname="road_network",
        user="postgres",
        password="mysecretpassword",
        host=host_ip
    )
    cursor = conn.cursor()
    
    # Check segment capacities first
    for segment in segment_directions:
        query = """
        SELECT COUNT(*) 
        FROM segment_bookings sb
        JOIN journey_bookings jb ON sb.booking_id = jb.booking_id
        WHERE segment_id = %s 
        AND direction = %s
        AND journey_start <= %s AND journey_end >= %s
        """
        cursor.execute(query, (segment['id'], segment['direction'], end_time, start_time))
        count = cursor.fetchone()[0]
        
        # Get segment capacity
        cursor.execute("SELECT max_capacity FROM road_segments WHERE id = %s", (segment['id'],))
        result = cursor.fetchone()
        if result:
            capacity = result[0]
        else:
            capacity = 1000  # Default capacity
        
        if count >= capacity:
            conn.close()
            return False, f"Segment {segment['id']} ({segment['name']}) is at capacity"
    
    # Create journey booking
    cursor.execute(
        "INSERT INTO journey_bookings (user_id, journey_name, journey_start, journey_end) VALUES (%s, %s, %s, %s) RETURNING booking_id",
        (user_id, journey_name, start_time, end_time)
    )
    booking_id = cursor.fetchone()[0]
    
    # Create segment bookings
    for segment in segment_directions:
        cursor.execute(
            "INSERT INTO segment_bookings (booking_id, segment_id, direction) VALUES (%s, %s, %s)",
            (booking_id, segment['id'], segment['direction'])
        )
    
    conn.commit()
    conn.close()
    return True, booking_id

def plan_journey(start_lat, start_lon, end_lat, end_lon, user_id, journey_name, start_time, end_time):
    """Plan and book a journey"""
    print(f"Planning journey from ({start_lat}, {start_lon}) to ({end_lat}, {end_lon})")
    route_response = get_route(start_lat, start_lon, end_lat, end_lon)
    
    if 'routes' in route_response and len(route_response['routes']) > 0:
        route = route_response['routes'][0]
        segments = route_to_segments(route['geometry'])
        
        success, result = book_journey(user_id, journey_name, start_time, end_time, segments)
        if success:
            return {
                'status': 'success',
                'booking_id': result,
                'segments': segments,
                'route': route
            }
        else:
            return {
                'status': 'error',
                'message': result
            }
    else:
        return {
            'status': 'error',
            'message': 'No route found',
            'response': route_response
        }

# Test function
if __name__ == "__main__":
    print("Route to segments module loaded")