"""Soul Browser Gesture Controls."""

from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable, Any
from enum import Enum

logger = logging.getLogger("soulbrowser.ui.gestures")


class GestureType(Enum):
    """Supported gesture types."""
    SWIPE_LEFT = "swipe_left"
    SWIPE_RIGHT = "swipe_right"
    SWIPE_UP = "swipe_up"
    SWIPE_DOWN = "swipe_down"
    PINCH_IN = "pinch_in"
    PINCH_OUT = "pinch_out"
    TWO_FINGER_TAP = "two_finger_tap"
    THREE_FINGER_SWIPE_LEFT = "three_finger_swipe_left"
    THREE_FINGER_SWIPE_RIGHT = "three_finger_swipe_right"
    ROTATE_LEFT = "rotate_left"
    ROTATE_RIGHT = "rotate_right"
    LONG_PRESS = "long_press"


class GestureAction(Enum):
    """Actions that can be triggered by gestures."""
    BACK = "back"
    FORWARD = "forward"
    REFRESH = "refresh"
    NEW_TAB = "new_tab"
    CLOSE_TAB = "close_tab"
    SWITCH_TAB_LEFT = "switch_tab_left"
    SWITCH_TAB_RIGHT = "switch_tab_right"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    SCROLL_TOP = "scroll_top"
    SCROLL_BOTTOM = "scroll_bottom"
    FULLSCREEN = "fullscreen"
    SCREENSHOT = "screenshot"
    COPY_URL = "copy_url"
    BOOKMARK = "bookmark"


@dataclass
class GestureBinding:
    """Gesture to action binding."""
    gesture: GestureType
    action: GestureAction
    enabled: bool = True


class GestureController:
    """Mouse and touch gesture controller."""
    
    DEFAULT_BINDINGS = {
        GestureType.SWIPE_LEFT: GestureAction.FORWARD,
        GestureType.SWIPE_RIGHT: GestureAction.BACK,
        GestureType.SWIPE_DOWN: GestureAction.NEW_TAB,
        GestureType.SWIPE_UP: GestureAction.CLOSE_TAB,
        GestureType.PINCH_IN: GestureAction.ZOOM_OUT,
        GestureType.PINCH_OUT: GestureAction.ZOOM_IN,
        GestureType.TWO_FINGER_TAP: GestureAction.REFRESH,
        GestureType.THREE_FINGER_SWIPE_LEFT: GestureAction.SWITCH_TAB_LEFT,
        GestureType.THREE_FINGER_SWIPE_RIGHT: GestureAction.SWITCH_TAB_RIGHT,
        GestureType.LONG_PRESS: GestureAction.COPY_URL,
    }
    
    def __init__(self):
        self._bindings: Dict[GestureType, GestureAction] = dict(self.DEFAULT_BINDINGS)
        self._enabled = True
        self._mouse_gestures_enabled = True
        self._touch_gestures_enabled = True
        self._action_handlers: Dict[GestureAction, Callable] = {}
    
    @property
    def enabled(self) -> bool:
        return self._enabled
    
    def enable(self) -> None:
        self._enabled = True
    
    def disable(self) -> None:
        self._enabled = False
    
    def set_binding(self, gesture: GestureType, action: GestureAction) -> None:
        """Set a gesture binding."""
        self._bindings[gesture] = action
    
    def remove_binding(self, gesture: GestureType) -> None:
        """Remove a gesture binding."""
        self._bindings.pop(gesture, None)
    
    def get_action(self, gesture: GestureType) -> Optional[GestureAction]:
        """Get the action for a gesture."""
        return self._bindings.get(gesture)
    
    def register_handler(self, action: GestureAction, handler: Callable) -> None:
        """Register a handler for an action."""
        self._action_handlers[action] = handler
    
    def handle_gesture(self, gesture: GestureType) -> bool:
        """Handle a gesture event."""
        if not self._enabled:
            return False
        
        action = self._bindings.get(gesture)
        if not action:
            return False
        
        handler = self._action_handlers.get(action)
        if handler:
            try:
                handler()
                return True
            except Exception as e:
                logger.error(f"Gesture handler failed: {e}")
        
        return False
    
    def get_mouse_gesture_script(self) -> str:
        """Get script for mouse gesture detection."""
        return """
(function() {
    let startX, startY, isRightClick = false;
    const THRESHOLD = 50;
    
    document.addEventListener("mousedown", function(e) {
        if (e.button === 2) {
            isRightClick = true;
            startX = e.clientX;
            startY = e.clientY;
        }
    });
    
    document.addEventListener("mouseup", function(e) {
        if (!isRightClick) return;
        isRightClick = false;
        
        const dx = e.clientX - startX;
        const dy = e.clientY - startY;
        
        if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > THRESHOLD) {
            const gesture = dx > 0 ? "swipe_right" : "swipe_left";
            window.postMessage({ type: "soul_gesture", gesture: gesture }, "*");
        } else if (Math.abs(dy) > THRESHOLD) {
            const gesture = dy > 0 ? "swipe_down" : "swipe_up";
            window.postMessage({ type: "soul_gesture", gesture: gesture }, "*");
        }
    });
    
    document.addEventListener("contextmenu", function(e) {
        if (Math.abs(e.clientX - startX) > 10 || Math.abs(e.clientY - startY) > 10) {
            e.preventDefault();
        }
    });
})();
"""
    
    def get_touch_gesture_script(self) -> str:
        """Get script for touch gesture detection."""
        return """
(function() {
    let touches = [];
    const THRESHOLD = 50;
    
    document.addEventListener("touchstart", function(e) {
        touches = Array.from(e.touches).map(t => ({x: t.clientX, y: t.clientY}));
    }, { passive: true });
    
    document.addEventListener("touchend", function(e) {
        if (touches.length === 0) return;
        
        const endTouches = Array.from(e.changedTouches).map(t => ({x: t.clientX, y: t.clientY}));
        const dx = endTouches[0].x - touches[0].x;
        const dy = endTouches[0].y - touches[0].y;
        
        let gesture = null;
        const fingerCount = touches.length;
        
        if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > THRESHOLD) {
            if (fingerCount === 3) {
                gesture = dx > 0 ? "three_finger_swipe_right" : "three_finger_swipe_left";
            } else {
                gesture = dx > 0 ? "swipe_right" : "swipe_left";
            }
        } else if (Math.abs(dy) > THRESHOLD) {
            gesture = dy > 0 ? "swipe_down" : "swipe_up";
        }
        
        if (gesture) {
            window.postMessage({ type: "soul_gesture", gesture: gesture }, "*");
        }
        
        touches = [];
    }, { passive: true });
})();
"""
    
    def apply_to_page(self, page: Any) -> None:
        """Apply gesture scripts to a page."""
        if not self._enabled:
            return
        try:
            if self._mouse_gestures_enabled:
                page.add_init_script(self.get_mouse_gesture_script())
            if self._touch_gestures_enabled:
                page.add_init_script(self.get_touch_gesture_script())
        except Exception as e:
            logger.warning(f"Failed to inject gesture scripts: {e}")
    
    def export_bindings(self) -> List[Dict]:
        """Export gesture bindings."""
        return [
            {"gesture": g.value, "action": a.value}
            for g, a in self._bindings.items()
        ]
    
    def import_bindings(self, bindings: List[Dict]) -> None:
        """Import gesture bindings."""
        for binding in bindings:
            try:
                gesture = GestureType(binding["gesture"])
                action = GestureAction(binding["action"])
                self._bindings[gesture] = action
            except (KeyError, ValueError) as e:
                logger.warning(f"Invalid binding: {binding}, {e}")
