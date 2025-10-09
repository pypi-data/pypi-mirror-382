"""
数据中心通用schemas模块
"""
from .base import BaseResponse, PaginatedResponse, PaginationInfo
from .a_stock import AStock
from .hk_stock import HKStock
from .index_basic import IndexBasic
from .index_company import IndexCompany
from .margin_account import MarginAccount
from .margin_analysis import MarginAnalysis
from .margin_detail import MarginDetail
from .margin_summary import MarginMarketSummary
from .hs_industry import HSIndustry, HSIndustryCategory
from .sw_industry import SWIndustry
from .sw_industry_company import SWIndustryCompany

__all__ = [
    "BaseResponse",
    "PaginatedResponse",
    "PaginationInfo",
    "AStock",
    "HKStock",
    "IndexBasic",
    "IndexCompany",
    "MarginAccount",
    "MarginAnalysis",
    "MarginDetail",
    "MarginMarketSummary",
    "HSIndustry",
    "HSIndustryCategory",
    "SWIndustry",
    "SWIndustryCompany",
]