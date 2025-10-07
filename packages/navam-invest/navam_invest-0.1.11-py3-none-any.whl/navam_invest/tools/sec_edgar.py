"""SEC EDGAR API tools for corporate filings and regulatory data."""

from typing import Any, Dict, List, Optional

import httpx
from langchain_core.tools import tool


async def _fetch_sec(
    endpoint: str, headers: Optional[Dict[str, str]] = None, **params: Any
) -> Dict[str, Any] | List[Dict[str, Any]]:
    """Fetch data from SEC EDGAR API.

    Note: SEC requires User-Agent header with contact info.
    """
    default_headers = {
        "User-Agent": "navam-invest investment-advisor (contact@navam.io)",
        "Accept-Encoding": "gzip, deflate",
    }

    if headers:
        default_headers.update(headers)

    async with httpx.AsyncClient() as client:
        url = f"https://data.sec.gov/{endpoint}"
        response = await client.get(
            url, params=params, headers=default_headers, timeout=30.0
        )
        response.raise_for_status()
        return response.json()


@tool
async def get_company_filings(symbol: str, filing_type: str = "10-K", limit: int = 5) -> str:
    """Get recent SEC filings for a company.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
        filing_type: Type of filing (e.g., '10-K', '10-Q', '8-K', '13F')
        limit: Number of recent filings to return (default: 5)

    Returns:
        List of recent filings with dates and links
    """
    try:
        # First, get company CIK from ticker
        # Note: SEC doesn't have direct ticker lookup, would need mapping
        # For now, return instructive message
        return (
            f"**SEC Filings for {symbol}**\n\n"
            f"To access SEC EDGAR filings:\n"
            f"1. Visit: https://www.sec.gov/cgi-bin/browse-edgar\n"
            f"2. Search for company: {symbol}\n"
            f"3. Filter by form type: {filing_type}\n\n"
            f"*Note: Direct SEC API access requires CIK mapping.*\n"
            f"*Future versions will include automated filing retrieval.*"
        )
    except Exception as e:
        return f"Error fetching SEC filings for {symbol}: {str(e)}"


@tool
async def get_latest_10k(cik: str) -> str:
    """Get latest 10-K annual report for a company.

    Args:
        cik: Central Index Key (CIK) for the company

    Returns:
        Summary of latest 10-K filing
    """
    try:
        # Pad CIK to 10 digits
        cik_padded = cik.zfill(10)

        # Fetch company submissions
        data = await _fetch_sec(f"submissions/CIK{cik_padded}.json")

        if "filings" not in data or "recent" not in data["filings"]:
            return f"No filings found for CIK {cik}"

        recent = data["filings"]["recent"]

        # Find latest 10-K
        for i, form in enumerate(recent["form"]):
            if form == "10-K":
                filing_date = recent["filingDate"][i]
                accession = recent["accessionNumber"][i].replace("-", "")
                primary_doc = recent["primaryDocument"][i]

                filing_url = (
                    f"https://www.sec.gov/Archives/edgar/data/"
                    f"{cik}/{accession}/{primary_doc}"
                )

                return (
                    f"**Latest 10-K Filing**\n\n"
                    f"CIK: {cik}\n"
                    f"Filing Date: {filing_date}\n"
                    f"Accession Number: {recent['accessionNumber'][i]}\n"
                    f"Document: {primary_doc}\n\n"
                    f"**Link:** {filing_url}\n\n"
                    f"*Note: Full XBRL parsing will be added in future versions*"
                )

        return f"No 10-K filings found for CIK {cik}"
    except Exception as e:
        return f"Error fetching 10-K for CIK {cik}: {str(e)}"


@tool
async def get_latest_10q(cik: str) -> str:
    """Get latest 10-Q quarterly report for a company.

    Args:
        cik: Central Index Key (CIK) for the company

    Returns:
        Summary of latest 10-Q filing
    """
    try:
        # Pad CIK to 10 digits
        cik_padded = cik.zfill(10)

        # Fetch company submissions
        data = await _fetch_sec(f"submissions/CIK{cik_padded}.json")

        if "filings" not in data or "recent" not in data["filings"]:
            return f"No filings found for CIK {cik}"

        recent = data["filings"]["recent"]

        # Find latest 10-Q
        for i, form in enumerate(recent["form"]):
            if form == "10-Q":
                filing_date = recent["filingDate"][i]
                accession = recent["accessionNumber"][i].replace("-", "")
                primary_doc = recent["primaryDocument"][i]

                filing_url = (
                    f"https://www.sec.gov/Archives/edgar/data/"
                    f"{cik}/{accession}/{primary_doc}"
                )

                return (
                    f"**Latest 10-Q Filing**\n\n"
                    f"CIK: {cik}\n"
                    f"Filing Date: {filing_date}\n"
                    f"Accession Number: {recent['accessionNumber'][i]}\n"
                    f"Document: {primary_doc}\n\n"
                    f"**Link:** {filing_url}\n\n"
                    f"*Note: Full XBRL parsing will be added in future versions*"
                )

        return f"No 10-Q filings found for CIK {cik}"
    except Exception as e:
        return f"Error fetching 10-Q for CIK {cik}: {str(e)}"


@tool
async def search_company_by_ticker(ticker: str) -> str:
    """Search for company information by ticker symbol.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Company name, CIK, and filing information
    """
    try:
        # Fetch company tickers mapping
        data = await _fetch_sec("files/company_tickers.json")

        # Search for ticker
        ticker_upper = ticker.upper()

        for cik, info in data.items():
            if info.get("ticker", "").upper() == ticker_upper:
                return (
                    f"**Company Information**\n\n"
                    f"Ticker: {info.get('ticker')}\n"
                    f"Name: {info.get('title')}\n"
                    f"CIK: {info.get('cik_str')}\n\n"
                    f"*Use CIK {info.get('cik_str')} to fetch specific filings*"
                )

        return f"No company found with ticker {ticker}"
    except Exception as e:
        return f"Error searching for ticker {ticker}: {str(e)}"


@tool
async def get_institutional_holdings(cik: str) -> str:
    """Get 13F institutional holdings for an investment company.

    Args:
        cik: Central Index Key (CIK) for the institutional investor

    Returns:
        Summary of latest 13F holdings
    """
    try:
        # Pad CIK to 10 digits
        cik_padded = cik.zfill(10)

        # Fetch company submissions
        data = await _fetch_sec(f"submissions/CIK{cik_padded}.json")

        if "filings" not in data or "recent" not in data["filings"]:
            return f"No filings found for CIK {cik}"

        recent = data["filings"]["recent"]

        # Find latest 13F
        for i, form in enumerate(recent["form"]):
            if form == "13F-HR":
                filing_date = recent["filingDate"][i]
                accession = recent["accessionNumber"][i].replace("-", "")
                primary_doc = recent["primaryDocument"][i]

                filing_url = (
                    f"https://www.sec.gov/Archives/edgar/data/"
                    f"{cik}/{accession}/{primary_doc}"
                )

                return (
                    f"**Latest 13F Holdings Report**\n\n"
                    f"Institution CIK: {cik}\n"
                    f"Filing Date: {filing_date}\n"
                    f"Accession Number: {recent['accessionNumber'][i]}\n\n"
                    f"**Link:** {filing_url}\n\n"
                    f"*Note: Detailed holdings parsing will be added in future versions*"
                )

        return f"No 13F filings found for CIK {cik}"
    except Exception as e:
        return f"Error fetching 13F for CIK {cik}: {str(e)}"
