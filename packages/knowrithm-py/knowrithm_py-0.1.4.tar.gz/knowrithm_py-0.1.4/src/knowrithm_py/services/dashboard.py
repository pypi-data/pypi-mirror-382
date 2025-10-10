
from typing import Dict, Optional

from knowrithm_py.knowrithm.client import KnowrithmClient


class AnalyticsService:
    """Analytics and monitoring service"""
    
    def __init__(self, client: KnowrithmClient):
        self.client = client
    
    def get_dashboard(self, company_id: Optional[str] = None) -> Dict:
        """Get comprehensive dashboard data"""
        params = {"company_id": company_id} if company_id else {}
        return self.client._make_request("GET", "/analytic/dashboard", params=params)
    
    def get_agent_metrics(self, agent_id: str, start_date: Optional[str] = None, 
                         end_date: Optional[str] = None) -> Dict:
        """Get metrics for specific agent"""
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self.client._make_request("GET", f"/analytic/agent/{agent_id}", params=params)
    
    
    def get_agent_performance_comparison(self, agent_id: str, start_date: Optional[str] = None, 
                         end_date: Optional[str] = None) -> Dict:
        """Get metrics for specific agent"""
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self.client._make_request("GET", f"/analytic/agent/{agent_id}/performance-comparison", params=params)
    
    
    def get_conversation_analytics(self, conversation_id: str) -> Dict:
        """Get analytics for specific conversation"""
        return self.client._make_request("GET", f"/analytic/conversation/{conversation_id}")
    
    def get_lead_analytics(self, start_date: Optional[str] = None, 
                         end_date: Optional[str] = None) -> Dict:
        """Get lead conversion analytics"""
        # params = {"company_id": company_id} if company_id else {}
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self.client._make_request("GET", "/analytic/leads", params=params)
    
    def get_usage_metrics(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict:
        """Get platform usage metrics"""
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self.client._make_request("GET", "/analytic/usage", params=params)
    
    def health_check(self) -> Dict:
        """System health check"""
        return self.client._make_request("GET", "/health", authenticated=False)

