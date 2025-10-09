"""
融资融券汇总相关的数据传输对象（DTO）
"""
from typing import List, Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field

from .base import PaginationInfoDTO, StandardResponseDTO, StandardListResponseDTO, TimestampFields, IdFields


class MarginSummaryItem(BaseModel, TimestampFields, IdFields):
    """融资融券市场汇总项"""
    trade_date: str = Field(..., description="交易日期（格式：YYYY-MM-DD）")
    exchange_id: Optional[str] = Field(None, description="交易所代码")
    rz_balance: Optional[int] = Field(None, description="融资余额(元)")
    rq_balance: Optional[int] = Field(None, description="融券余额(元)")
    rzrq_balance: Optional[int] = Field(None, description="融资融券余额(元)")
    rz_buy_amount: Optional[int] = Field(None, description="融资买入额(元)")
    rq_sell_amount: Optional[int] = Field(None, description="融券卖出额(元)")
    rz_repay_amount: Optional[int] = Field(None, description="融资偿还额(元)")
    rq_repay_amount: Optional[int] = Field(None, description="融券偿还额(元)")
    rz_net_buy_amount: Optional[int] = Field(None, description="融资净买入额(元)")
    rq_net_sell_amount: Optional[int] = Field(None, description="融券净卖出额(元)")
    rz_margin_ratio: Optional[float] = Field(None, description="融资保证金比例")
    rq_margin_ratio: Optional[float] = Field(None, description="融券保证金比例")


class MarginSummaryListResponse(StandardListResponseDTO):
    """融资融券市场汇总列表响应"""
    
    def __init__(self, **data):
        """初始化方法，处理没有data字段的情况"""
        # 如果传入的数据没有data字段，但有items或pagination字段，则将整个数据作为data
        if "data" not in data and ("items" in data or "pagination" in data):
            super().__init__(status=data.get("status", "success"), data=data)
        else:
            super().__init__(**data)
    
    @property
    def items(self) -> List[MarginSummaryItem]:
        """获取融资融券市场汇总项列表"""
        if isinstance(self.data, dict) and "items" in self.data:
            return [MarginSummaryItem(**item) if isinstance(item, dict) else item for item in self.data["items"]]
        elif isinstance(self.data, list):
            # 如果data直接是列表
            return [MarginSummaryItem(**item) if isinstance(item, dict) else item for item in self.data]
        return []
    
    @property
    def pagination(self) -> Optional[PaginationInfoDTO]:
        """获取分页信息"""
        if isinstance(self.data, dict) and "pagination" in self.data and self.data["pagination"]:
            return PaginationInfoDTO(**self.data["pagination"])
        return None
    
    @property
    def total(self) -> int:
        """获取总记录数"""
        if isinstance(self.data, dict) and "total" in self.data:
            return self.data["total"]
        if self.pagination:
            return self.pagination.total
        return len(self.items)


class MarginSummaryResponse(StandardResponseDTO):
    """融资融券市场汇总响应"""
    
    def __init__(self, **data):
        """初始化方法，处理没有data字段的情况"""
        # 如果传入的数据没有data字段，但有items或total字段，则将整个数据作为data
        if "data" not in data and ("items" in data or "total" in data):
            super().__init__(status=data.get("status", "success"), data=data)
        else:
            super().__init__(**data)
    
    @property
    def items(self) -> List[MarginSummaryItem]:
        """获取融资融券市场汇总项列表"""
        if isinstance(self.data, dict) and "items" in self.data:
            items_data = self.data["items"]
            return [MarginSummaryItem(**item) if isinstance(item, dict) else item for item in items_data]
        elif isinstance(self.data, list):
            # 如果data直接是列表
            return [MarginSummaryItem(**item) if isinstance(item, dict) else item for item in self.data]
        return []
    
    @property
    def total(self) -> int:
        """获取总记录数"""
        if isinstance(self.data, dict) and "total" in self.data:
            return self.data["total"]
        elif isinstance(self.data, list):
            # 如果data直接是列表
            return len(self.data)
        return 0