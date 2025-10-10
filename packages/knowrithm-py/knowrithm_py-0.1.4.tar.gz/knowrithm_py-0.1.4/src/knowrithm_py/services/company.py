

from typing import Dict, List

from knowrithm_py.knowrithm.client import KnowrithmClient


class CompanyService:
    """Company management service"""
    
    def __init__(self, client: KnowrithmClient):
        self.client = client
    
    # def create(self, company_data: Dict) -> Dict:
    #     """Create a new company"""
    #     return self.client._make_request("POST", "/company", company_data)
    
    def list(self, active_only: bool = True) -> List[Dict]:
        """List companies"""
        params = {"active_only": active_only}
        return self.client._make_request("GET", "/company", params=params)
    
    def get(self) -> Dict:
        """Get company details"""
        return self.client._make_request("GET", f"/company")
    
    # def update(self, company_id: str, company_data: Dict) -> Dict:
    #     """Update company information"""
    #     return self.client._make_request("PUT", f"/company/{company_id}", company_data)
    
    # def patch(self, company_id: str, company_data: Dict) -> Dict:
    #     """Partially update company information"""
    #     return self.client._make_request("PATCH", f"/company/{company_id}", company_data)
    
    # def delete(self, company_id: str) -> Dict:
    #     """Soft delete a company"""
    #     return self.client._make_request("DELETE", f"/company/{company_id}")
    
    # def restore(self, company_id: str) -> Dict:
    #     """Restore a soft-deleted company"""
    #     return self.client._make_request("PATCH", f"/company/{company_id}/restore")
    
    def get_statistics(self, days=None) -> Dict:
        """Get company statistics and metrics"""
        return self.client._make_request("GET", f"/company/statistics", params={"days": days} if days else None)
    
    # def verify_company(self, company_id: str) -> Dict:
    #     """Verify a company (admin only)"""
    #     return self.client._make_request("PATCH", f"/company/{company_id}/verify")
