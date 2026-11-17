-- V001__core_schema.sql
CREATE TABLE IF NOT EXISTS risk_assessments (
    id SERIAL PRIMARY KEY,
    region_name VARCHAR(150) NOT NULL,
    latitude DECIMAL(9, 6) NOT NULL,
    longitude DECIMAL(9, 6) NOT NULL,
    safety_score DECIMAL(5, 2) NOT NULL,
    risk_classification VARCHAR(50) NOT NULL,
    advisory TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_profiles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100) UNIQUE NOT NULL,
    blood_group VARCHAR(5),
    emergency_contact VARCHAR(20),
    saved_location VARCHAR(150)
);

INSERT INTO user_profiles (name, phone, email, blood_group, emergency_contact, saved_location)
VALUES ('Himanshu Shukla', '+91-9876543210', 'cs25b1017@iiitraichur.ac.in', 'B+', '+91-9123456789', 'Hostel Krishna, IIIT Raichur')
ON CONFLICT (email) DO NOTHING;
