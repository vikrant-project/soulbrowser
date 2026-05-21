"""Session persistence and restoration."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import json
import asyncio
from pathlib import Path
from datetime import datetime
import hashlib


@dataclass
class Tab:
    """Tab state."""
    id: str
    url: str
    title: str
    favicon: Optional[str] = None
    scroll_position: int = 0
    form_data: Dict[str, Any] = field(default_factory=dict)
    history: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_accessed: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    

@dataclass
class Window:
    """Window state."""
    id: str
    tabs: List[Tab] = field(default_factory=list)
    active_tab_id: Optional[str] = None
    position: Dict[str, int] = field(default_factory=lambda: {"x": 0, "y": 0})
    size: Dict[str, int] = field(default_factory=lambda: {"width": 1280, "height": 800})
    is_maximized: bool = False
    is_minimized: bool = False


@dataclass
class Session:
    """Browser session."""
    id: str
    name: str
    windows: List[Window] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_saved: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class SessionManager:
    """Session management for Soul Browser."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path.home() / ".soulbrowser" / "sessions"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._current_session: Optional[Session] = None
        self._auto_save_interval: int = 30
        self._auto_save_task: Optional[asyncio.Task] = None
        
    def _generate_id(self) -> str:
        """Generate unique ID."""
        return hashlib.md5(
            f"{datetime.utcnow().isoformat()}{id(self)}".encode()
        ).hexdigest()[:12]
        
    def create_session(self, name: str = "Default") -> Session:
        """Create new session."""
        session = Session(
            id=self._generate_id(),
            name=name
        )
        self._current_session = session
        return session
        
    def add_window(self) -> Window:
        """Add window to current session."""
        if not self._current_session:
            self.create_session()
            
        window = Window(id=self._generate_id())
        self._current_session.windows.append(window)
        return window
        
    def add_tab(self, window_id: str, url: str, title: str = "") -> Tab:
        """Add tab to window."""
        if not self._current_session:
            return None
            
        for window in self._current_session.windows:
            if window.id == window_id:
                tab = Tab(
                    id=self._generate_id(),
                    url=url,
                    title=title or url
                )
                window.tabs.append(tab)
                return tab
        return None
        
    def save_session(self, session: Optional[Session] = None) -> bool:
        """Save session to disk."""
        session = session or self._current_session
        if not session:
            return False
            
        session.last_saved = datetime.utcnow().isoformat()
        filepath = self.storage_path / f"{session.id}.json"
        
        try:
            data = {
                "id": session.id,
                "name": session.name,
                "created_at": session.created_at,
                "last_saved": session.last_saved,
                "windows": [
                    {
                        "id": w.id,
                        "active_tab_id": w.active_tab_id,
                        "position": w.position,
                        "size": w.size,
                        "is_maximized": w.is_maximized,
                        "tabs": [
                            {
                                "id": t.id,
                                "url": t.url,
                                "title": t.title,
                                "favicon": t.favicon,
                                "scroll_position": t.scroll_position,
                                "history": t.history,
                                "created_at": t.created_at,
                                "last_accessed": t.last_accessed
                            }
                            for t in w.tabs
                        ]
                    }
                    for w in session.windows
                ]
            }
            filepath.write_text(json.dumps(data, indent=2))
            return True
        except Exception:
            return False
            
    def load_session(self, session_id: str) -> Optional[Session]:
        """Load session from disk."""
        filepath = self.storage_path / f"{session_id}.json"
        
        if not filepath.exists():
            return None
            
        try:
            data = json.loads(filepath.read_text())
            session = Session(
                id=data["id"],
                name=data["name"],
                created_at=data["created_at"],
                last_saved=data["last_saved"]
            )
            
            for w_data in data["windows"]:
                window = Window(
                    id=w_data["id"],
                    active_tab_id=w_data.get("active_tab_id"),
                    position=w_data.get("position", {}),
                    size=w_data.get("size", {}),
                    is_maximized=w_data.get("is_maximized", False)
                )
                
                for t_data in w_data["tabs"]:
                    tab = Tab(
                        id=t_data["id"],
                        url=t_data["url"],
                        title=t_data["title"],
                        favicon=t_data.get("favicon"),
                        scroll_position=t_data.get("scroll_position", 0),
                        history=t_data.get("history", []),
                        created_at=t_data.get("created_at", ""),
                        last_accessed=t_data.get("last_accessed", "")
                    )
                    window.tabs.append(tab)
                    
                session.windows.append(window)
                
            self._current_session = session
            return session
        except Exception:
            return None
            
    def list_sessions(self) -> List[Dict[str, str]]:
        """List all saved sessions."""
        sessions = []
        for filepath in self.storage_path.glob("*.json"):
            try:
                data = json.loads(filepath.read_text())
                sessions.append({
                    "id": data["id"],
                    "name": data["name"],
                    "last_saved": data["last_saved"]
                })
            except Exception:
                pass
        return sessions
        
    def delete_session(self, session_id: str) -> bool:
        """Delete saved session."""
        filepath = self.storage_path / f"{session_id}.json"
        if filepath.exists():
            filepath.unlink()
            return True
        return False
        
    async def start_auto_save(self, interval: int = 30) -> None:
        """Start auto-save task."""
        self._auto_save_interval = interval
        
        async def auto_save_loop():
            while True:
                await asyncio.sleep(self._auto_save_interval)
                self.save_session()
                
        self._auto_save_task = asyncio.create_task(auto_save_loop())
        
    def stop_auto_save(self) -> None:
        """Stop auto-save task."""
        if self._auto_save_task:
            self._auto_save_task.cancel()
            self._auto_save_task = None
