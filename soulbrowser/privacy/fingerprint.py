"""Soul Browser Fingerprint Protection Module."""

from __future__ import annotations
import random
import hashlib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class FingerprintProfile:
    """A randomized fingerprint profile."""
    screen_width: int
    screen_height: int
    color_depth: int
    pixel_ratio: float
    timezone_offset: int
    language: str
    platform: str
    hardware_concurrency: int
    device_memory: int
    
    @classmethod
    def generate(cls, seed: Optional[int] = None) -> "FingerprintProfile":
        if seed:
            random.seed(seed)
        
        screens = [(1920, 1080), (2560, 1440), (1366, 768), (1440, 900), (1536, 864)]
        width, height = random.choice(screens)
        
        return cls(
            screen_width=width,
            screen_height=height,
            color_depth=random.choice([24, 32]),
            pixel_ratio=random.choice([1.0, 1.25, 1.5, 2.0]),
            timezone_offset=random.randint(-720, 720),
            language=random.choice(["en-US", "en-GB", "en"]),
            platform=random.choice(["Win32", "MacIntel", "Linux x86_64"]),
            hardware_concurrency=random.choice([4, 8, 12, 16]),
            device_memory=random.choice([4, 8, 16, 32])
        )


class FingerprintProtection:
    """Advanced fingerprint protection for Soul Browser."""
    
    def __init__(self, profile: Optional[FingerprintProfile] = None):
        self.profile = profile or FingerprintProfile.generate()
        self._noise_seed = random.randint(1, 1000000)
    
    def get_canvas_noise_script(self) -> str:
        return f'''
(function() {{
    const seed = {self._noise_seed};
    const orig = HTMLCanvasElement.prototype.toDataURL;
    HTMLCanvasElement.prototype.toDataURL = function() {{
        const ctx = this.getContext("2d");
        if (ctx) {{
            const img = ctx.getImageData(0, 0, this.width, this.height);
            for (let i = 0; i < img.data.length; i += 4) {{
                img.data[i] += Math.floor((Math.random() - 0.5) * 2);
            }}
            ctx.putImageData(img, 0, 0);
        }}
        return orig.apply(this, arguments);
    }};
}})();
'''
    
    def get_webgl_noise_script(self) -> str:
        return '''
(function() {
    const orig = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(p) {
        if (p === 37445) return "Google Inc.";
        if (p === 37446) return "ANGLE (Intel UHD Graphics)";
        return orig.apply(this, arguments);
    };
    const ext = WebGLRenderingContext.prototype.getExtension;
    WebGLRenderingContext.prototype.getExtension = function(name) {
        if (name === "WEBGL_debug_renderer_info") return null;
        return ext.apply(this, arguments);
    };
})();
'''
    
    def get_audio_noise_script(self) -> str:
        return '''
(function() {
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return;
    const orig = AC.prototype.createAnalyser;
    AC.prototype.createAnalyser = function() {
        const a = orig.apply(this, arguments);
        const gf = a.getFloatFrequencyData;
        a.getFloatFrequencyData = function(arr) {
            gf.apply(this, arguments);
            for (let i = 0; i < arr.length; i++) arr[i] += (Math.random() - 0.5) * 0.05;
        };
        return a;
    };
})();
'''
    
    def get_font_noise_script(self) -> str:
        return '''
(function() {
    const fonts = ["Arial", "Helvetica", "Times New Roman", "Georgia", "Verdana"];
    const orig = document.fonts.check;
    document.fonts.check = function(font) {
        const f = font.split(" ").pop().replace(/['"]/g, "");
        if (fonts.includes(f)) return orig.apply(this, arguments);
        return Math.random() > 0.7;
    };
})();
'''
    
    def get_screen_spoof_script(self) -> str:
        p = self.profile
        return f'''
(function() {{
    Object.defineProperty(screen, "width", {{ get: () => {p.screen_width} }});
    Object.defineProperty(screen, "height", {{ get: () => {p.screen_height} }});
    Object.defineProperty(screen, "availWidth", {{ get: () => {p.screen_width} }});
    Object.defineProperty(screen, "availHeight", {{ get: () => {p.screen_height - 40} }});
    Object.defineProperty(screen, "colorDepth", {{ get: () => {p.color_depth} }});
    Object.defineProperty(screen, "pixelDepth", {{ get: () => {p.color_depth} }});
    Object.defineProperty(window, "devicePixelRatio", {{ get: () => {p.pixel_ratio} }});
}})();
'''
    
    def get_all_scripts(self) -> List[str]:
        return [
            self.get_canvas_noise_script(),
            self.get_webgl_noise_script(),
            self.get_audio_noise_script(),
            self.get_font_noise_script(),
            self.get_screen_spoof_script(),
        ]
    
    def apply_to_page(self, page: Any) -> None:
        for script in self.get_all_scripts():
            try:
                page.add_init_script(script)
            except Exception:
                pass
    
    async def apply_to_page_async(self, page: Any) -> None:
        for script in self.get_all_scripts():
            try:
                await page.add_init_script(script)
            except Exception:
                pass
