"""Soul Browser Web3 Module."""

from __future__ import annotations
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger("soulbrowser.web3")


class Web3Wallet:
    """Web3 wallet integration for Soul Browser.
    
    Supports cryptocurrency wallets and DApp interactions.
    """
    
    def __init__(self):
        self._connected = False
        self._address: Optional[str] = None
        self._chain_id: int = 1  # Ethereum mainnet
    
    def get_injection_script(self) -> str:
        """Get script to inject Web3 wallet provider."""
        return '''
(function() {
    // Soul Browser Web3 Provider
    window.soulBrowserProvider = {
        isMetaMask: false,
        isSoulBrowser: true,
        chainId: "0x1",
        networkVersion: "1",
        selectedAddress: null,
        
        request: async function(args) {
            const method = args.method;
            const params = args.params || [];
            
            switch(method) {
                case "eth_requestAccounts":
                case "eth_accounts":
                    return this.selectedAddress ? [this.selectedAddress] : [];
                case "eth_chainId":
                    return this.chainId;
                case "net_version":
                    return this.networkVersion;
                default:
                    throw new Error("Method not supported: " + method);
            }
        },
        
        on: function(event, callback) {},
        removeListener: function(event, callback) {},
    };
    
    // Expose as ethereum provider
    if (!window.ethereum) {
        window.ethereum = window.soulBrowserProvider;
    }
})();
'''
    
    def apply_to_page(self, page: Any) -> None:
        try:
            page.add_init_script(self.get_injection_script())
        except Exception as e:
            logger.warning(f"Failed to inject Web3 provider: {e}")


class IPFSClient:
    """IPFS protocol support for Soul Browser."""
    
    def __init__(self, gateway: str = "https://ipfs.io"):
        self.gateway = gateway
    
    def resolve_ipfs_url(self, url: str) -> str:
        """Resolve IPFS URL to HTTP gateway URL."""
        if url.startswith("ipfs://"):
            cid = url[7:]
            return f"{self.gateway}/ipfs/{cid}"
        return url
    
    def get_injection_script(self) -> str:
        """Get script for IPFS URL handling."""
        return f'''
(function() {{
    const gateway = "{self.gateway}";
    
    // Intercept fetch for IPFS URLs
    const origFetch = window.fetch;
    window.fetch = function(url, options) {{
        if (typeof url === "string" && url.startsWith("ipfs://")) {{
            url = gateway + "/ipfs/" + url.substring(7);
        }}
        return origFetch.call(this, url, options);
    }};
}})();
'''


class BlockchainExplorer:
    """Blockchain explorer integration."""
    
    EXPLORERS = {
        1: "https://etherscan.io",
        137: "https://polygonscan.com",
        56: "https://bscscan.com",
        43114: "https://snowtrace.io",
    }
    
    def __init__(self, chain_id: int = 1):
        self.chain_id = chain_id
    
    def get_explorer_url(self) -> str:
        return self.EXPLORERS.get(self.chain_id, "https://etherscan.io")
    
    def get_address_url(self, address: str) -> str:
        return f"{self.get_explorer_url()}/address/{address}"
    
    def get_tx_url(self, tx_hash: str) -> str:
        return f"{self.get_explorer_url()}/tx/{tx_hash}"
