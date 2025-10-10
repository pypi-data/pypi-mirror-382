from typing import Dict, List, Set
from datetime import datetime, timedelta
from snapqrpy.utils.logger import Logger

class FirewallManager:
    def __init__(self):
        self.logger = Logger("FirewallManager")
        self.blocked_ips: Set[str] = set()
        self.rate_limits: Dict[str, List[datetime]] = {}
        self.max_requests_per_minute = 60
        
    def block_ip(self, ip: str):
        self.blocked_ips.add(ip)
        self.logger.info(f"Blocked IP: {ip}")
        
    def unblock_ip(self, ip: str):
        self.blocked_ips.discard(ip)
        self.logger.info(f"Unblocked IP: {ip}")
        
    def is_blocked(self, ip: str) -> bool:
        return ip in self.blocked_ips
        
    def check_rate_limit(self, ip: str) -> bool:
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        
        if ip not in self.rate_limits:
            self.rate_limits[ip] = []
        
        self.rate_limits[ip] = [t for t in self.rate_limits[ip] if t > minute_ago]
        
        if len(self.rate_limits[ip]) >= self.max_requests_per_minute:
            self.logger.warning(f"Rate limit exceeded for IP: {ip}")
            return False
        
        self.rate_limits[ip].append(now)
        return True
