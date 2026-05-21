"""Soul Browser Privacy Manager.

Central management for all privacy protection features.
"""

from __future__ import annotations

import logging
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from ..config import PrivacyLevel, PrivacyConfig, get_privacy_config

logger = logging.getLogger("soulbrowser.privacy")


@dataclass
class PrivacyStats:
    """Statistics about privacy protection."""
    trackers_blocked: int = 0
    fingerprint_attempts_blocked: int = 0
    cookies_isolated: int = 0
    webrtc_leaks_prevented: int = 0
    dns_queries_encrypted: int = 0
    https_upgrades: int = 0


class PrivacyManager:
    """Central manager for Soul Browser privacy protection."""
    
    def __init__(
        self,
        level: PrivacyLevel = PrivacyLevel.STANDARD,
        config: Optional[PrivacyConfig] = None
    ):
        self.level = level
        self.config = config or get_privacy_config(level)
        self.stats = PrivacyStats()
        self._scripts: List[str] = []
        logger.info(f"Privacy Manager initialized with level: {level.name}")
    
    def get_injection_scripts(self) -> List[str]:
        """Get JavaScript injection scripts for privacy protection."""
        if self._scripts:
            return self._scripts
            
        scripts = []
        
        if self.config.hardware_randomization:
            scripts.append(self._get_navigator_protection_script())
        if self.config.canvas_protection:
            scripts.append(self._get_canvas_protection_script())
        if self.config.webgl_protection:
            scripts.append(self._get_webgl_protection_script())
        if self.config.audio_protection:
            scripts.append(self._get_audio_protection_script())
        if self.config.battery_api_blocked:
            scripts.append(self._get_battery_block_script())
        if self.config.sensor_api_blocked:
            scripts.append(self._get_sensor_block_script())
        if self.config.webrtc_protection:
            scripts.append(self._get_webrtc_protection_script())
        if self.config.tracking_protection:
            scripts.append(self._get_tracking_protection_script())
        
        self._scripts = scripts
        return scripts
    
    def _get_navigator_protection_script(self) -> str:
        seed = random.randint(1, 1000000)
        return f'''
(function() {{
    const seed = {seed};
    let s = seed;
    const random = function(min, max) {{
        const x = Math.sin(s++) * 10000;
        return Math.floor((x - Math.floor(x)) * (max - min + 1)) + min;
    }};
    Object.defineProperty(navigator, "hardwareConcurrency", {{ get: () => random(4, 16) }});
    Object.defineProperty(navigator, "deviceMemory", {{ get: () => [2, 4, 8, 16][random(0, 3)] }});
    Object.defineProperty(navigator, "platform", {{ get: () => "Win32" }});
    Object.defineProperty(navigator, "webdriver", {{ get: () => false }});
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
}})();
'''
    
    def _get_canvas_protection_script(self) -> str:
        return '''
(function() {
    const original = HTMLCanvasElement.prototype.toDataURL;
    HTMLCanvasElement.prototype.toDataURL = function(type, quality) {
        const ctx = this.getContext("2d");
        if (ctx) {
            const imageData = ctx.getImageData(0, 0, this.width, this.height);
            const data = imageData.data;
            for (let i = 0; i < data.length; i += 4) {
                data[i] = Math.max(0, Math.min(255, data[i] + Math.floor((Math.random() - 0.5) * 2)));
            }
            ctx.putImageData(imageData, 0, 0);
        }
        return original.apply(this, arguments);
    };
})();
'''
    
    def _get_webgl_protection_script(self) -> str:
        return '''
(function() {
    const orig = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(param) {
        if (param === 37445) return "Google Inc.";
        if (param === 37446) return "ANGLE (Intel HD Graphics)";
        return orig.apply(this, arguments);
    };
})();
'''
    
    def _get_audio_protection_script(self) -> str:
        return '''
(function() {
    const ctx = window.AudioContext || window.webkitAudioContext;
    if (!ctx) return;
    const orig = ctx.prototype.createAnalyser;
    ctx.prototype.createAnalyser = function() {
        const analyser = orig.apply(this, arguments);
        const origGet = analyser.getFloatFrequencyData;
        analyser.getFloatFrequencyData = function(array) {
            origGet.apply(this, arguments);
            for (let i = 0; i < array.length; i++) array[i] += (Math.random() - 0.5) * 0.1;
        };
        return analyser;
    };
})();
'''
    
    def _get_battery_block_script(self) -> str:
        return '''
(function() {
    if (navigator.getBattery) delete navigator.getBattery;
    Object.defineProperty(navigator, "getBattery", { get: () => undefined });
})();
'''
    
    def _get_sensor_block_script(self) -> str:
        return '''
(function() {
    ["Accelerometer", "Gyroscope", "Magnetometer", "AmbientLightSensor"].forEach(function(s) {
        if (window[s]) window[s] = function() { throw new Error("Blocked"); };
    });
})();
'''
    
    def _get_webrtc_protection_script(self) -> str:
        return '''
(function() {
    const orig = window.RTCPeerConnection || window.webkitRTCPeerConnection;
    if (orig) {
        window.RTCPeerConnection = function(cfg) {
            cfg = cfg || {};
            cfg.iceTransportPolicy = "relay";
            return new orig(cfg);
        };
        window.RTCPeerConnection.prototype = orig.prototype;
    }
})();
'''
    
    def _get_tracking_protection_script(self) -> str:
        return '''
(function() {
    const tracking = ["doubleclick.net", "google-analytics.com", "facebook.net", "analytics."];
    const orig = navigator.sendBeacon;
    navigator.sendBeacon = function(url, data) {
        if (tracking.some(function(d) { return url.includes(d); })) return true;
        return orig.apply(this, arguments);
    };
})();
'''
    
    def apply_to_page(self, page: Any) -> None:
        for script in self.get_injection_scripts():
            try:
                page.add_init_script(script)
            except Exception as e:
                logger.warning(f"Failed to inject script: {e}")
    
    async def apply_to_page_async(self, page: Any) -> None:
        for script in self.get_injection_scripts():
            try:
                await page.add_init_script(script)
            except Exception as e:
                logger.warning(f"Failed to inject script: {e}")
    
    def get_stats(self) -> PrivacyStats:
        return self.stats
    
    def reset_stats(self) -> None:
        self.stats = PrivacyStats()
