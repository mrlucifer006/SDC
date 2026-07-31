from locust import HttpUser, task, between
import uuid

class CTFUserBehavior(HttpUser):
    # Wait between 1 and 3 seconds between tasks for each simulated user
    wait_time = between(1, 3)

    def on_start(self):
        """Called when a simulated user starts. Registers and logs in to get an auth token."""
        self.username = f"user_{uuid.uuid4().hex[:8]}"
        self.email = f"{self.username}@kpriet.ac.in"
        self.password = "password123"
        self.token = ""
        
        # 1. Register new user
        self.client.post("/api/auth/register", json={
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "is_admin": False
        })
        
        # 2. Login to get token
        response = self.client.post(
            "/api/auth/token",
            data={"username": self.email, "password": self.password}
        )
        if response.status_code == 200:
            self.token = response.json().get("access_token")

    @property
    def auth_headers(self):
        """Helper to attach the JWT token to requests."""
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    @task(5)
    def health_check(self):
        """Public endpoint"""
        self.client.get("/api/health")

    @task(5)
    def view_public_settings(self):
        """Public endpoint"""
        self.client.get("/api/game/settings")

    @task(10)
    def view_leaderboard(self):
        """Authenticated endpoint: Leaderboard"""
        self.client.get("/api/game/leaderboard", headers=self.auth_headers)

    @task(10)
    def view_gates(self):
        """Authenticated endpoint: All Gates"""
        self.client.get("/api/game/gates", headers=self.auth_headers)

    @task(5)
    def view_specific_gate(self):
        """Authenticated endpoint: Single Gate"""
        # Gate 1 is typically unlocked by default
        self.client.get("/api/game/gates/1", headers=self.auth_headers)

    @task(5)
    def view_progress(self):
        """Authenticated endpoint: User Progress"""
        self.client.get("/api/game/progress", headers=self.auth_headers)

    @task(2)
    def submit_code(self):
        """Authenticated endpoint: Code Submission (Heavy task testing Judge0)"""
        self.client.post("/api/game/submit", json={
            "gate_id": 1,
            "source_code": "print(input())", # Simple echo program
            "language": "python",
            "stdin": "test input"
        }, headers=self.auth_headers)
        
    @task(1)
    def hit_admin_endpoints(self):
        """Hit admin endpoints (will likely 403 Forbidden, but still tests the backend routing/auth)"""
        self.client.get("/api/admin/leaderboard", headers=self.auth_headers)
        self.client.get("/api/admin/submissions", headers=self.auth_headers)
        self.client.get("/api/admin/stats", headers=self.auth_headers)
