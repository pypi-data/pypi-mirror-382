from __future__ import annotations
from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..base import BaseClient

from ..dto.margin_summary import (
    MarginSummaryListResponse,
    MarginSummaryResponse
)


class MarginSummaryClient:
    """Client for Margin Summary related endpoints."""
    def __init__(self, client: "BaseClient"):
        self._client = client

    def page_list(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        exchange_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> MarginSummaryListResponse:
        """
        Get a paginated list of margin market summaries.
        Corresponds to GET /margin_summary/page_list
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            exchange_id: Exchange ID
            page: Page number (default: 1)
            page_size: Number of items per page (default: 10)
            
        Returns:
            MarginSummaryListResponse containing paginated margin market summary data
        """
        params: Dict[str, Any] = {"page": page, "page_size": page_size}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if exchange_id:
            params["exchange_id"] = exchange_id
        
        response_data = self._client._request("GET", "/api/v1/margin_summary/page_list", params=params)
        return MarginSummaryListResponse(**response_data)

    def list(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        exchange_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> MarginSummaryResponse:
        """
        Get a list of margin market summaries without pagination.
        Corresponds to GET /api/v1/margin_summary/list
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            exchange_id: Exchange ID
            limit: Maximum number of records to return
            
        Returns:
            MarginSummaryResponse containing margin market summary data
        """
        params: Dict[str, Any] = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if exchange_id:
            params["exchange_id"] = exchange_id
        if limit:
            params["limit"] = limit
        
        response_data = self._client._request("GET", "/api/v1/margin_summary/list", params=params)
        return MarginSummaryResponse(**response_data)