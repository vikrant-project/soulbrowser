"""Soul Browser Tab Management."""

from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from enum import Enum
import uuid

logger = logging.getLogger("soulbrowser.ui.tabs")


class TabState(Enum):
    """Tab state options."""
    ACTIVE = "active"
    LOADING = "loading"
    HIBERNATED = "hibernated"
    CRASHED = "crashed"


@dataclass
class Tab:
    """Represents a browser tab."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    url: str = "about:blank"
    title: str = "New Tab"
    favicon: Optional[str] = None
    state: TabState = TabState.ACTIVE
    pinned: bool = False
    muted: bool = False
    group_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    memory_usage: int = 0
    page: Any = None


@dataclass
class TabGroup:
    """Tab group for organization."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "New Group"
    color: str = "#6366f1"
    collapsed: bool = False
    tabs: List[str] = field(default_factory=list)


class TabManager:
    """Advanced tab management with groups, hibernation, and vertical tabs."""
    
    MAX_TABS = 500
    HIBERNATE_THRESHOLD_MB = 100
    HIBERNATE_IDLE_MINUTES = 30
    
    def __init__(self):
        self._tabs: Dict[str, Tab] = {}
        self._groups: Dict[str, TabGroup] = {}
        self._active_tab_id: Optional[str] = None
        self._tab_order: List[str] = []
        self._history: List[str] = []
        self._on_tab_change: List[Callable] = []
        self._vertical_mode: bool = False
    
    @property
    def active_tab(self) -> Optional[Tab]:
        if self._active_tab_id:
            return self._tabs.get(self._active_tab_id)
        return None
    
    @property
    def tabs(self) -> List[Tab]:
        return [self._tabs[tid] for tid in self._tab_order if tid in self._tabs]
    
    @property
    def groups(self) -> List[TabGroup]:
        return list(self._groups.values())
    
    def create_tab(self, url: str = "about:blank", group_id: Optional[str] = None) -> Tab:
        """Create a new tab."""
        if len(self._tabs) >= self.MAX_TABS:
            self._hibernate_oldest_tabs(10)
        
        tab = Tab(url=url, group_id=group_id)
        self._tabs[tab.id] = tab
        self._tab_order.append(tab.id)
        
        if group_id and group_id in self._groups:
            self._groups[group_id].tabs.append(tab.id)
        
        logger.info(f"Created tab {tab.id}: {url}")
        return tab
    
    def close_tab(self, tab_id: str) -> bool:
        """Close a tab."""
        if tab_id not in self._tabs:
            return False
        
        tab = self._tabs[tab_id]
        if tab.group_id and tab.group_id in self._groups:
            self._groups[tab.group_id].tabs.remove(tab_id)
        
        del self._tabs[tab_id]
        self._tab_order.remove(tab_id)
        
        if self._active_tab_id == tab_id:
            self._active_tab_id = self._tab_order[-1] if self._tab_order else None
        
        logger.info(f"Closed tab {tab_id}")
        return True
    
    def activate_tab(self, tab_id: str) -> bool:
        """Activate a tab."""
        if tab_id not in self._tabs:
            return False
        
        old_active = self._active_tab_id
        self._active_tab_id = tab_id
        self._tabs[tab_id].last_accessed = datetime.now()
        
        if self._tabs[tab_id].state == TabState.HIBERNATED:
            self._wake_tab(tab_id)
        
        if old_active:
            self._history.append(old_active)
        
        self._notify_change("activate", tab_id)
        return True
    
    def pin_tab(self, tab_id: str) -> bool:
        """Pin/unpin a tab."""
        if tab_id not in self._tabs:
            return False
        self._tabs[tab_id].pinned = not self._tabs[tab_id].pinned
        return True
    
    def mute_tab(self, tab_id: str) -> bool:
        """Mute/unmute a tab."""
        if tab_id not in self._tabs:
            return False
        self._tabs[tab_id].muted = not self._tabs[tab_id].muted
        return True
    
    def hibernate_tab(self, tab_id: str) -> bool:
        """Hibernate a tab to save memory."""
        if tab_id not in self._tabs:
            return False
        
        tab = self._tabs[tab_id]
        if tab.pinned or tab.state == TabState.HIBERNATED:
            return False
        
        tab.state = TabState.HIBERNATED
        tab.memory_usage = 0
        logger.info(f"Hibernated tab {tab_id}")
        return True
    
    def _wake_tab(self, tab_id: str) -> None:
        """Wake a hibernated tab."""
        if tab_id in self._tabs:
            self._tabs[tab_id].state = TabState.LOADING
    
    def _hibernate_oldest_tabs(self, count: int) -> None:
        """Hibernate oldest unused tabs."""
        candidates = [
            t for t in self.tabs 
            if not t.pinned and t.state == TabState.ACTIVE
        ]
        candidates.sort(key=lambda t: t.last_accessed)
        
        for tab in candidates[:count]:
            self.hibernate_tab(tab.id)
    
    def create_group(self, name: str, color: str = "#6366f1") -> TabGroup:
        """Create a new tab group."""
        group = TabGroup(name=name, color=color)
        self._groups[group.id] = group
        return group
    
    def move_to_group(self, tab_id: str, group_id: str) -> bool:
        """Move a tab to a group."""
        if tab_id not in self._tabs or group_id not in self._groups:
            return False
        
        tab = self._tabs[tab_id]
        if tab.group_id and tab.group_id in self._groups:
            self._groups[tab.group_id].tabs.remove(tab_id)
        
        tab.group_id = group_id
        self._groups[group_id].tabs.append(tab_id)
        return True
    
    def reorder_tabs(self, tab_ids: List[str]) -> None:
        """Reorder tabs."""
        valid_ids = [tid for tid in tab_ids if tid in self._tabs]
        self._tab_order = valid_ids
    
    def duplicate_tab(self, tab_id: str) -> Optional[Tab]:
        """Duplicate a tab."""
        if tab_id not in self._tabs:
            return None
        
        original = self._tabs[tab_id]
        return self.create_tab(original.url, original.group_id)
    
    def toggle_vertical_mode(self) -> bool:
        """Toggle vertical tabs mode."""
        self._vertical_mode = not self._vertical_mode
        return self._vertical_mode
    
    def on_change(self, callback: Callable) -> None:
        """Register a change callback."""
        self._on_tab_change.append(callback)
    
    def _notify_change(self, action: str, tab_id: str) -> None:
        for callback in self._on_tab_change:
            try:
                callback(action, tab_id)
            except Exception as e:
                logger.warning(f"Tab change callback failed: {e}")
    
    def get_stats(self) -> Dict:
        """Get tab statistics."""
        return {
            "total": len(self._tabs),
            "active": sum(1 for t in self._tabs.values() if t.state == TabState.ACTIVE),
            "hibernated": sum(1 for t in self._tabs.values() if t.state == TabState.HIBERNATED),
            "pinned": sum(1 for t in self._tabs.values() if t.pinned),
            "groups": len(self._groups),
            "memory_total_mb": sum(t.memory_usage for t in self._tabs.values()) / (1024 * 1024)
        }
