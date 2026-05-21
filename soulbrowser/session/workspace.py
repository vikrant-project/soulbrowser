"""Workspace management for organizing tabs and sessions."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import json
from pathlib import Path
from datetime import datetime


@dataclass
class Workspace:
    """Workspace configuration."""
    id: str
    name: str
    icon: str = "briefcase"
    color: str = "#4A90D9"
    urls: List[str] = field(default_factory=list)
    is_active: bool = False
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class WorkspaceManager:
    """Workspace management for Soul Browser."""
    
    DEFAULT_WORKSPACES = [
        {"name": "Personal", "icon": "home", "color": "#4CAF50"},
        {"name": "Work", "icon": "briefcase", "color": "#2196F3"},
        {"name": "Research", "icon": "book", "color": "#9C27B0"},
        {"name": "Shopping", "icon": "shopping-cart", "color": "#FF9800"},
    ]
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path.home() / ".soulbrowser" / "workspaces"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._workspaces: Dict[str, Workspace] = {}
        self._active_workspace_id: Optional[str] = None
        self._load_workspaces()
        
    def _generate_id(self) -> str:
        """Generate unique ID."""
        import hashlib
        return hashlib.md5(
            f"{datetime.utcnow().isoformat()}{len(self._workspaces)}".encode()
        ).hexdigest()[:8]
        
    def _load_workspaces(self) -> None:
        """Load workspaces from disk."""
        config_file = self.storage_path / "workspaces.json"
        
        if config_file.exists():
            try:
                data = json.loads(config_file.read_text())
                for w_data in data.get("workspaces", []):
                    workspace = Workspace(
                        id=w_data["id"],
                        name=w_data["name"],
                        icon=w_data.get("icon", "briefcase"),
                        color=w_data.get("color", "#4A90D9"),
                        urls=w_data.get("urls", []),
                        is_active=w_data.get("is_active", False),
                        created_at=w_data.get("created_at", "")
                    )
                    self._workspaces[workspace.id] = workspace
                    if workspace.is_active:
                        self._active_workspace_id = workspace.id
            except Exception:
                pass
                
        # Create defaults if none exist
        if not self._workspaces:
            for w_data in self.DEFAULT_WORKSPACES:
                self.create_workspace(
                    name=w_data["name"],
                    icon=w_data["icon"],
                    color=w_data["color"]
                )
                
    def _save_workspaces(self) -> None:
        """Save workspaces to disk."""
        config_file = self.storage_path / "workspaces.json"
        
        data = {
            "workspaces": [
                {
                    "id": w.id,
                    "name": w.name,
                    "icon": w.icon,
                    "color": w.color,
                    "urls": w.urls,
                    "is_active": w.is_active,
                    "created_at": w.created_at
                }
                for w in self._workspaces.values()
            ]
        }
        config_file.write_text(json.dumps(data, indent=2))
        
    def create_workspace(
        self,
        name: str,
        icon: str = "briefcase",
        color: str = "#4A90D9"
    ) -> Workspace:
        """Create new workspace."""
        workspace = Workspace(
            id=self._generate_id(),
            name=name,
            icon=icon,
            color=color
        )
        self._workspaces[workspace.id] = workspace
        self._save_workspaces()
        return workspace
        
    def delete_workspace(self, workspace_id: str) -> bool:
        """Delete workspace."""
        if workspace_id in self._workspaces:
            del self._workspaces[workspace_id]
            if self._active_workspace_id == workspace_id:
                self._active_workspace_id = None
            self._save_workspaces()
            return True
        return False
        
    def switch_workspace(self, workspace_id: str) -> bool:
        """Switch to workspace."""
        if workspace_id in self._workspaces:
            # Deactivate current
            if self._active_workspace_id:
                self._workspaces[self._active_workspace_id].is_active = False
                
            # Activate new
            self._workspaces[workspace_id].is_active = True
            self._active_workspace_id = workspace_id
            self._save_workspaces()
            return True
        return False
        
    def add_url_to_workspace(self, workspace_id: str, url: str) -> bool:
        """Add URL to workspace."""
        if workspace_id in self._workspaces:
            if url not in self._workspaces[workspace_id].urls:
                self._workspaces[workspace_id].urls.append(url)
                self._save_workspaces()
            return True
        return False
        
    def remove_url_from_workspace(self, workspace_id: str, url: str) -> bool:
        """Remove URL from workspace."""
        if workspace_id in self._workspaces:
            if url in self._workspaces[workspace_id].urls:
                self._workspaces[workspace_id].urls.remove(url)
                self._save_workspaces()
            return True
        return False
        
    def get_active_workspace(self) -> Optional[Workspace]:
        """Get active workspace."""
        if self._active_workspace_id:
            return self._workspaces.get(self._active_workspace_id)
        return None
        
    def get_all_workspaces(self) -> List[Workspace]:
        """Get all workspaces."""
        return list(self._workspaces.values())
        
    def rename_workspace(self, workspace_id: str, name: str) -> bool:
        """Rename workspace."""
        if workspace_id in self._workspaces:
            self._workspaces[workspace_id].name = name
            self._save_workspaces()
            return True
        return False
        
    def update_workspace_color(self, workspace_id: str, color: str) -> bool:
        """Update workspace color."""
        if workspace_id in self._workspaces:
            self._workspaces[workspace_id].color = color
            self._save_workspaces()
            return True
        return False
