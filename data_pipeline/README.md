# Data Engineering & GIS Sub-project
**Owner:** Magai Akash Jagdish (Member 4)
**Integration Partners:** Himanshu Shukla (Database & PostGIS), Sanskar Dave (Frontend Map), Vaibhav Rawat (Backend)

---

### Purpose
Processes environmental, meteorological (CWC, IMD, Satellite) data, converts GIS shapefiles into GeoJSON, and loads spatial data into the central PostgreSQL / PostGIS database.

### PostGIS Database Connection
When running via Docker Compose, connect to Himanshu's PostGIS instance:
* **Host:** `localhost` (outside Docker) or `db` (inside Docker network `pdews_net`)
* **Port:** `5432`
* **Database:** `pdews_db`
* **User:** `pdews_admin`
* **Password:** `securepassword123`
* **Table:** `risk_zones` (supports `ST_GeomFromGeoJSON` and spatial bounding box queries)

### GeoJSON Contract
See [`sample_zones.geojson`](./sample_zones.geojson) for the exact schema expected by the Frontend Interactive Map (Sanskar Dave):
- Properties: `zone_code`, `zone_name`, `disaster_type`, `risk_level` (Low, Moderate, High, Critical), `color` (Green, Yellow, Orange, Red), `safety_score` (0-100).
