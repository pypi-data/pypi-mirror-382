"""Unified tools registry for navam-invest agents."""

from functools import wraps
from typing import Dict, List

from langchain_core.tools import BaseTool, StructuredTool

# Alpha Vantage tools
from navam_invest.tools.alpha_vantage import get_stock_overview, get_stock_price

# File reading tools
from navam_invest.tools.file_reader import list_local_files, read_local_file

# FRED tools
from navam_invest.tools.fred import get_economic_indicator, get_key_macro_indicators

# NewsAPI tools
from navam_invest.tools.newsapi import (
    get_company_news,
    get_top_financial_headlines,
    search_market_news,
)

# Financial Modeling Prep tools
from navam_invest.tools.fmp import (
    get_company_fundamentals,
    get_financial_ratios,
    get_insider_trades,
    screen_stocks,
)

# Finnhub tools
from navam_invest.tools.finnhub import (
    get_company_news_sentiment,
    get_company_news as get_finnhub_company_news,
    get_insider_sentiment,
    get_recommendation_trends,
    get_social_sentiment,
)

# SEC EDGAR tools
from navam_invest.tools.sec_edgar import (
    get_company_filings,
    get_institutional_holdings,
    get_latest_10k,
    get_latest_10q,
    search_company_by_ticker,
)

# Treasury tools
from navam_invest.tools.treasury import (
    get_debt_to_gdp,
    get_treasury_rate,
    get_treasury_yield_curve,
    get_treasury_yield_spread,
)

# Unified tools registry
TOOLS: Dict[str, BaseTool] = {
    # Market Data (Alpha Vantage)
    "get_stock_price": get_stock_price,
    "get_stock_overview": get_stock_overview,
    # File Reading (Local Data)
    "read_local_file": read_local_file,
    "list_local_files": list_local_files,
    # Fundamentals (FMP)
    "get_company_fundamentals": get_company_fundamentals,
    "get_financial_ratios": get_financial_ratios,
    "get_insider_trades": get_insider_trades,
    "screen_stocks": screen_stocks,
    # Alternative Data & Sentiment (Finnhub)
    "get_company_news_sentiment": get_company_news_sentiment,
    "get_social_sentiment": get_social_sentiment,
    "get_insider_sentiment": get_insider_sentiment,
    "get_recommendation_trends": get_recommendation_trends,
    "get_finnhub_company_news": get_finnhub_company_news,
    # Macro Data (FRED)
    "get_economic_indicator": get_economic_indicator,
    "get_key_macro_indicators": get_key_macro_indicators,
    # News & Sentiment (NewsAPI)
    "search_market_news": search_market_news,
    "get_top_financial_headlines": get_top_financial_headlines,
    "get_company_news": get_company_news,
    # Treasury Data
    "get_treasury_yield_curve": get_treasury_yield_curve,
    "get_treasury_rate": get_treasury_rate,
    "get_treasury_yield_spread": get_treasury_yield_spread,
    "get_debt_to_gdp": get_debt_to_gdp,
    # SEC Filings
    "search_company_by_ticker": search_company_by_ticker,
    "get_company_filings": get_company_filings,
    "get_latest_10k": get_latest_10k,
    "get_latest_10q": get_latest_10q,
    "get_institutional_holdings": get_institutional_holdings,
}


def get_all_tools() -> List[BaseTool]:
    """Get list of all available tools."""
    return list(TOOLS.values())


def get_tools_by_category(category: str) -> List[BaseTool]:
    """Get tools filtered by category.

    Args:
        category: One of 'market', 'fundamentals', 'macro', 'treasury', 'sec'

    Returns:
        List of tools in the specified category
    """
    category_map = {
        "market": ["get_stock_price", "get_stock_overview"],
        "files": ["read_local_file", "list_local_files"],
        "fundamentals": [
            "get_company_fundamentals",
            "get_financial_ratios",
            "get_insider_trades",
            "screen_stocks",
        ],
        "sentiment": [
            "get_company_news_sentiment",
            "get_social_sentiment",
            "get_insider_sentiment",
            "get_recommendation_trends",
            "get_finnhub_company_news",
        ],
        "macro": ["get_economic_indicator", "get_key_macro_indicators"],
        "news": [
            "search_market_news",
            "get_top_financial_headlines",
            "get_company_news",
        ],
        "treasury": [
            "get_treasury_yield_curve",
            "get_treasury_rate",
            "get_treasury_yield_spread",
            "get_debt_to_gdp",
        ],
        "sec": [
            "search_company_by_ticker",
            "get_company_filings",
            "get_latest_10k",
            "get_latest_10q",
            "get_institutional_holdings",
        ],
    }

    if category not in category_map:
        return []

    return [TOOLS[name] for name in category_map[category] if name in TOOLS]


