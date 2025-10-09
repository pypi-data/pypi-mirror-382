"""
融资融券交易汇总相关的Pydantic模型
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class MarginMarketSummaryBase(BaseModel):
    trade_date: str = Field(..., description="交易日期（格式：YYYYMMDD）")
    exchange_id: str = Field(..., description="交易所代码（SSE上交所SZSE深交所BSE北交所，ALL表示全市场汇总）")
    rzye: Optional[float] = Field(None, description="融资余额(元)")
    rzmre: Optional[float] = Field(None, description="融资买入额(元)")
    rzche: Optional[float] = Field(None, description="融资偿还额(元)")
    rzjme: Optional[float] = Field(None, description="融资净买入额(元)")
    rqye: Optional[float] = Field(None, description="融券余额(元)")
    rqmcl: Optional[float] = Field(None, description="融券卖出量(股,份,手)")
    rzrqye: Optional[float] = Field(None, description="融资融券余额(元)")
    rqyl: Optional[float] = Field(None, description="融券余量(股,份,手)")

class MarginMarketSummary(MarginMarketSummaryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True