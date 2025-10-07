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
    get_finnhub_company_news,
    get_insider_sentiment,
    get_recommendation_trends,
    get_social_sentiment,
)

# Tiingo tools
from navam_invest.tools.tiingo import (
    get_fundamentals_daily,
    get_fundamentals_definitions,
    get_fundamentals_statements,
    get_historical_fundamentals,
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
    # Historical Fundamentals (Tiingo)
    "get_fundamentals_daily": get_fundamentals_daily,
    "get_fundamentals_statements": get_fundamentals_statements,
    "get_fundamentals_definitions": get_fundamentals_definitions,
    "get_historical_fundamentals": get_historical_fundamentals,
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
        category: One of 'market', 'fundamentals', 'macro', 'treasury', 'sec', 'news', 'sentiment', 'files'

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
            "get_fundamentals_daily",
            "get_fundamentals_statements",
            "get_fundamentals_definitions",
            "get_historical_fundamentals",
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


def get_tools_for_agent(agent_name: str) -> List[BaseTool]:
    """Get recommended tools for a specific agent.

    This function maps specialized agents to their optimal tool sets based on
    the agent refactoring plan. It ensures each agent has focused, relevant tools
    for their specialized tasks.

    Args:
        agent_name: One of 'quill', 'screen_forge', 'portfolio', 'research'

    Returns:
        List of tools recommended for the specified agent
    """
    agent_tool_map = {
        # Quill (Equity Research): Deep fundamental analysis, thesis building, valuation
        "quill": [
            # Market data for current pricing
            "get_stock_price",
            "get_stock_overview",
            # Fundamentals for analysis (excluding screening tool)
            "get_company_fundamentals",
            "get_financial_ratios",
            "get_insider_trades",
            "get_fundamentals_daily",
            "get_fundamentals_statements",
            "get_fundamentals_definitions",
            "get_historical_fundamentals",
            # SEC filings for deep-dive analysis
            "search_company_by_ticker",
            "get_company_filings",
            "get_latest_10k",
            "get_latest_10q",
            "get_institutional_holdings",
            # Company-specific news for thesis validation
            "get_company_news",
            "get_finnhub_company_news",
        ],
        # Screen Forge (Equity Screening): Systematic screening, idea generation
        "screen_forge": [
            # Market data for validation
            "get_stock_price",
            "get_stock_overview",
            # Screening and fundamentals
            "screen_stocks",
            "get_company_fundamentals",
            "get_financial_ratios",
            # Sentiment for conviction signals
            "get_company_news_sentiment",
            "get_social_sentiment",
            "get_insider_sentiment",
            "get_recommendation_trends",
        ],
        # Portfolio (Generalist - Legacy): Broad portfolio analysis
        "portfolio": [
            # Market data
            "get_stock_price",
            "get_stock_overview",
            # Fundamentals
            "get_company_fundamentals",
            "get_financial_ratios",
            "get_insider_trades",
            "screen_stocks",
            "get_fundamentals_daily",
            "get_fundamentals_statements",
            "get_historical_fundamentals",
            # Sentiment
            "get_company_news_sentiment",
            "get_social_sentiment",
            "get_insider_sentiment",
            "get_recommendation_trends",
            "get_finnhub_company_news",
            # SEC filings
            "search_company_by_ticker",
            "get_company_filings",
            "get_latest_10k",
            "get_latest_10q",
            "get_institutional_holdings",
            # News
            "search_market_news",
            "get_top_financial_headlines",
            "get_company_news",
            # Files
            "read_local_file",
            "list_local_files",
        ],
        # Research (Macro Analysis - Legacy): Top-down macro analysis
        "research": [
            # Macro indicators
            "get_economic_indicator",
            "get_key_macro_indicators",
            # Treasury data
            "get_treasury_yield_curve",
            "get_treasury_rate",
            "get_treasury_yield_spread",
            "get_debt_to_gdp",
            # Macro news
            "search_market_news",
            "get_top_financial_headlines",
            # Files
            "read_local_file",
            "list_local_files",
        ],
    }

    if agent_name not in agent_tool_map:
        return []

    return [TOOLS[name] for name in agent_tool_map[agent_name] if name in TOOLS]


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
    tiingo_key: str = "",
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
        tiingo_key: Tiingo API key
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

        # Tiingo tools
        elif tool_name in [
            "get_fundamentals_daily",
            "get_fundamentals_statements",
            "get_fundamentals_definitions",
            "get_historical_fundamentals",
        ]:
            if tiingo_key and callable_func:
                bound_func = _create_bound_wrapper(callable_func, tiingo_key)
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
    "get_tools_for_agent",
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
    # Tiingo
    "get_fundamentals_daily",
    "get_fundamentals_statements",
    "get_fundamentals_definitions",
    "get_historical_fundamentals",
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
