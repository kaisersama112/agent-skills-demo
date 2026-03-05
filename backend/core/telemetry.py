import json
from datetime import datetime
from typing import Any, Dict


def log_event(event: str, **kwargs: Any) -> None:
    payload: Dict[str, Any] = {
        "ts": datetime.utcnow().isoformat(),
        "event": event,
        **kwargs,
    }
    print(json.dumps(payload, ensure_ascii=False, default=str))