def _create_bound_wrapper(original_func, api_key: str):
    """Create a wrapper function that binds API key (proper closure)."""

    @wraps(original_func)
    async def wrapper(*args, **kwargs):
        # Remove api_key from kwargs if LLM passed it to avoid duplicate
        kwargs.pop('api_key', None)
        return await original_func(*args, api_key=api_key, **kwargs)

    return wrapper


def bind_api_keys_to_tools(
    tools: List[BaseTool],
    alpha_vantage_key: str = "",
    fmp_key: str = "",
    finnhub_key: str = "",
    fred_key: str = "",
    newsapi_key: str = "",
) -> List[BaseTool]:
    """Bind API keys to tools securely using wrapper functions.

    This removes the need to pass API keys through system prompts,
    improving security by keeping credentials out of LLM context.

    Args:
        tools: List of tools to bind API keys to
        alpha_vantage_key: Alpha Vantage API key
        fmp_key: Financial Modeling Prep API key
        finnhub_key: Finnhub API key
        fred_key: FRED API key
        newsapi_key: NewsAPI.org API key

    Returns:
        List of tools with API keys pre-bound
    """
    bound_tools = []

    for tool in tools:
        tool_name = tool.name

        # Get the actual callable (coroutine for async tools, func for sync)
        callable_func = tool.coroutine if tool.coroutine else tool.func

        # Alpha Vantage tools
        if tool_name in ["get_stock_price", "get_stock_overview"]:
            if alpha_vantage_key and callable_func:
                bound_func = _create_bound_wrapper(callable_func, alpha_vantage_key)
                bound_tool = StructuredTool.from_function(
                    coroutine=bound_func,
                    name=tool.name,
                    description=tool.description,
                )
                bound_tools.append(bound_tool)
            else:
                bound_tools.append(tool)  # Keep original if no key

        # FMP tools
        elif tool_name in [
            "get_company_fundamentals",
            "get_financial_ratios",
            "get_insider_trades",
            "screen_stocks",
        ]:
            if fmp_key and callable_func:
                bound_func = _create_bound_wrapper(callable_func, fmp_key)
                bound_tool = StructuredTool.from_function(
                    coroutine=bound_func,
                    name=tool.name,
                    description=tool.description,
                )
                bound_tools.append(bound_tool)
            else:
                bound_tools.append(tool)

        # Finnhub tools
        elif tool_name in [
            "get_company_news_sentiment",
            "get_social_sentiment",
            "get_insider_sentiment",
            "get_recommendation_trends",
            "get_finnhub_company_news",
        ]:
            if finnhub_key and callable_func:
                bound_func = _create_bound_wrapper(callable_func, finnhub_key)
                bound_tool = StructuredTool.from_function(
                    coroutine=bound_func,
                    name=tool.name,
                    description=tool.description,
                )
                bound_tools.append(bound_tool)
            else:
                bound_tools.append(tool)

        # FRED tools
        elif tool_name in ["get_economic_indicator", "get_key_macro_indicators"]:
            if fred_key and callable_func:
                bound_func = _create_bound_wrapper(callable_func, fred_key)
                bound_tool = StructuredTool.from_function(
                    coroutine=bound_func,
                    name=tool.name,
                    description=tool.description,
                )
                bound_tools.append(bound_tool)
            else:
                bound_tools.append(tool)

        # NewsAPI tools
        elif tool_name in [
            "search_market_news",
            "get_top_financial_headlines",
            "get_company_news",
        ]:
            if newsapi_key and callable_func:
                bound_func = _create_bound_wrapper(callable_func, newsapi_key)
                bound_tool = StructuredTool.from_function(
                    coroutine=bound_func,
                    name=tool.name,
                    description=tool.description,
                )
                bound_tools.append(bound_tool)
            else:
                bound_tools.append(tool)

        # Tools that don't need API keys (Treasury, SEC, Files)
        else:
            bound_tools.append(tool)

    return bound_tools


__all__ = [
    "TOOLS",
    "get_all_tools",
    "get_tools_by_category",
    "bind_api_keys_to_tools",
    # Alpha Vantage
    "get_stock_price",
    "get_stock_overview",
    # File Reading
    "read_local_file",
    "list_local_files",
    # FMP
    "get_company_fundamentals",
    "get_financial_ratios",
    "get_insider_trades",
    "screen_stocks",
    # Finnhub
    "get_company_news_sentiment",
    "get_social_sentiment",
    "get_insider_sentiment",
    "get_recommendation_trends",
    "get_finnhub_company_news",
    # FRED
    "get_economic_indicator",
    "get_key_macro_indicators",
    # NewsAPI
    "search_market_news",
    "get_top_financial_headlines",
    "get_company_news",
    # Treasury
    "get_treasury_yield_curve",
    "get_treasury_rate",
    "get_treasury_yield_spread",
    "get_debt_to_gdp",
    # SEC
    "search_company_by_ticker",
    "get_company_filings",
    "get_latest_10k",
    "get_latest_10q",
    "get_institutional_holdings",
]
