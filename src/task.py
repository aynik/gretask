from datetime import datetime
from typing import Optional, Dict, Any


class Task:
    def __init__(
        self,
        name: str,
        payload: Dict[str, Any],
        reschedule: Optional[int] = None,
        acquire_at: Optional[datetime] = None,
        id_: int = 0,
    ):
        self.id = id_
        self.name = name
        self.payload = payload
        self.reschedule = reschedule
        self.acquire_at = acquire_at or datetime.utcnow()
