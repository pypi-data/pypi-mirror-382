
from datetime import datetime
from typing import Dict, List, Optional

from knowrithm_py.dataclass.response import AuthResponse
from knowrithm_py.knowrithm.client import KnowrithmClient


# Updated AuthService for API key management
class AuthService:
    """API Key and authentication service"""
    
    def __init__(self, client: KnowrithmClient):
        self.client = client
    
    def validate_credentials(self) -> Dict:
        """Validate current API key and secret"""
        return self.client._make_request("GET", "/auth/validate")
    
    def get_api_key_info(self) -> Dict:
        """Get information about the current API key"""
        return self.client._make_request("GET", "/auth/api-key/info")
    
    def refresh_api_key(self) -> Dict:
        """Refresh/rotate API key (if supported)"""
        return self.client._make_request("POST", "/auth/api-key/refresh")
    
    def revoke_api_key(self) -> Dict:
        """Revoke current API key"""
        return self.client._make_request("POST", "/auth/api-key/revoke")
    
    def list_api_keys(self) -> Dict:
        """List all API keys for the account"""
        return self.client._make_request("GET", "/auth/api-keys")
    
    def create_api_key(self, name: str, permissions: Optional[Dict] = None) -> Dict:
        """Create a new API key"""
        data = {"name": name}
        if permissions:
            data["permissions"] = permissions
        return self.client._make_request("POST", "/auth/api-keys", data)
    
    def delete_api_key(self, key_id: str) -> Dict:
        """Delete an API key"""
        return self.client._make_request("DELETE", f"/auth/api-keys/{key_id}")




class SessionService:
    """User session management service"""
    
    def __init__(self, client: KnowrithmClient):
        self.client = client
    
    def list_active_sessions(self) -> List[Dict]:
        """List active sessions for current user"""
        return self.client._make_request("GET", "/sessions")
    
    def revoke_session(self, session_id: str) -> Dict:
        """Revoke a specific session"""
        return self.client._make_request("DELETE", f"/sessions/{session_id}")
    
    def revoke_all_sessions(self) -> Dict:
        """Revoke all sessions except current"""
        return self.client._make_request("DELETE", "/sessions/all")
    
    def get_current_session(self) -> Dict:
        """Get current session details"""
        return self.client._make_request("GET", "/sessions/current")


class UserService:
    """User management service"""
    
    def __init__(self, client: KnowrithmClient):
        self.client = client
    
    def get_profile(self) -> Dict:
        """Get current user profile"""
        return self.client._make_request("GET", "/user/profile")
    
    def update_profile(self, profile_data: Dict) -> Dict:
        """Update current user profile"""
        return self.client._make_request("PUT", "/user/profile", profile_data)
    
    def get_user(self, user_id: str) -> Dict:
        """Get specific user details"""
        return self.client._make_request("GET", f"/user/{user_id}")
    
    def update_preferences(self, preferences: Dict) -> Dict:
        """Update user preferences"""
        return self.client._make_request("PATCH", "/user/preferences", {"preferences": preferences})
    
    def enable_two_factor(self) -> Dict:
        """Enable two-factor authentication"""
        return self.client._make_request("POST", "/user/2fa/enable")
    
    def disable_two_factor(self, totp_code: str) -> Dict:
        """Disable two-factor authentication"""
        return self.client._make_request("POST", "/user/2fa/disable", {"totp_code": totp_code})
    
    def verify_two_factor(self, totp_code: str) -> Dict:
        """Verify two-factor authentication code"""
        return self.client._make_request("POST", "/user/2fa/verify", {"totp_code": totp_code})

