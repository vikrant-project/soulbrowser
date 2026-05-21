"""Soul Browser Automation Module."""

from __future__ import annotations
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass

logger = logging.getLogger("soulbrowser.automation")


@dataclass
class MacroStep:
    """A single step in a macro."""
    action: str
    selector: Optional[str] = None
    value: Optional[str] = None
    wait: float = 0.0


class ScriptRunner:
    """Run user scripts (Greasemonkey/Tampermonkey compatible)."""
    
    def __init__(self):
        self._scripts: Dict[str, str] = {}
    
    def add_script(self, name: str, script: str) -> None:
        self._scripts[name] = script
    
    def remove_script(self, name: str) -> None:
        self._scripts.pop(name, None)
    
    def get_injection_script(self) -> str:
        if not self._scripts:
            return ""
        
        combined = "\n".join(self._scripts.values())
        return f'''
(function() {{
    {combined}
}})();
'''
    
    def apply_to_page(self, page: Any) -> None:
        script = self.get_injection_script()
        if script:
            try:
                page.add_init_script(script)
            except Exception as e:
                logger.warning(f"Failed to inject user script: {e}")


class AutomationManager:
    """Automation manager for Soul Browser.
    
    Provides macro recording, task scheduling, and browser automation.
    """
    
    def __init__(self):
        self._macros: Dict[str, List[MacroStep]] = {}
        self._script_runner = ScriptRunner()
    
    def record_macro(self, name: str, steps: List[MacroStep]) -> None:
        self._macros[name] = steps
    
    def get_macro(self, name: str) -> Optional[List[MacroStep]]:
        return self._macros.get(name)
    
    async def run_macro(self, page: Any, name: str) -> bool:
        steps = self._macros.get(name)
        if not steps:
            return False
        
        for step in steps:
            try:
                if step.action == "click":
                    await page.click(step.selector)
                elif step.action == "type":
                    await page.type(step.selector, step.value)
                elif step.action == "goto":
                    await page.goto(step.value)
                elif step.action == "wait":
                    await page.wait_for_timeout(int(step.wait * 1000))
                
                if step.wait > 0:
                    await page.wait_for_timeout(int(step.wait * 1000))
            except Exception as e:
                logger.error(f"Macro step failed: {e}")
                return False
        
        return True
    
    @property
    def script_runner(self) -> ScriptRunner:
        return self._script_runner
