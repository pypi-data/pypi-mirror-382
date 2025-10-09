<div align="center">

# 🤖 Navam Invest

**AI-Powered Investment Advisor for Retail Investors**

[![PyPI version](https://badge.fury.io/py/navam-invest.svg)](https://badge.fury.io/py/navam-invest)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/badge/navam-invest)](https://pepy.tech/project/navam-invest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[Features](#-features) •
[Quick Start](#-quick-start) •
[Agents](#-specialized-ai-agents) •
[API Sources](#-data-sources) •
[Examples](#-example-interactions) •
[Documentation](#-documentation)

</div>

---

## 🆕 What's New in v0.1.27

**Earnings Whisperer Agent** - Specialized earnings analysis and trading opportunities:

- ✨ **New Agent**: Earnings Whisperer for earnings surprise analysis, post-earnings drift detection, and momentum tracking
- ✨ **14 Specialized Tools**: Earnings data (Yahoo), market analysis, analyst coverage, SEC 8-K filings, news
- ✨ **5-Step Framework**: History analysis, drift detection, analyst tracking, calendar monitoring, catalyst integration
- ✨ **TUI Command**: `/earnings` to switch to Earnings Whisperer agent
- ✨ **Pattern Recognition**: Consistent beaters, accelerating beats, drift opportunities, quality issues

**Analysis Capabilities**:
- **Earnings Momentum**: Identify stocks with 3+ consecutive quarters beating estimates
- **Post-Earnings Drift**: Detect underreaction opportunities (1-3 days after earnings)
- **Analyst Revisions**: Track estimate changes and rating upgrades post-earnings
- **Earnings Quality**: Flag revenue misses vs. EPS beats, non-recurring items
- **Trading Signals**: BUY (drift play), HOLD (wait), SELL (negative momentum)

**Previous Release**: [v0.1.26](backlog/release-0.1.26.md) - Yahoo Finance + Enhanced SEC EDGAR Integration

---

## 📖 Overview

`navam-invest` brings **institutional-grade portfolio intelligence** to individual retail investors. Built with [LangGraph](https://langchain-ai.github.io/langgraph/) and powered by [Anthropic's Claude](https://www.anthropic.com/claude), it provides **specialized AI agents** that collaborate through **multi-agent workflows** for equity research, systematic screening, macro analysis, and portfolio management—all accessible through an interactive terminal interface.

### Why Navam Invest?

- **🎯 Multi-Agent Workflows**: Coordinated agent collaboration for comprehensive analysis
- **🤖 Specialized Agents**: 7 purpose-built agents (Quill, Earnings Whisperer, Screen Forge, Macro Lens, Atlas, Portfolio, Research)
- **📊 Institutional Data**: Yahoo Finance + Enhanced EDGAR + 8 premium APIs (all free tiers)
- **🔒 Privacy-First**: Run locally with your own API keys—your data stays yours
- **💡 Transparent**: Full audit trails and explainable AI reasoning with real-time streaming
- **🆓 Zero Additional Cost**: Yahoo Finance + EDGAR tools require no API keys
- **🔧 Extensible**: Modular architecture makes it easy to add new agents and workflows

---

## ✨ Features

### 🤖 **Specialized AI Agents** (Powered by LangGraph)

<table>
<tr>
<td width="50%">

#### **Quill - Equity Research** ⭐ *Enhanced v0.1.26*
*Deep fundamental analysis & thesis building*

**NEW Capabilities**:
- ✨ Real-time earnings trends & surprises (Yahoo Finance)
- ✨ Analyst consensus & price targets (Yahoo Finance)
- ✨ Institutional ownership tracking (Yahoo Finance)
- ✨ Material event detection (8-K filings)
- ✨ XBRL structured data extraction
- ✨ Insider transaction patterns (Form 4)

**Core Capabilities**:
- Investment thesis development
- DCF & comparable company valuation
- 5-year historical fundamentals (Tiingo)
- Quarterly earnings tracking
- SEC filings analysis (10-K, 10-Q, 8-K)
- Company-specific news validation
- Dividend history & yield analysis
- **36 specialized tools** (up from 22)

**Command**: `/quill`

**Use Case**: "Analyze AAPL with focus on recent earnings trends and analyst sentiment"

</td>
<td width="50%">

#### **Screen Forge - Equity Screening**
*Systematic stock discovery & idea generation*

**Enhanced Capabilities** (v0.1.26):
- ✨ Earnings momentum screening (consistent beats)
- ✨ Analyst upgrade activity filtering

**Core Capabilities**:
- Multi-factor screening (value, growth, quality)
- Systematic candidate identification
- Weekly watchlist generation
- Factor-based ranking systems
- Sentiment validation (Finnhub + Yahoo)
- Integration with Quill for deep-dives
- **15 specialized tools** (up from 10)

**Command**: `/screen`

**Use Case**: "Screen for stocks with consistent earnings beats and analyst upgrades"

</td>
</tr>
<tr>
<td width="50%">

#### **Earnings Whisperer - Earnings Analyst** ⭐ *NEW v0.1.27*
*Earnings surprise analysis & post-earnings drift*

**Core Capabilities**:
- Historical earnings surprise tracking (4-8 quarters)
- Post-earnings drift detection (1-3 day momentum)
- Analyst estimate revision monitoring
- Earnings quality assessment (revenue vs. EPS beats)
- Upcoming earnings calendar with probability scoring
- Earnings momentum patterns (consistent beaters)
- Trading signals (BUY/HOLD/SELL on earnings)
- **14 specialized tools**

**Command**: `/earnings`

**Use Case**: "Analyze NVDA earnings history - is there a post-earnings drift opportunity?"

</td>
<td width="50%">

#### **Macro Lens - Market Strategist**
*Top-down macro analysis & regime identification*

**Enhanced Capabilities** (v0.1.26):
- ✨ Market indices tracking (S&P 500, Nasdaq, VIX)
- ✨ Historical index data for regime analysis

**Core Capabilities**:
- Economic cycle regime analysis (4 phases)
- Yield curve interpretation & recession signals
- Sector allocation guidance based on macro
- Factor recommendations (value/growth, size)
- Inflation, growth, employment tracking
- Fed policy and interest rate analysis
- **13 specialized tools** (up from 11)

**Command**: `/macro`

**Use Case**: "What's the current macro regime and which sectors should I overweight?"

</td>
<td width="50%">

#### **Atlas - Investment Strategist**
*Strategic asset allocation & portfolio construction*

**Core Capabilities**:
- Investment Policy Statement (IPS) development
- Strategic asset allocation frameworks
- Risk tolerance profiling (Conservative/Moderate/Aggressive)
- Macro-driven tactical tilts
- Rebalancing strategies (threshold, calendar, tax-aware)
- Portfolio construction guidance
- **12 specialized tools**

**Command**: `/atlas`

**Use Case**: "Create an IPS for moderate risk tolerance with $100k portfolio"

</td>
</tr>
<tr>
<td width="50%">

#### **Portfolio Analysis** (Legacy)
*Comprehensive portfolio tools*

- Real-time stock quotes & metrics
- Company fundamentals & financial ratios
- News & social sentiment analysis
- SEC filings & institutional holdings
- Multi-criteria stock screening
- Local file reading (CSV, JSON, Excel)
- **24 tools** (backward compatible)

**Command**: `/portfolio`

**Use Case**: "What's the current price and fundamentals of MSFT?"

</td>
<td width="50%">

#### **Market Research** (Legacy)
*Top-down macro analysis*

- Macroeconomic indicators (GDP, CPI, unemployment)
- Treasury yield curves & spreads
- Federal Reserve data (FRED)
- Economic regime detection
- Debt-to-GDP analysis
- Market news & sentiment
- **10 tools**

**Command**: `/research`

**Use Case**: "Show me the Treasury yield curve and economic indicators"

*Note: Will be phased out in favor of Macro Lens agent in v0.2.0*

</td>
</tr>
</table>

### 🔀 **Multi-Agent Workflows**

Coordinated agent collaboration combining specialized expertise:

#### **Investment Analysis Workflow**

**Sequential Orchestration**: Quill → Macro Lens → Synthesis

**How it works**:
1. **Quill** performs bottom-up fundamental analysis
   - Business overview & competitive position
   - Financial health (5-year trends)
   - Valuation (P/E, P/B, DCF fair value)
   - **NEW**: Earnings trends, analyst sentiment
   - Investment thesis with catalysts

2. **Macro Lens** validates timing with top-down analysis
   - Receives Quill's thesis via shared state
   - Assesses current macro regime
   - Evaluates sector positioning
   - Validates entry point timing
   - **NEW**: Market indices regime correlation

3. **Synthesis** combines both perspectives
   - Overall rating: BUY/HOLD/SELL
   - Confidence level: High/Medium/Low
   - Key reasoning from both agents
   - Risk warning & suggested action

**Command**: `/analyze <SYMBOL>`

**Example**:
```
/analyze AAPL

📊 Quill analyzing fundamentals...
  → get_quote: $227.45, P/E 36x, Market Cap $3.5T
  → get_earnings_history: Beat by $0.15 last 3 quarters
  → get_analyst_recommendations: 42 Buy, 8 Hold, 2 Sell
  → get_institutional_holders: BlackRock 6.8%, Vanguard 8.2%

🌍 Macro Lens validating timing...
  → get_market_indices: S&P 500 +12% YTD, VIX 14.2
  → get_treasury_yield_curve: 10Y-2Y inverted -0.54%

🎯 Final Recommendation: HOLD - Medium Confidence
Apple shows strong fundamentals (earnings beats, analyst
support) but late-cycle macro timing suggests cautious
positioning. Dollar-cost average on dips below $210.
```

### 📊 **Data Sources** (36 Tools Across 10+ APIs)

| Data Source | Tools | Purpose | Cost | New in v0.1.26 |
|-------------|-------|---------|------|----------------|
| **Yahoo Finance** 🆕 | 11 | Real-time quotes, earnings, analyst ratings, ownership | **FREE** | ✅ |
| **SEC EDGAR** 🔄 | 9 | Corporate filings (10-K, 10-Q, 8-K), XBRL, insider transactions | **FREE** | ✅ 4 new |
| **Financial Modeling Prep** | 4 | Financial statements, ratios, screening | 250 calls/day | |
| **Tiingo** | 4 | Historical fundamentals (5yr), quarterly data | 50 symbols/hr | |
| **Finnhub** | 5 | News/social/insider sentiment, analyst ratings | 60 calls/min | |
| **Alpha Vantage** | 2 | Stock prices, company overviews | 25-500 calls/day | |
| **FRED (St. Louis Fed)** | 2 | Economic indicators, macro data | Unlimited | |
| **U.S. Treasury** | 4 | Yield curves, treasury rates | Unlimited | |
| **NewsAPI.org** | 3 | Market news, headlines | 100 calls/day | |
| **Anthropic Claude** | - | AI reasoning (Sonnet 4.5) | Pay-as-you-go | |

**Total Free Data**: 7 out of 10 sources require no API key! (Yahoo Finance, SEC, Treasury)

### 💬 **Interactive Terminal UI**

- **Chat Interface**: Natural language interaction with specialized agents
- **Real-time Streaming**: Watch agents think and reason live
- **Multi-Agent Progress**: See workflow transitions and agent collaboration
- **Granular Tool Tracking**: Watch which tools are called with what arguments
- **Markdown Rendering**: Beautiful formatted output with tables
- **Agent Switching**: `/quill`, `/screen`, `/macro`, `/atlas`, `/portfolio`, `/research`
- **Workflow Commands**: `/analyze <SYMBOL>` for multi-agent analysis
- **Command Palette**: Quick access to common actions
- **File Reading**: Analyze local portfolio files

### 🏗️ **Built on Modern Tech**

```
LangGraph (Multi-Agent Orchestration) → LangChain (Tools) → Anthropic Claude (Reasoning)
     ↓
Textual (Terminal UI) + Typer (CLI) + httpx (Async HTTP) + yfinance (Market Data)
```

**Architecture Highlights**:
- **Multi-Agent Workflows**: Sequential orchestration with shared state
- **Specialized Agents**: Purpose-built agents with focused tool sets
- **Tools Registry**: Agent-specific tool mappings for optimal performance
- **ReAct Pattern**: Reasoning + Acting for transparent decision-making
- **Async/Await**: Non-blocking I/O for responsive UI
- **Type Safety**: Full type hints with MyPy strict mode

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** (3.13 recommended)
- **pip** package manager
- API keys (see [Configuration](#configuration))

### Installation

#### Option 1: Install from PyPI (Recommended)

```bash
pip install navam-invest
```

#### Option 2: Install from Source

```bash
git clone https://github.com/navam-io/navam-invest.git
cd navam-invest
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### Configuration

1. **Copy environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Add your API keys** to `.env`:
   ```bash
   # Required
   ANTHROPIC_API_KEY=sk-ant-...

   # Optional (but recommended for full functionality)
   ALPHA_VANTAGE_API_KEY=your_key_here
   FMP_API_KEY=your_key_here
   TIINGO_API_KEY=your_key_here
   FINNHUB_API_KEY=your_key_here
   FRED_API_KEY=your_key_here
   NEWSAPI_API_KEY=your_key_here

   # No keys needed for Yahoo Finance, SEC EDGAR, U.S. Treasury!
   ```

3. **Verify API Keys** (use `/api` command in chat to check status):
   ```bash
   navam invest
   > /api
   # Shows status table with ✅ working / ❌ failed / ⚪ not configured
   ```

4. **Get API Keys** (all have free tiers):

   | Service | Link | Free Tier | Required? |
   |---------|------|-----------|-----------|
   | **Anthropic** ⭐ | [console.anthropic.com](https://console.anthropic.com/) | Pay-as-you-go ($3-15/M tokens) | ✅ Required |
   | **Yahoo Finance** 🆕 | - | Unlimited, no key needed | ✅ Built-in |
   | **SEC EDGAR** | - | Unlimited, no key needed | ✅ Built-in |
   | **U.S. Treasury** | - | Unlimited, no key needed | ✅ Built-in |
   | **Alpha Vantage** | [alphavantage.co/support/#api-key](https://www.alphavantage.co/support/#api-key) | 25 calls/day | Optional |
   | **FMP** | [financialmodelingprep.com/developer](https://financialmodelingprep.com/developer) | 250 calls/day | Optional |
   | **Tiingo** | [tiingo.com](https://www.tiingo.com/) | 50 symbols/hr, 5yr history | Optional |
   | **Finnhub** | [finnhub.io/register](https://finnhub.io/register) | 60 calls/min | Optional |
   | **FRED** | [fredaccount.stlouisfed.org/apikeys](https://fredaccount.stlouisfed.org/apikeys) | Unlimited | Optional |
   | **NewsAPI.org** | [newsapi.org/register](https://newsapi.org/register) | 1,000 calls/day | Optional |

### Usage

#### Launch the Interactive Interface

```bash
navam invest
```

This opens an interactive chat interface with 7 specialized AI agents and multi-agent workflows.

#### Slash Commands

| Command | Description |
|---------|-------------|
| `/api` | Check API connectivity and status of all data providers |
| `/help` | Show all available commands |
| `/examples` | Show example prompts for current agent |
| `/clear` | Clear chat history |
| `/quit` | Exit the application |

#### Agent Selection Commands

| Command | Agent/Workflow | Description |
|---------|----------------|-------------|
| `/analyze <SYMBOL>` | Investment Analysis Workflow | Multi-agent fundamental + macro analysis |
| `/quill` | Quill (Equity Research) | Deep fundamental analysis & thesis building ⭐ *36 tools* |
| `/earnings` | Earnings Whisperer | Earnings surprise analysis & post-earnings drift ⭐ *NEW v0.1.27* |
| `/screen` | Screen Forge | Systematic stock screening & idea generation |
| `/macro` | Macro Lens | Top-down macro analysis & regime identification |
| `/atlas` | Atlas (Investment Strategist) | Strategic asset allocation & IPS development |
| `/portfolio` | Portfolio Analysis | Comprehensive stock & portfolio tools (legacy) |
| `/research` | Market Research | Macroeconomic analysis & treasury data (legacy) |
| `/examples` | - | Show example queries for current agent/workflow |
| `/help` | - | Show all commands |
| `/clear` | - | Clear chat history |
| `/quit` | - | Exit application |

---

## 💡 Example Interactions

### Quill - Equity Research (with Yahoo Finance) 🆕

<details>
<summary><b>📈 Earnings & Analyst Sentiment Analysis</b></summary>

```
You: /quill
You: Analyze AAPL with focus on recent earnings trends and analyst sentiment

Quill (Equity Research):
  → get_quote(symbol=AAPL)
  ✓ AAPL: $227.45, +1.2% (+$2.70), P/E 36x, Market Cap $3.5T

  → get_earnings_history(symbol=AAPL)
  ✓ Earnings history retrieved

  → get_analyst_recommendations(symbol=AAPL)
  ✓ Analyst ratings retrieved

  → get_institutional_holders(symbol=AAPL)
  ✓ Institutional ownership retrieved

**Apple Inc. (AAPL) - Earnings & Sentiment Analysis**

**Earnings Trends** (Last 4 Quarters):

| Quarter | EPS Actual | EPS Estimate | Surprise | Surprise % |
|---------|------------|--------------|----------|------------|
| Q4 2024 | $1.64 | $1.60 | $0.04 | +2.5% |
| Q3 2024 | $1.40 | $1.35 | $0.05 | +3.7% |
| Q2 2024 | $1.53 | $1.50 | $0.03 | +2.0% |
| Q1 2024 | $2.18 | $2.10 | $0.08 | +3.8% |

**Key Observation**: Apple has beaten analyst estimates for 4 consecutive
quarters with an average surprise of +3.0%. This demonstrates consistent
execution and conservative guidance from management.

**Upcoming Earnings**:
- **Date**: January 30, 2025 (estimated)
- **EPS Estimate**: $2.23 (range: $2.18 - $2.28)
- **Revenue Estimate**: $124.5B

**Analyst Sentiment**:

**Ratings Distribution** (52 analysts):
- **Buy/Overweight**: 42 (81%)
- **Hold/Neutral**: 8 (15%)
- **Sell/Underweight**: 2 (4%)

**Price Targets**:
- **Mean Target**: $248 (+9% upside)
- **Median Target**: $245 (+7.7% upside)
- **High Target**: $275 (+21% upside)
- **Low Target**: $180 (-21% downside)

**Recent Rating Changes** (Last 30 days):
- **Wedbush**: Maintained Outperform, raised target $260 → $275
- **Morgan Stanley**: Upgraded Neutral → Overweight, target $240 → $260
- **JPMorgan**: Maintained Overweight, raised target $245 → $265

**Institutional Ownership**:

**Top 5 Holders** (Total: 58.2% institutional ownership):
1. **Vanguard Group**: 8.2% ($287B) - Increased 2.1M shares Q3
2. **BlackRock**: 6.8% ($238B) - Increased 1.5M shares Q3
3. **Berkshire Hathaway**: 5.8% ($203B) - Maintained position
4. **State Street**: 4.1% ($144B) - Increased 850K shares Q3
5. **Fidelity**: 2.3% ($81B) - Decreased 300K shares Q3

**Sentiment Analysis**:

**Bullish Indicators**:
- ✅ 4 consecutive earnings beats (avg +3% surprise)
- ✅ 81% analyst buy ratings (strong consensus)
- ✅ Recent analyst upgrades (3 in last month)
- ✅ Institutional accumulation (+4.4M shares Q3 from top holders)
- ✅ Mean price target implies +9% upside

**Cautionary Signals**:
- ⚠️ High valuation (36x P/E vs. 28x 5-year avg)
- ⚠️ Fidelity reduced position (-300K shares)
- ⚠️ Wide price target range ($180-$275, $95 spread)

**Investment Recommendation**: **BUY on Dips**

Apple demonstrates strong fundamental momentum with consistent earnings
beats and positive analyst sentiment. However, current valuation (36x P/E)
is elevated. Recommend accumulating on any pullback to $210-215 range
(30-31x P/E) for better risk/reward.

**Upcoming Catalysts**:
1. **Q1 FY25 Earnings** (Jan 30, 2025) - iPhone 16 holiday sales reveal
2. **Vision Pro Expansion** (International launch scheduled Q1 2025)
3. **AI Features Rollout** (iOS 18.2+ with enhanced Siri capabilities)

**Risk Factors**:
- China demand softness (18% of revenue)
- DOJ antitrust case (App Store at risk)
- Valuation multiple compression if growth disappoints

**Data Sources**:
- Real-time quote: Yahoo Finance
- Earnings history: Yahoo Finance (4 quarters)
- Analyst ratings: Yahoo Finance (52 analysts)
- Institutional ownership: Yahoo Finance (13F filings)
```
</details>

### Multi-Agent Workflow: Investment Analysis

<details>
<summary><b>📊 Complete Investment Analysis (Fundamental + Macro)</b></summary>

```
You: /analyze MSFT

Investment Analysis Workflow: Starting multi-agent analysis...

📊 Quill analyzing fundamentals...
  → get_quote
  → get_financials
  → get_earnings_history
  → get_analyst_recommendations
  ✓ Fundamental analysis complete

🌍 Macro Lens validating timing...
  → get_key_macro_indicators
  → get_treasury_yield_curve
  → get_market_indices
  ✓ Macro validation complete

🎯 Synthesizing recommendation...

Final Recommendation:

**Overall Rating: BUY - Medium Confidence**

**Key Reasoning**:
Microsoft demonstrates exceptional fundamental quality with 42% ROE,
$87B annual free cash flow, and strong competitive moats in cloud
(Azure) and enterprise software. Recent earnings show consistent beats
(+4.2% avg surprise last 4 quarters) with 89% analyst buy ratings.
Current valuation of 31x P/E is reasonable given 15% revenue growth.

However, macro timing presents headwinds—we're in late expansion phase
with inverted yield curve (-0.54%) signaling recession risk within 12
months. Tech sector (Nasdaq -8% from highs) showing vulnerability.

**Suggested Action**:
Consider accumulating MSFT on dips rather than full position immediately.
Dollar-cost average over 3-6 months to capture potential volatility from
macro headwinds. Microsoft's defensive characteristics (enterprise
subscriptions, cloud infrastructure) should outperform cyclical tech
peers in downturn.

**Risk Warning**:
Monitor enterprise cloud spending trends and Microsoft Azure growth rates.
If Azure growth decelerates below 25% YoY, fundamental thesis weakens.
Macro risk: Recession could compress P/E multiple to 24-26x (historical
trough), implying 15-20% downside risk from current levels.

**Data Sources**:
- Fundamentals: Yahoo Finance (earnings, analysts, quotes), FMP (ratios)
- Macro: FRED (GDP, CPI, unemployment), U.S. Treasury (yield curve)
- Market: Yahoo Finance (indices), NewsAPI (sentiment)
```
</details>

### Screen Forge - Earnings Momentum Screening 🆕

<details>
<summary><b>🔍 Screen for Earnings Beat Momentum</b></summary>

```
You: /screen
You: Screen for stocks with consistent earnings beats over last 3 quarters

Screen Forge (Equity Screening):
  → screen_stocks(market_cap_min=1000000000)
  ✓ 347 stocks retrieved

  → get_earnings_history (batch for 347 stocks)
  ✓ Earnings data retrieved for 298 stocks

  → Filtering for 3+ consecutive beats
  ✓ 42 stocks match criteria

**Earnings Beat Momentum Screen Results**

**Criteria**:
- Market Cap: > $1B
- Earnings Beats: 3+ consecutive quarters
- Average Surprise: > 2%

**Top 10 Candidates** (Ranked by avg surprise %):

| Rank | Ticker | Company | Mkt Cap | Avg Surprise | Streak | Latest Beat |
|------|--------|---------|---------|--------------|--------|-------------|
| 1 | **NVDA** | NVIDIA | $3.2T | +18.4% | 8 qtrs | +21.2% |
| 2 | **META** | Meta Platforms | $1.4T | +12.6% | 5 qtrs | +15.8% |
| 3 | **GOOGL** | Alphabet | $2.1T | +8.9% | 6 qtrs | +9.4% |
| 4 | **MSFT** | Microsoft | $3.1T | +4.2% | 4 qtrs | +3.8% |
| 5 | **AAPL** | Apple | $3.5T | +3.0% | 4 qtrs | +2.5% |
| 6 | **AMZN** | Amazon | $1.9T | +7.5% | 5 qtrs | +8.2% |
| 7 | **V** | Visa | $592B | +5.1% | 7 qtrs | +4.8% |
| 8 | **MA** | Mastercard | $453B | +4.9% | 6 qtrs | +5.2% |
| 9 | **HD** | Home Depot | $381B | +3.8% | 4 qtrs | +4.1% |
| 10 | **CRM** | Salesforce | $308B | +6.2% | 5 qtrs | +7.8% |

**Sector Breakdown**:
- Technology: 28 stocks (67%)
- Financials: 6 stocks (14%)
- Consumer Discretionary: 5 stocks (12%)
- Healthcare: 3 stocks (7%)

**Key Insights**:

1. **Tech Dominance**: Technology sector shows strongest earnings momentum,
   driven by AI tailwinds (NVDA, META, GOOGL) and cloud growth (MSFT, AMZN).

2. **Consistency Matters**: Stocks with 5+ quarter streaks (NVDA, META, GOOGL,
   AMZN, V, MA) show stronger post-earnings drift (+2.1% avg vs. market).

3. **Valuation Check**: Despite earnings beats, many trade at premium multiples:
   - NVDA: 65x P/E (highest risk)
   - META: 28x P/E (reasonable)
   - GOOGL: 26x P/E (attractive)

**Recommended Next Steps**:

1. **Deep Dive Top 3** (use Quill):
   - GOOGL: Best risk/reward (26x P/E, 8.9% avg surprise, cloud recovery)
   - META: Strong momentum (12.6% surprise, AI monetization)
   - V: Defensive quality (5.1% surprise, recession resilient)

2. **Analyst Validation**:
   - Run `get_analyst_recommendations` for top candidates
   - Check for recent upgrades/downgrades

3. **Timing Check** (use Macro Lens):
   - Validate entry timing with current macro regime
   - Consider dollar-cost averaging if late-cycle concerns persist

**Use with Quill**:
Type `/quill` then "Analyze GOOGL with earnings momentum focus" for
deep-dive analysis on top value candidate.
```
</details>

---

## 📚 Documentation

### Project Resources

- **[Integration Docs](backlog/edgar-yahoo-integration.md)**: Yahoo Finance + EDGAR integration guide (NEW)
- **[Backlog](backlog/active.md)**: Current development roadmap
- **[Release Notes](backlog/)**: Detailed changelog for each version
- **[Architecture Specs](refer/specs/)**: Technical design documents
- **[LangGraph Guide](refer/langgraph/)**: Multi-agent patterns & best practices

### API Reference

- **[Anthropic Claude](https://docs.anthropic.com/)**: AI reasoning engine
- **[LangGraph](https://langchain-ai.github.io/langgraph/)**: Agent orchestration framework
- **[Yahoo Finance (yfinance)](https://github.com/ranaroussi/yfinance)**: Free market data library 🆕
- **[Alpha Vantage](https://www.alphavantage.co/documentation/)**: Stock market data
- **[FMP](https://site.financialmodelingprep.com/developer/docs)**: Financial statements & screening
- **[Tiingo](https://www.tiingo.com/documentation/)**: Historical fundamentals
- **[Finnhub](https://finnhub.io/docs/api)**: Alternative data & sentiment
- **[FRED](https://fred.stlouisfed.org/docs/api/fred/)**: Economic indicators
- **[SEC EDGAR](https://www.sec.gov/edgar/sec-api-documentation)**: Corporate filings 🔄 *Enhanced*

### Development

#### Running Tests

```bash
pytest                    # Run all tests
pytest -v                # Verbose output
pytest tests/test_*.py   # Specific test file
```

#### Code Quality

```bash
black src/ tests/        # Format code
ruff check src/ tests/   # Lint code
mypy src/                # Type check
```

#### Building from Source

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Build package
python -m build

# Check distribution
twine check dist/*
```

---

## 🗺️ Roadmap

### Current Release: v0.1.27
- ✅ Earnings Whisperer agent (earnings surprise analysis, post-earnings drift)
- ✅ 14 specialized earnings tools (Yahoo Finance + SEC + Finnhub)
- ✅ 5-step earnings analysis framework
- ✅ Pattern recognition (consistent beaters, drift opportunities)

### Recent: v0.1.26
- ✅ Yahoo Finance integration (11 tools, FREE)
- ✅ Enhanced SEC EDGAR (4 new tools: 8-K, company facts, insider transactions)
- ✅ Quill agent enhanced with earnings & analyst coverage
- ✅ Zero cost expansion ($2.4K-$10.8K/year savings)

### Next: v0.1.28-0.1.30
- [ ] News Sentry agent (leverages 8-K material events)
- [ ] Options analysis tools for Hedge Smith agent (Yahoo options chain)
- [ ] Enhanced multi-agent workflows (parallel execution)
- [ ] Caching layer (DuckDB) for API efficiency

### Future: v0.2.0+
- [ ] Portfolio tracking & performance attribution
- [ ] Backtesting engine for investment strategies
- [ ] Risk management workflows (VaR, stress testing)
- [ ] Web UI (in addition to TUI)
- [ ] Cloud deployment options

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Ways to Contribute**:
- 🐛 Report bugs via [GitHub Issues](https://github.com/navam-io/navam-invest/issues)
- 💡 Suggest features or improvements
- 📝 Improve documentation
- 🔧 Submit pull requests

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **[Anthropic](https://www.anthropic.com/)** - Claude AI reasoning engine
- **[LangChain](https://www.langchain.com/)** - Agent framework ecosystem
- **[Textual](https://textual.textualize.io/)** - Modern terminal UI framework
- **[yfinance](https://github.com/ranaroussi/yfinance)** - Free Yahoo Finance API wrapper 🆕
- **Data Providers** - Yahoo Finance, SEC, Treasury, Alpha Vantage, FMP, Tiingo, Finnhub, FRED, NewsAPI

---

<div align="center">

**Built with ❤️ for retail investors**

[⬆ Back to Top](#-navam-invest)

</div>
