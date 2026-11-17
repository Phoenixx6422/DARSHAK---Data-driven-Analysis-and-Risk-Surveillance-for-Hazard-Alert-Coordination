import math
EARTH_RADIUS_KM = 6371.0
NIO_COASTLINE_POLYLINE = [
    (25.0, 61.5), (24.8, 66.9), (23.2, 68.6), (22.3, 69.0), (20.9, 70.4),
    (21.6, 72.2), (20.4, 72.8), (19.0, 72.8), (17.0, 73.3), (15.4, 73.8),
    (13.0, 74.8), (11.2, 75.8), (9.9, 76.2), (8.1, 77.5), (9.2, 79.3),
    (10.3, 79.8), (13.1, 80.3), (15.9, 80.8), (17.7, 83.3), (19.3, 84.9),
    (20.3, 86.7), (21.6, 87.5), (21.8, 89.0), (22.3, 91.8), (20.1, 92.9),
    (16.5, 94.2), (16.0, 97.6), (9.8, 80.2), (8.6, 81.2), (6.9, 81.8),
    (6.0, 80.2), (7.9, 79.8), (9.8, 80.2),
]
def haversine_km(lat1, lon1, lat2, lon2):
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * EARTH_RADIUS_KM * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))

def initial_bearing_deg(lat1, lon1, lat2, lon2):
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dlambda = math.radians(lon2 - lon1)
    x = math.sin(dlambda) * math.cos(phi2)
    y = math.cos(phi1) * math.sin(phi2) - math.sin(phi1)*math.cos(phi2)*math.cos(dlambda)
    return (math.degrees(math.atan2(x, y)) + 360.0) % 360.0

def relative_approach_cosine(slat, slon, shdg, tlat, tlon):
    bt = initial_bearing_deg(slat, slon, tlat, tlon)
    diff = math.radians((bt - shdg + 180.0) % 360.0 - 180.0)
    return math.cos(diff)

def approximate_distance_to_coast_km(lat, lon):
    min_d = float('inf')
    for i in range(len(NIO_COASTLINE_POLYLINE) - 1):
        if i == 26: continue
        a, b = NIO_COASTLINE_POLYLINE[i], NIO_COASTLINE_POLYLINE[i+1]
        mean_lat = math.radians((a[0] + b[0] + lat)/3.0)
        cos_l = max(0.1, math.cos(mean_lat))
        ax, ay = a[1]*cos_l, a[0]
        bx, by = b[1]*cos_l, b[0]
        px, py = lon*cos_l, lat
        dx, dy = bx - ax, by - ay
        sq = dx*dx + dy*dy
        t = 0.0 if sq == 0 else max(0.0, min(1.0, ((px - ax)*dx + (py - ay)*dy)/sq))
        d = haversine_km(lat, lon, ay + t*dy, (ax + t*dx)/cos_l)
        if d < min_d: min_d = d
    return float(min_d)

def classify_sub_basin(lat, lon):
    return ("Bay of Bengal", 1) if lon >= 77.5 else ("Arabian Sea", 0)
