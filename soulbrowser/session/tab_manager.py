"""Advanced tab management."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import asyncio


class TabState(Enum):
    ACTIVE = "active"
    HIBERNATED = "hibernated"
    LOADING = "loading"
    CRASHED = "crashed"


@dataclass
class TabGroup:
    """Tab group configuration."""
    id: str
    name: str
    color: str
    collapsed: bool = False
    tab_ids: List[str] = field(default_factory=list)


class TabManager:
    """Advanced tab management for Soul Browser."""
    
    def __init__(self, max_active_tabs: int = 10):
        self.max_active_tabs = max_active_tabs
        self._tabs: Dict[str, Dict[str, Any]] = {}
        self._groups: Dict[str, TabGroup] = {}
        self._pinned_tabs: List[str] = []
        self._muted_tabs: List[str] = []
        self._tab_stack: List[str] = []
        self._listeners: List[Callable] = []
        
    def create_tab(
        self,
        tab_id: str,
        url: str,
        title: str = "",
        group_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create new tab."""
        tab = {
            "id": tab_id,
            "url": url,
            "title": title or url,
            "state": TabState.LOADING,
            "group_id": group_id,
            "memory_usage": 0,
            "cpu_usage": 0.0
        }
        self._tabs[tab_id] = tab
        self._tab_stack.append(tab_id)
        
        if group_id and group_id in self._groups:
            self._groups[group_id].tab_ids.append(tab_id)
            
        self._notify_listeners("tab_created", tab)
        self._check_hibernation()
        return tab
        
    def close_tab(self, tab_id: str) -> bool:
        """Close tab."""
        if tab_id not in self._tabs:
            return False
            
        tab = self._tabs.pop(tab_id)
        
        # Remove from group
        if tab.get("group_id") and tab["group_id"] in self._groups:
            self._groups[tab["group_id"]].tab_ids.remove(tab_id)
            
        # Remove from other lists
        if tab_id in self._pinned_tabs:
            self._pinned_tabs.remove(tab_id)
        if tab_id in self._muted_tabs:
            self._muted_tabs.remove(tab_id)
        if tab_id in self._tab_stack:
            self._tab_stack.remove(tab_id)
            
        self._notify_listeners("tab_closed", tab)
        return True
        
    def pin_tab(self, tab_id: str) -> bool:
        """Pin tab."""
        if tab_id in self._tabs and tab_id not in self._pinned_tabs:
            self._pinned_tabs.insert(0, tab_id)
            self._notify_listeners("tab_pinned", self._tabs[tab_id])
            return True
        return False
        
    def unpin_tab(self, tab_id: str) -> bool:
        """Unpin tab."""
        if tab_id in self._pinned_tabs:
            self._pinned_tabs.remove(tab_id)
            self._notify_listeners("tab_unpinned", self._tabs[tab_id])
            return True
        return False
        
    def mute_tab(self, tab_id: str) -> bool:
        """Mute tab audio."""
        if tab_id in self._tabs and tab_id not in self._muted_tabs:
            self._muted_tabs.append(tab_id)
            self._notify_listeners("tab_muted", self._tabs[tab_id])
            return True
        return False
        
    def unmute_tab(self, tab_id: str) -> bool:
        """Unmute tab audio."""
        if tab_id in self._muted_tabs:
            self._muted_tabs.remove(tab_id)
            self._notify_listeners("tab_unmuted", self._tabs[tab_id])
            return True
        return False
        
    def hibernate_tab(self, tab_id: str) -> bool:
        """Hibernate tab to save resources."""
        if tab_id in self._tabs:
            self._tabs[tab_id]["state"] = TabState.HIBERNATED
            self._tabs[tab_id]["memory_usage"] = 0
            self._tabs[tab_id]["cpu_usage"] = 0
            self._notify_listeners("tab_hibernated", self._tabs[tab_id])
            return True
        return False
        
    def wake_tab(self, tab_id: str) -> bool:
        """Wake hibernated tab."""
        if tab_id in self._tabs and self._tabs[tab_id]["state"] == TabState.HIBERNATED:
            self._tabs[tab_id]["state"] = TabState.LOADING
            self._notify_listeners("tab_waking", self._tabs[tab_id])
            return True
        return False
        
    def create_group(self, name: str, color: str = "#4A90D9") -> TabGroup:
        """Create tab group."""
        import hashlib
        group_id = hashlib.md5(f"{name}{id(self)}".encode()).hexdigest()[:8]
        group = TabGroup(id=group_id, name=name, color=color)
        self._groups[group_id] = group
        return group
        
    def add_to_group(self, tab_id: str, group_id: str) -> bool:
        """Add tab to group."""
        if tab_id in self._tabs and group_id in self._groups:
            # Remove from old group
            old_group_id = self._tabs[tab_id].get("group_id")
            if old_group_id and old_group_id in self._groups:
                self._groups[old_group_id].tab_ids.remove(tab_id)
                
            self._tabs[tab_id]["group_id"] = group_id
            self._groups[group_id].tab_ids.append(tab_id)
            return True
        return False
        
    def remove_from_group(self, tab_id: str) -> bool:
        """Remove tab from group."""
        if tab_id in self._tabs:
            group_id = self._tabs[tab_id].get("group_id")
            if group_id and group_id in self._groups:
                self._groups[group_id].tab_ids.remove(tab_id)
                self._tabs[tab_id]["group_id"] = None
                return True
        return False
        
    def collapse_group(self, group_id: str) -> bool:
        """Collapse tab group."""
        if group_id in self._groups:
            self._groups[group_id].collapsed = True
            return True
        return False
        
    def expand_group(self, group_id: str) -> bool:
        """Expand tab group."""
        if group_id in self._groups:
            self._groups[group_id].collapsed = False
            return True
        return False
        
    def get_tab_order(self) -> List[str]:
        """Get ordered list of tab IDs."""
        # Pinned tabs first, then grouped, then ungrouped
        order = list(self._pinned_tabs)
        
        for group in self._groups.values():
            if not group.collapsed:
                order.extend(group.tab_ids)
                
        for tab_id in self._tabs:
            if tab_id not in order:
                order.append(tab_id)
                
        return order
        
    def get_memory_usage(self) -> Dict[str, int]:
        """Get memory usage per tab."""
        return {
            tab_id: tab["memory_usage"]
            for tab_id, tab in self._tabs.items()
        }
        
    def _check_hibernation(self) -> None:
        """Check if tabs should be hibernated."""
        active_count = sum(
            1 for t in self._tabs.values()
            if t["state"] == TabState.ACTIVE
        )
        
        if active_count > self.max_active_tabs:
            # Hibernate oldest non-pinned tabs
            for tab_id in self._tab_stack:
                if tab_id not in self._pinned_tabs:
                    if self._tabs[tab_id]["state"] == TabState.ACTIVE:
                        self.hibernate_tab(tab_id)
                        active_count -= 1
                        if active_count <= self.max_active_tabs:
                            break
                            
    def _notify_listeners(self, event: str, data: Any) -> None:
        """Notify event listeners."""
        for listener in self._listeners:
            try:
                listener(event, data)
            except Exception:
                pass
                
    def add_listener(self, listener: Callable) -> None:
        """Add event listener."""
        self._listeners.append(listener)
