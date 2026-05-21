"""Advanced media player controls."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import asyncio


@dataclass
class MediaInfo:
    """Media information."""
    url: str
    title: str
    duration: float
    current_time: float
    is_playing: bool
    is_muted: bool
    volume: float
    playback_rate: float
    media_type: str  # video, audio


@dataclass
class EqualizerPreset:
    """Audio equalizer preset."""
    name: str
    gains: Dict[str, float]  # frequency: gain


class MediaPlayer:
    """Advanced media player for Soul Browser."""
    
    EQUALIZER_PRESETS = {
        "flat": {"60": 0, "170": 0, "310": 0, "600": 0, "1k": 0, "3k": 0, "6k": 0, "12k": 0, "14k": 0, "16k": 0},
        "bass_boost": {"60": 6, "170": 4, "310": 2, "600": 0, "1k": 0, "3k": 0, "6k": 0, "12k": 0, "14k": 0, "16k": 0},
        "treble_boost": {"60": 0, "170": 0, "310": 0, "600": 0, "1k": 0, "3k": 2, "6k": 4, "12k": 5, "14k": 6, "16k": 6},
        "vocal": {"60": -2, "170": 0, "310": 2, "600": 4, "1k": 4, "3k": 2, "6k": 0, "12k": -2, "14k": -2, "16k": -4},
        "rock": {"60": 4, "170": 3, "310": 0, "600": -2, "1k": -1, "3k": 2, "6k": 4, "12k": 5, "14k": 5, "16k": 4},
    }
    
    def __init__(self):
        self._current_preset: str = "flat"
        self._pip_enabled: bool = False
        
    async def get_all_media(self, page) -> List[MediaInfo]:
        """Get all media elements on page."""
        return await page.evaluate("""() => {
            const media = [];
            
            document.querySelectorAll("video, audio").forEach(el => {
                media.push({
                    url: el.currentSrc || el.src,
                    title: el.title || document.title,
                    duration: el.duration || 0,
                    current_time: el.currentTime || 0,
                    is_playing: !el.paused,
                    is_muted: el.muted,
                    volume: el.volume,
                    playback_rate: el.playbackRate,
                    media_type: el.tagName.toLowerCase()
                });
            });
            
            return media;
        }""")
        
    async def play_all(self, page) -> None:
        """Play all media."""
        await page.evaluate("""() => {
            document.querySelectorAll("video, audio").forEach(el => {
                el.play().catch(() => {});
            });
        }""")
        
    async def pause_all(self, page) -> None:
        """Pause all media."""
        await page.evaluate("""() => {
            document.querySelectorAll("video, audio").forEach(el => {
                el.pause();
            });
        }""")
        
    async def mute_all(self, page) -> None:
        """Mute all media."""
        await page.evaluate("""() => {
            document.querySelectorAll("video, audio").forEach(el => {
                el.muted = true;
            });
        }""")
        
    async def unmute_all(self, page) -> None:
        """Unmute all media."""
        await page.evaluate("""() => {
            document.querySelectorAll("video, audio").forEach(el => {
                el.muted = false;
            });
        }""")
        
    async def set_playback_rate(self, page, rate: float) -> None:
        """Set playback rate for all media."""
        await page.evaluate(f"""() => {{
            document.querySelectorAll("video, audio").forEach(el => {{
                el.playbackRate = {rate};
            }});
        }}""")
        
    async def set_volume(self, page, volume: float) -> None:
        """Set volume for all media (0.0 to 1.0)."""
        volume = max(0.0, min(1.0, volume))
        await page.evaluate(f"""() => {{
            document.querySelectorAll("video, audio").forEach(el => {{
                el.volume = {volume};
            }});
        }}""")
        
    async def enable_pip(self, page) -> bool:
        """Enable Picture-in-Picture for first video."""
        result = await page.evaluate("""async () => {
            const video = document.querySelector("video");
            if (video && document.pictureInPictureEnabled) {
                try {
                    await video.requestPictureInPicture();
                    return true;
                } catch (e) {
                    return false;
                }
            }
            return false;
        }""")
        self._pip_enabled = result
        return result
        
    async def disable_pip(self, page) -> bool:
        """Disable Picture-in-Picture."""
        result = await page.evaluate("""async () => {
            if (document.pictureInPictureElement) {
                await document.exitPictureInPicture();
                return true;
            }
            return false;
        }""")
        self._pip_enabled = not result
        return result
        
    async def apply_equalizer(self, page, preset: str = "flat") -> bool:
        """Apply equalizer preset."""
        if preset not in self.EQUALIZER_PRESETS:
            return False
            
        gains = self.EQUALIZER_PRESETS[preset]
        self._current_preset = preset
        
        await page.evaluate(f"""() => {{
            const gains = {gains};
            
            document.querySelectorAll("audio, video").forEach(el => {{
                if (!el._audioContext) {{
                    el._audioContext = new (window.AudioContext || window.webkitAudioContext)();
                    el._source = el._audioContext.createMediaElementSource(el);
                    el._filters = [];
                    
                    const frequencies = [60, 170, 310, 600, 1000, 3000, 6000, 12000, 14000, 16000];
                    frequencies.forEach((freq, i) => {{
                        const filter = el._audioContext.createBiquadFilter();
                        filter.type = i === 0 ? "lowshelf" : i === frequencies.length - 1 ? "highshelf" : "peaking";
                        filter.frequency.value = freq;
                        filter.Q.value = 1;
                        filter.gain.value = 0;
                        el._filters.push(filter);
                    }});
                    
                    el._source.connect(el._filters[0]);
                    for (let i = 0; i < el._filters.length - 1; i++) {{
                        el._filters[i].connect(el._filters[i + 1]);
                    }}
                    el._filters[el._filters.length - 1].connect(el._audioContext.destination);
                }}
                
                const keys = ["60", "170", "310", "600", "1k", "3k", "6k", "12k", "14k", "16k"];
                keys.forEach((key, i) => {{
                    if (el._filters[i]) {{
                        el._filters[i].gain.value = gains[key] || 0;
                    }}
                }});
            }});
        }}""")
        return True
        
    async def prevent_autoplay(self, page) -> None:
        """Prevent video/audio autoplay."""
        await page.evaluate("""() => {
            // Prevent autoplay on existing media
            document.querySelectorAll("video[autoplay], audio[autoplay]").forEach(el => {
                el.removeAttribute("autoplay");
                el.pause();
            });
            
            // Observer for new media
            const observer = new MutationObserver(mutations => {
                mutations.forEach(m => {
                    m.addedNodes.forEach(node => {
                        if (node.tagName === "VIDEO" || node.tagName === "AUDIO") {
                            node.removeAttribute("autoplay");
                            node.pause();
                        }
                        if (node.querySelectorAll) {
                            node.querySelectorAll("video[autoplay], audio[autoplay]").forEach(el => {
                                el.removeAttribute("autoplay");
                                el.pause();
                            });
                        }
                    });
                });
            });
            
            observer.observe(document.body, { childList: true, subtree: true });
        }""")
        
    async def download_media(self, page, url: str) -> Dict[str, Any]:
        """Get media download info."""
        return await page.evaluate(f"""async () => {{
            const url = "{url}";
            try {{
                const response = await fetch(url, {{ method: "HEAD" }});
                return {{
                    url: url,
                    size: response.headers.get("content-length"),
                    type: response.headers.get("content-type"),
                    downloadable: true
                }};
            }} catch (e) {{
                return {{ url: url, downloadable: false, error: e.message }};
            }}
        }}""")
