from datetime import datetime, timedelta
from typing import Dict, Optional, List
from enum import Enum
from snapqrpy.utils.logger import Logger

class PermissionType(Enum):
    SCREEN_SHARE = "screen_share"
    REMOTE_CONTROL = "remote_control"
    FILE_TRANSFER = "file_transfer"
    AUDIO_SHARE = "audio_share"
    CAMERA_ACCESS = "camera_access"
    MICROPHONE_ACCESS = "microphone_access"

class ConsentStatus(Enum):
    PENDING = "pending"
    GRANTED = "granted"
    DENIED = "denied"
    EXPIRED = "expired"
    REVOKED = "revoked"

class ConsentManager:
    def __init__(self, default_timeout: int = 30):
        self.default_timeout = default_timeout
        self.logger = Logger("ConsentManager")
        self.permissions: Dict[str, Dict] = {}
        self.consent_history: List[Dict] = []
        
    def request_permission(self, session_id: str, permission_type: PermissionType, timeout: Optional[int] = None) -> bool:
        timeout = timeout or self.default_timeout
        expiry = datetime.now() + timedelta(seconds=timeout)
        
        self.permissions[session_id] = {
            "type": permission_type,
            "status": ConsentStatus.PENDING,
            "requested_at": datetime.now(),
            "expires_at": expiry,
            "granted_at": None,
        }
        
        self.logger.info(f"Permission request for {permission_type.value} from session {session_id}")
        return True
    
    def grant_permission(self, session_id: str) -> bool:
        if session_id not in self.permissions:
            self.logger.warning(f"No permission request found for session {session_id}")
            return False
        
        perm = self.permissions[session_id]
        if datetime.now() > perm["expires_at"]:
            perm["status"] = ConsentStatus.EXPIRED
            self.logger.warning(f"Permission request expired for session {session_id}")
            return False
        
        perm["status"] = ConsentStatus.GRANTED
        perm["granted_at"] = datetime.now()
        self.consent_history.append({
            "session_id": session_id,
            "action": "granted",
            "timestamp": datetime.now(),
        })
        self.logger.info(f"Permission granted for session {session_id}")
        return True
    
    def deny_permission(self, session_id: str) -> bool:
        if session_id not in self.permissions:
            return False
        
        self.permissions[session_id]["status"] = ConsentStatus.DENIED
        self.consent_history.append({
            "session_id": session_id,
            "action": "denied",
            "timestamp": datetime.now(),
        })
        self.logger.info(f"Permission denied for session {session_id}")
        return True
    
    def revoke_permission(self, session_id: str) -> bool:
        if session_id not in self.permissions:
            return False
        
        self.permissions[session_id]["status"] = ConsentStatus.REVOKED
        self.consent_history.append({
            "session_id": session_id,
            "action": "revoked",
            "timestamp": datetime.now(),
        })
        self.logger.info(f"Permission revoked for session {session_id}")
        return True
    
    def check_permission(self, session_id: str) -> bool:
        if session_id not in self.permissions:
            return False
        
        perm = self.permissions[session_id]
        if perm["status"] != ConsentStatus.GRANTED:
            return False
        
        if datetime.now() > perm["expires_at"]:
            perm["status"] = ConsentStatus.EXPIRED
            return False
        
        return True
    
    def get_consent_history(self) -> List[Dict]:
        return self.consent_history
