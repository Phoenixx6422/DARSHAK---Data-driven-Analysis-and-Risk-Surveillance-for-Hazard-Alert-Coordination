import unittest
from fastapi.testclient import TestClient
from app.main import app

class TestPDEWSEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_root_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "active")
        self.assertEqual(data["service"], "PDEWS Integrated API")

    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["database"], "connected")
        self.assertEqual(data["monitoring"], "active")

    def test_get_alerts(self):
        response = self.client.get("/api/v1/alerts")
        self.assertEqual(response.status_code, 200)
        alerts = response.json()
        self.assertIsInstance(alerts, list)
        self.assertGreaterEqual(len(alerts), 2)

    def test_get_alerts_filtered(self):
        response = self.client.get("/api/v1/alerts?severity=Critical")
        self.assertEqual(response.status_code, 200)
        alerts = response.json()
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["severity"], "Critical")

    def test_risk_evaluate_valid(self):
        payload = {
            "region_name": "Krishna River Basin",
            "latitude": 16.3000,
            "longitude": 77.4000
        }
        response = self.client.post("/api/v1/risk/evaluate", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["region_name"], "Krishna River Basin")
        self.assertTrue(data["automated_notification_triggered"])

    def test_risk_evaluate_missing_fields(self):
        response = self.client.post("/api/v1/risk/evaluate", json={"latitude": 16.3})
        self.assertEqual(response.status_code, 422)

    def test_profile(self):
        response = self.client.get("/api/v1/profile")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Himanshu Shukla")
        self.assertIn("@", data["email"])

    def test_websocket(self):
        with self.client.websocket_connect("/ws/alerts") as ws:
            ws.send_text("Hello Alert Server")
            reply = ws.receive_text()
            self.assertIn("Broadcast acknowledgment: Hello Alert Server", reply)

if __name__ == "__main__":
    unittest.main()
