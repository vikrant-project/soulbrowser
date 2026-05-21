"""Screen and media recording capabilities."""

from dataclasses import dataclass
from typing import Dict, Optional, Any
from enum import Enum


class RecordingFormat(Enum):
    WEBM = "webm"
    MP4 = "mp4"
    GIF = "gif"


@dataclass
class RecordingConfig:
    """Recording configuration."""
    format: RecordingFormat = RecordingFormat.WEBM
    quality: str = "high"  # low, medium, high
    audio: bool = True
    video: bool = True
    fps: int = 30
    resolution: str = "1080p"


class MediaRecorder:
    """Screen and media recording for Soul Browser."""
    
    def __init__(self, config: Optional[RecordingConfig] = None):
        self.config = config or RecordingConfig()
        self._is_recording: bool = False
        
    async def start_screen_recording(self, page) -> bool:
        """Start screen recording."""
        quality_map = {
            "low": 1000000,
            "medium": 2500000,
            "high": 5000000
        }
        bitrate = quality_map.get(self.config.quality, 2500000)
        
        result = await page.evaluate(f"""async () => {{
            try {{
                const stream = await navigator.mediaDevices.getDisplayMedia({{
                    video: {{ mediaSource: "screen" }},
                    audio: {str(self.config.audio).lower()}
                }});
                
                window._soulRecorder = new MediaRecorder(stream, {{
                    mimeType: "video/webm;codecs=vp9",
                    videoBitsPerSecond: {bitrate}
                }});
                
                window._soulRecordedChunks = [];
                
                window._soulRecorder.ondataavailable = (e) => {{
                    if (e.data.size > 0) {{
                        window._soulRecordedChunks.push(e.data);
                    }}
                }};
                
                window._soulRecorder.start(1000);
                return true;
            }} catch (e) {{
                console.error("Recording failed:", e);
                return false;
            }}
        }}""")
        
        self._is_recording = result
        return result
        
    async def stop_screen_recording(self, page) -> Optional[str]:
        """Stop recording and get download URL."""
        if not self._is_recording:
            return None
            
        result = await page.evaluate("""async () => {
            return new Promise(resolve => {
                if (!window._soulRecorder) {
                    resolve(null);
                    return;
                }
                
                window._soulRecorder.onstop = () => {
                    const blob = new Blob(window._soulRecordedChunks, { type: "video/webm" });
                    const url = URL.createObjectURL(blob);
                    resolve(url);
                };
                
                window._soulRecorder.stop();
                window._soulRecorder.stream.getTracks().forEach(t => t.stop());
            });
        }""")
        
        self._is_recording = False
        return result
        
    async def take_screenshot(
        self,
        page,
        full_page: bool = False,
        selector: Optional[str] = None
    ) -> bytes:
        """Take screenshot."""
        if selector:
            element = await page.query_selector(selector)
            if element:
                return await element.screenshot()
        return await page.screenshot(full_page=full_page)
        
    async def capture_tab_audio(self, page) -> bool:
        """Capture audio from current tab."""
        return await page.evaluate("""async () => {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                window._soulAudioRecorder = new MediaRecorder(stream, {
                    mimeType: "audio/webm"
                });
                
                window._soulAudioChunks = [];
                
                window._soulAudioRecorder.ondataavailable = (e) => {
                    if (e.data.size > 0) {
                        window._soulAudioChunks.push(e.data);
                    }
                };
                
                window._soulAudioRecorder.start(1000);
                return true;
            } catch (e) {
                return false;
            }
        }""")
        
    @property
    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self._is_recording
