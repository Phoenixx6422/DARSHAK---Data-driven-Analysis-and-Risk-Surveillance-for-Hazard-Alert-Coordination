-- V002__postgis_and_alerts.sql
-- Integration support for Magai Akash Jagdish (GIS/PostGIS) and Himanshu Shukla (Monitoring/Notifications)

CREATE EXTENSION IF NOT EXISTS postgis;

-- Spatial risk zones for GIS integration (Layer 3 & Layer 4)
CREATE TABLE IF NOT EXISTS risk_zones (
    id SERIAL PRIMARY KEY,
    zone_code VARCHAR(50) UNIQUE NOT NULL,
    zone_name VARCHAR(150) NOT NULL,
    disaster_type VARCHAR(50) NOT NULL,
    risk_level VARCHAR(20) NOT NULL CHECK (risk_level IN ('Low', 'Moderate', 'High', 'Critical')),
    safety_score DECIMAL(5, 2) NOT NULL,
    geom GEOMETRY(Polygon, 4326),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Disaster Alerts Table
CREATE TABLE IF NOT EXISTS disaster_alerts (
    id SERIAL PRIMARY KEY,
    disaster_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('Low', 'Moderate', 'High', 'Critical')),
    location VARCHAR(150) NOT NULL,
    latitude DECIMAL(9, 6) NOT NULL,
    longitude DECIMAL(9, 6) NOT NULL,
    description TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Automated Notification Audit Log
-- Mandatory Architectural Rule: All High/Critical notifications are automated with NO authority approval.
CREATE TABLE IF NOT EXISTS automated_notification_logs (
    id SERIAL PRIMARY KEY,
    channel VARCHAR(30) NOT NULL, -- SMS, Email, WebSocket, In-App
    recipient VARCHAR(150) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    region_name VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    dispatch_status VARCHAR(30) DEFAULT 'SENT',
    authority_approval_required BOOLEAN DEFAULT FALSE, -- Always FALSE per Master Project Context
    dispatched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
