import os
import time
from typing import List, Optional
from urllib.parse import urlparse

from pydantic import BaseModel
import redis


class Pipeline:
    class Valves(BaseModel):
        pipelines: List[str] = []
        priority: int = 0
        requests_per_minute: Optional[int] = None

    def __init__(self):
        redis_url = os.getenv("RATE_LIMIT_REDIS_URL")
        requests_per_minute = int(
            os.getenv("RATE_LIMIT_DEFAULT_REQUESTS_PER_MINUTE", 10)
        )

        if redis_url is None:
            self.type = None
            self.name = "Rate Limit Filter (disabled)"
            return

        self.type = "filter"
        self.name = "Rate Limit Filter"

        self.valves = self.Valves(
            pipelines=["*"],
            requests_per_minute=requests_per_minute,
        )

        parsed_url = urlparse(redis_url)
        if not parsed_url.hostname:
            raise ValueError("Invalid RATE_LIMIT_REDIS_URL: missing hostname")
        try:
            self.redis_client = redis.Redis(
                host=parsed_url.hostname,
                port=parsed_url.port if parsed_url.port else 6379,
                db=int(parsed_url.path[1:]) if parsed_url.path else 0,
                password=parsed_url.password,
                decode_responses=True,
            )
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Redis: {str(e)}")

    def get_redis_key(self, user_id: str, model_id: str):
        """Generate Redis keys for rate limits."""
        now = int(time.time())
        return f"user:{user_id}:{model_id}:rate:minute:{now // 60}"

    def is_rate_limited(self, user_id: str, model_id: str) -> bool:
        """Check if the user exceeds rate limits."""
        minute_key = self.get_redis_key(user_id, model_id)

        if (
            self.valves.requests_per_minute
            and int(self.redis_client.get(minute_key) or 0)
            >= self.valves.requests_per_minute
        ):
            return True

        return False

    def log_request(self, user_id: str, model_id: str):
        minute_key = self.get_redis_key(user_id, model_id)

        self.redis_client.incr(minute_key)
        self.redis_client.expire(minute_key, 60, nx=True)

    async def inlet(self, body: dict, user: Optional[dict] = None) -> dict:
        user_id = user.get("id", "default_user")
        model_id = body["model"]

        if self.is_rate_limited(user_id, model_id):
            raise Exception("Rate limit exceeded. Please try again later.")

        self.log_request(user_id, model_id)

        return body
