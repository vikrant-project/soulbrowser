"""Soul Browser DevTools Module."""

from __future__ import annotations
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger("soulbrowser.devtools")


@dataclass
class NetworkRequest:
    """Captured network request."""
    url: str
    method: str
    headers: Dict[str, str]
    status: int = 0
    response_headers: Dict[str, str] = None
    timing: float = 0.0


@dataclass
class PerformanceEntry:
    """Performance timing entry."""
    name: str
    start_time: float
    duration: float
    entry_type: str


class NetworkInspector:
    """Network request inspector."""
    
    def __init__(self):
        self._requests: List[NetworkRequest] = []
        self._enabled = False
    
    def enable(self) -> None:
        self._enabled = True
    
    def disable(self) -> None:
        self._enabled = False
    
    def add_request(self, request: NetworkRequest) -> None:
        if self._enabled:
            self._requests.append(request)
    
    def get_requests(self) -> List[NetworkRequest]:
        return self._requests.copy()
    
    def clear(self) -> None:
        self._requests.clear()
    
    def export_har(self) -> Dict[str, Any]:
        """Export requests as HAR format."""
        entries = []
        for req in self._requests:
            entries.append({
                "request": {
                    "method": req.method,
                    "url": req.url,
                    "headers": [{"name": k, "value": v} for k, v in req.headers.items()],
                },
                "response": {
                    "status": req.status,
                    "headers": [{"name": k, "value": v} for k, v in (req.response_headers or {}).items()],
                },
                "time": req.timing,
            })
        
        return {
            "log": {
                "version": "1.2",
                "creator": {"name": "Soul Browser", "version": "1.0.0"},
                "entries": entries,
            }
        }


class ConsoleCapture:
    """Browser console capture."""
    
    def __init__(self):
        self._messages: List[Dict[str, Any]] = []
        self._enabled = False
    
    def enable(self) -> None:
        self._enabled = True
    
    def disable(self) -> None:
        self._enabled = False
    
    def add_message(self, level: str, text: str, source: str = "") -> None:
        if self._enabled:
            self._messages.append({
                "level": level,
                "text": text,
                "source": source,
            })
    
    def get_messages(self, level: Optional[str] = None) -> List[Dict[str, Any]]:
        if level:
            return [m for m in self._messages if m["level"] == level]
        return self._messages.copy()
    
    def clear(self) -> None:
        self._messages.clear()


class DevTools:
    """DevTools integration for Soul Browser."""
    
    def __init__(self):
        self.network = NetworkInspector()
        self.console = ConsoleCapture()
    
    def attach_to_page(self, page: Any) -> None:
        """Attach DevTools to a page."""
        self.network.enable()
        self.console.enable()
        
        # Set up request interception
        page.on("request", lambda req: self.network.add_request(NetworkRequest(
            url=req.url,
            method=req.method,
            headers=dict(req.headers),
        )))
        
        page.on("console", lambda msg: self.console.add_message(
            level=msg.type,
            text=msg.text,
        ))
    
    def get_performance_metrics(self, page: Any) -> List[PerformanceEntry]:
        """Get performance metrics from page."""
        try:
            metrics = page.evaluate('''() => {
                return performance.getEntriesByType("navigation").map(e => ({
                    name: e.name,
                    startTime: e.startTime,
                    duration: e.duration,
                    entryType: e.entryType
                }));
            }''')
            return [PerformanceEntry(**m) for m in metrics]
        except Exception:
            return []
