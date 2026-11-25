
import unittest
from app import app


class HealthCheckTest(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_health_endpoint(self):
        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "healthy")
        self.assertEqual(
            response.get_json()["message"],
            "Booking API is running"
        )


if __name__ == "__main__":
    unittest.main()
