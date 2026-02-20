import os
import time
import httpx
from typing import Generator


class Auth(httpx.Auth):
    def __init__(self):
        self.token_endpoint = os.getenv("TOKEN_ENDPOINT", None)
        self.client_id = os.getenv("CLIENT_ID", None)
        self.username = os.getenv("AGENT_USERNAME", None)
        self.password = os.getenv("AGENT_PASSWORD", None)

        self.access_token = None
        self.token_expires_at = 0

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        if not all([self.client_id, self.username, self.password, self.token_endpoint]):
            raise ValueError(f"Missing environment variables: CLIENT_ID, AGENT_USERNAME, AGENT_PASSWORD, or TOKEN_ENDPOINT. Values: {self.client_id, self.username, self.password, self.token_endpoint}")

        if not self.access_token or time.time() >= self.token_expires_at:
            self.access_token = self.get_token()

        request.headers['Authorization'] = self.access_token
        request.headers['user-agent'] = "Agent-auth"

        yield request

    def get_token(self) -> str:
        payload = {
            "client_id": self.client_id,
            "username": self.username,
            "password": self.password,
            "grant_type": "password",
        }
        with httpx.Client() as client:
            response = client.post(self.token_endpoint, data=payload)
            response.raise_for_status()

            data = response.json()
            self.token_expires_at = time.time() + float(data.get("expires_in", 3600)) - 10
            return f"Bearer {data['access_token']}"

