"""Soul Browser WebRTC Protection Module."""

from __future__ import annotations
import logging
from typing import Optional, Any

logger = logging.getLogger("soulbrowser.webrtc")


class WebRTCProtection:
    """WebRTC leak protection for Soul Browser.
    
    Prevents IP address leaks through WebRTC connections.
    """
    
    def __init__(self, mode: str = "relay_only"):
        """Initialize WebRTC protection.
        
        Args:
            mode: Protection mode - "relay_only", "disable", or "spoof"
        """
        self.mode = mode
        self._leak_count = 0
    
    def get_protection_script(self) -> str:
        """Get JavaScript for WebRTC protection."""
        if self.mode == "disable":
            return '''
(function() {
    window.RTCPeerConnection = undefined;
    window.webkitRTCPeerConnection = undefined;
    window.mozRTCPeerConnection = undefined;
    window.RTCDataChannel = undefined;
    window.RTCSessionDescription = undefined;
    window.RTCIceCandidate = undefined;
})();
'''
        elif self.mode == "spoof":
            return '''
(function() {
    const orig = window.RTCPeerConnection || window.webkitRTCPeerConnection;
    if (!orig) return;
    
    window.RTCPeerConnection = function(config) {
        config = config || {};
        config.iceTransportPolicy = "relay";
        
        const pc = new orig(config);
        const origCreateOffer = pc.createOffer.bind(pc);
        const origCreateAnswer = pc.createAnswer.bind(pc);
        
        pc.createOffer = function(options) {
            return origCreateOffer(options).then(function(offer) {
                offer.sdp = offer.sdp.replace(/c=IN IP4 [0-9.]+/g, "c=IN IP4 0.0.0.0");
                return offer;
            });
        };
        
        pc.createAnswer = function(options) {
            return origCreateAnswer(options).then(function(answer) {
                answer.sdp = answer.sdp.replace(/c=IN IP4 [0-9.]+/g, "c=IN IP4 0.0.0.0");
                return answer;
            });
        };
        
        return pc;
    };
    window.RTCPeerConnection.prototype = orig.prototype;
    window.webkitRTCPeerConnection = window.RTCPeerConnection;
})();
'''
        else:  # relay_only (default)
            return '''
(function() {
    const orig = window.RTCPeerConnection || window.webkitRTCPeerConnection;
    if (!orig) return;
    
    window.RTCPeerConnection = function(config) {
        config = config || {};
        config.iceTransportPolicy = "relay";
        return new orig(config);
    };
    window.RTCPeerConnection.prototype = orig.prototype;
    window.webkitRTCPeerConnection = window.RTCPeerConnection;
})();
'''
    
    def apply_to_page(self, page: Any) -> None:
        try:
            page.add_init_script(self.get_protection_script())
        except Exception as e:
            logger.warning(f"Failed to apply WebRTC protection: {e}")
    
    async def apply_to_page_async(self, page: Any) -> None:
        try:
            await page.add_init_script(self.get_protection_script())
        except Exception as e:
            logger.warning(f"Failed to apply WebRTC protection: {e}")
