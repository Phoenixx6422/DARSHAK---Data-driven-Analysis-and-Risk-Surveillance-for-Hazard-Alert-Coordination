-- Seed Data for Local Development & Testing
-- Team integration seed for Raichur & Krishna River Basin

INSERT INTO disaster_alerts (disaster_type, severity, location, latitude, longitude, description, is_active)
VALUES
('Cyclone', 'Critical', 'Coastal Raichur Sector 4', 16.216000, 77.356600, 'High-velocity cyclonic winds exceeding 110 km/h detected. Immediate evacuation recommended.', TRUE),
('Flood', 'High', 'Krishna River Basin Zone B', 16.300000, 77.400000, 'Water levels rising above danger mark due to heavy sustained upstream rainfall.', TRUE),
('Heatwave', 'Moderate', 'Raichur Urban Zone 1', 16.200000, 77.340000, 'Temperatures reaching 41C. Hydration advisories active.', TRUE)
ON CONFLICT DO NOTHING;

-- Sample PostGIS Polygon for Raichur Risk Zone (Akash's GIS integration)
INSERT INTO risk_zones (zone_code, zone_name, disaster_type, risk_level, safety_score, geom)
VALUES (
    'RC-SEC4-CRIT',
    'Coastal Raichur Sector 4',
    'Cyclone',
    'Critical',
    24.50,
    ST_GeomFromText('POLYGON((77.350 16.210, 77.365 16.210, 77.365 16.225, 77.350 16.225, 77.350 16.210))', 4326)
)
ON CONFLICT (zone_code) DO NOTHING;
