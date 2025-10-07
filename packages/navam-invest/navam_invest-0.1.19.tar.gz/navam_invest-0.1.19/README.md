<div align="center">

# 🤖 Navam Invest

**AI-Powered Investment Advisor for Retail Investors**

[![PyPI version](https://badge.fury.io/py/navam-invest.svg)](https://badge.fury.io/py/navam-invest)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/badge/navam-invest)](https://pepy.tech/project/navam-invest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](https://img.shields.io/badge/mypy-checked-blue)](http://mypy-lang.org/)

[Features](#-features) •
[Quick Start](#-quick-start) •
[Agents](#-specialized-ai-agents) •
[Workflows](#-multi-agent-workflows-new) •
[Examples](#-example-interactions) •
[Documentation](#-documentation)

</div>

---

## 🆕 What's New in v0.1.17

**Atlas - Investment Strategist** - Strategic asset allocation and portfolio construction:

- ✨ **Atlas Agent**: Investment strategist for strategic asset allocation, IPS development, and portfolio construction
- ✨ **Risk Tolerance Frameworks**: Conservative (30/60/10), Moderate (60/35/5), Aggressive (85/10/5) allocations
- ✨ **Macro-Driven Tactical Tilts**: Dynamic allocation adjustments based on economic cycle phase
- ✨ **Rebalancing Strategies**: Threshold-based, calendar-based, and tax-aware rebalancing guidance
- ✨ **Complete Phase 2B**: All specialized agents from refactoring plan now implemented

**Agent Count**: 5 → **6 specialized agents** (Quill, Screen Forge, Macro Lens, Atlas, Portfolio, Research)

See [Release Notes](backlog/release-0.1.17.md) for details | Previous: [v0.1.16 - Multi-Agent Workflows](backlog/release-0.1.16.md)

---

## 📖 Overview

`navam-invest` brings **institutional-grade portfolio intelligence** to individual retail investors. Built with [LangGraph](https://langchain-ai.github.io/langgraph/) and powered by [Anthropic's Claude](https://www.anthropic.com/claude), it provides **specialized AI agents** that collaborate through **multi-agent workflows** for equity research, systematic screening, macro analysis, portfolio management, and market research—all accessible through an interactive terminal interface.

### Why Navam Invest?

- **🎯 Multi-Agent Workflows**: Coordinated agent collaboration for comprehensive analysis (NEW in v0.1.16)
- **🤖 Specialized Agents**: Purpose-built agents for equity research, screening, macro strategy, portfolio analysis, and market research
- **🔒 Privacy-First**: Run locally with your own API keys—your data stays yours
- **💡 Transparent**: Full audit trails and explainable AI reasoning with real-time streaming
- **🆓 Free Data Sources**: Leverages high-quality public APIs (free tiers available)
- **🔧 Extensible**: Modular architecture makes it easy to add new agents and workflows

---

## ✨ Features

### 🔀 **Multi-Agent Workflows** (NEW in v0.1.16)

Coordinated agent collaboration that combines specialized expertise for comprehensive analysis:

<table>
<tr>
<td>

#### **Investment Analysis Workflow**

**Sequential Orchestration**: Quill → Macro Lens → Synthesis

**How it works**:
1. **Quill** performs bottom-up fundamental analysis
   - Business overview & competitive position
   - Financial health (5-year trends)
   - Valuation (P/E, P/B, DCF fair value)
   - Investment thesis with catalysts

2. **Macro Lens** validates timing with top-down macro analysis
   - Receives Quill's thesis via shared state
   - Assesses current macro regime
   - Evaluates sector positioning
   - Validates entry point timing

3. **Synthesis** combines both perspectives
   - Overall rating: BUY/HOLD/SELL
   - Confidence level: High/Medium/Low
   - Key reasoning from both agents
   - Risk warning & suggested action

**Command**: `/analyze <SYMBOL>`

**Example**:
```
/analyze AAPL

Investment Analysis Workflow: Starting...
📊 Quill analyzing fundamentals...
  → get_company_fundamentals
  → get_financial_ratios
  → get_dcf_valuation
🌍 Macro Lens validating timing...
  → get_treasury_yield_curve
  → get_key_macro_indicators
🎯 Synthesizing recommendation...

Final Recommendation:
BUY - High Confidence
Apple shows strong fundamentals (28% ROE,
$100B FCF) with reasonable valuation (24x P/E
vs 27x historical avg). Macro timing favorable
with defensive positioning in late-cycle regime.
```

**Benefits**:
- ✅ Combines fundamental + macro perspectives automatically
- ✅ Agents reference each other's analysis (shared state)
- ✅ Transparent multi-agent execution
- ✅ Institutional-grade analysis in seconds

</td>
</tr>
</table>

### 🤖 **Specialized AI Agents** (Powered by LangGraph)

<table>
<tr>
<td width="50%">

#### **Quill - Equity Research**
*Deep fundamental analysis & thesis building*

- Investment thesis development
- DCF & comparable company valuation
- 5-year historical fundamentals (Tiingo)
- Quarterly earnings tracking
- SEC filings analysis (10-K, 10-Q)
- Insider trading pattern analysis
- Company-specific news validation
- **16 specialized tools**

**Command**: `/quill`

**Use Case**: "Analyze AAPL and provide an investment thesis with fair value"

</td>
<td width="50%">

#### **Screen Forge - Equity Screening**
*Systematic stock discovery & idea generation*

- Multi-factor screening (value, growth, quality)
- Systematic candidate identification
- Weekly watchlist generation
- Factor-based ranking systems
- Sentiment validation (Finnhub)
- Integration with Quill for deep-dives
- **9 specialized tools**

**Command**: `/screen`

**Use Case**: "Screen for value stocks with P/E < 15 and market cap > $1B"

</td>
</tr>
<tr>
<td width="50%">

#### **Macro Lens - Market Strategist**
*Top-down macro analysis & regime identification*

- Economic cycle regime analysis (4 phases)
- Yield curve interpretation & recession signals
- Sector allocation guidance based on macro
- Factor recommendations (value/growth, size)
- Inflation, growth, employment tracking
- Fed policy and interest rate analysis
- **10 specialized tools**

**Command**: `/macro`

**Use Case**: "What's the current macro regime and which sectors should I overweight?"

</td>
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
</tr>
<tr>
<td colspan="2">

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

### 📊 **Real API Integrations** (27 Tools Across 8 Data Sources)

| API | Tools | Purpose | Free Tier |
|-----|-------|---------|-----------|
| **Alpha Vantage** | 2 | Stock prices, company overviews | 25-500 calls/day |
| **Financial Modeling Prep** | 4 | Financial statements, ratios, screening | 250 calls/day |
| **Tiingo** | 4 | Historical fundamentals (5yr), quarterly data | 50 symbols/hr |
| **Finnhub** | 5 | News/social/insider sentiment, analyst ratings | 60 calls/min |
| **FRED (St. Louis Fed)** | 2 | Economic indicators, macro data | Unlimited |
| **U.S. Treasury** | 4 | Yield curves, treasury rates | Unlimited |
| **SEC EDGAR** | 5 | Corporate filings (10-K, 10-Q, 13F) | 10 req/sec |
| **NewsAPI.org** | 3 | Market news, headlines | 100 calls/day |
| **Anthropic Claude** | - | AI reasoning (Sonnet 4.5) | Pay-as-you-go |

### 💬 **Interactive Terminal UI**

- **Chat Interface**: Natural language interaction with specialized agents
- **Real-time Streaming**: Watch agents think and reason live
- **Multi-Agent Progress**: See workflow transitions and agent collaboration
- **Granular Tool Tracking**: Watch which tools are called with what arguments
- **Markdown Rendering**: Beautiful formatted output with tables
- **Agent Switching**: `/quill`, `/screen`, `/macro`, `/portfolio`, `/research`
- **Workflow Commands**: `/analyze <SYMBOL>` for multi-agent analysis
- **Command Palette**: Quick access to common actions
- **File Reading**: Analyze local portfolio files

### 🏗️ **Built on Modern Tech**

```
LangGraph (Multi-Agent Orchestration) → LangChain (Tools) → Anthropic Claude (Reasoning)
     ↓
Textual (Terminal UI) + Typer (CLI) + httpx (Async HTTP)
```

**Architecture Highlights**:
- **Multi-Agent Workflows**: Sequential orchestration with shared state (NEW)
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
   ```

3. **Get API Keys** (all have free tiers):

   | Service | Link | Free Tier |
   |---------|------|-----------|
   | **Anthropic** ⭐ | [console.anthropic.com](https://console.anthropic.com/) | Pay-as-you-go ($3-15/M tokens) |
   | **Alpha Vantage** | [alphavantage.co/support/#api-key](https://www.alphavantage.co/support/#api-key) | 25 calls/day |
   | **FMP** | [financialmodelingprep.com/developer](https://financialmodelingprep.com/developer) | 250 calls/day |
   | **Tiingo** | [tiingo.com](https://www.tiingo.com/) | 50 symbols/hr, 5yr history |
   | **Finnhub** | [finnhub.io/register](https://finnhub.io/register) | 60 calls/min |
   | **FRED** | [fredaccount.stlouisfed.org/apikeys](https://fredaccount.stlouisfed.org/apikeys) | Unlimited |
   | **NewsAPI** | [newsapi.org/register](https://newsapi.org/register) | 100 calls/day |
   | **Treasury & SEC** | - | No keys required! |

### Usage

#### Launch the Interactive Interface

```bash
navam invest
```

This opens an interactive chat interface with 5 specialized AI agents and multi-agent workflows.

#### Quick Command Reference

| Command | Agent/Workflow | Description |
|---------|----------------|-------------|
| `/analyze <SYMBOL>` 🆕 | Investment Analysis Workflow | Multi-agent fundamental + macro analysis |
| `/quill` | Quill (Equity Research) | Deep fundamental analysis & thesis building |
| `/screen` | Screen Forge | Systematic stock screening & idea generation |
| `/macro` | Macro Lens | Top-down macro analysis & regime identification |
| `/portfolio` | Portfolio Analysis | Comprehensive stock & portfolio tools |
| `/research` | Market Research | Macroeconomic analysis & treasury data (legacy) |
| `/examples` | - | Show example queries for current agent/workflow |
| `/help` | - | Show all commands |
| `/clear` | - | Clear chat history |
| `/quit` | - | Exit application |

---

## 💡 Example Interactions

### Multi-Agent Workflow: Investment Analysis 🆕

<details>
<summary><b>📊 Complete Investment Analysis (Fundamental + Macro)</b></summary>

```
You: /analyze MSFT

Investment Analysis Workflow: Starting multi-agent analysis...

📊 Quill analyzing fundamentals...
  → get_company_fundamentals
  → get_financial_ratios
  → get_historical_fundamentals
  → get_dcf_valuation
  ✓ Fundamental analysis complete

🌍 Macro Lens validating timing...
  → get_key_macro_indicators
  → get_treasury_yield_curve
  → search_market_news
  ✓ Macro validation complete

🎯 Synthesizing recommendation...

Final Recommendation:

**Overall Rating: BUY - Medium Confidence**

**Key Reasoning**:
Microsoft demonstrates exceptional fundamental quality with 42% ROE,
$87B annual free cash flow, and strong competitive moats in cloud
(Azure) and enterprise software. Current valuation of 31x P/E is
reasonable given 15% revenue growth and expanding margins. However,
macro timing presents headwinds—we're in late expansion phase with
inverted yield curve signaling recession risk within 12 months. Tech
sector typically underperforms in early recession as enterprise IT
spending contracts.

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
- Fundamentals: Tiingo (5-year history), FMP (financial ratios)
- Macro: FRED (GDP, CPI, unemployment), U.S. Treasury (yield curve)
- Valuation: DCF model with 10% WACC, 3% terminal growth

---

**Quill's Fundamental Analysis** (Bottom-Up):

**Business Quality: Excellent**
- Market leader in cloud infrastructure (Azure: #2 globally, 23% market share)
- Dominant enterprise software franchise (Office 365, Windows, LinkedIn)
- Emerging AI leadership (OpenAI partnership, Copilot integration)
- Exceptional competitive moats: switching costs, network effects, scale

**Financial Health** (5-Year Trends):
- Revenue Growth: 14% CAGR (FY19-FY24) → Consistent, accelerating
- Operating Margin: 37% → 43% (600bps expansion) → World-class
- Free Cash Flow: $52B → $87B (+68%) → Capital allocation strength
- ROE: 38% → 42% → Best-in-class capital efficiency
- Debt-to-Equity: 0.34 → Conservative, AA+ credit rating

**Valuation Assessment**:
- Current P/E: 31x (vs. 5-year avg: 28x) → Slight premium
- P/FCF: 28x → Reasonable given quality and growth
- DCF Fair Value: $425 (current: $410) → **3.7% upside**
- Price-to-Sales: 12x → Premium to peers, justified by margins

**Investment Thesis**:
Microsoft is a **quality growth compounder** with secular tailwinds in
cloud and AI. The business demonstrates pricing power, margin expansion,
and capital-light growth. At current valuation, shares are fairly valued
with modest upside to DCF fair value.

**Bull Case** (Upside to $480, +17%):
- Azure accelerates to 30%+ growth (AI workloads)
- Copilot drives $10B+ incremental revenue by FY26
- Operating margin expands to 45% (cloud scale economics)
- Multiple re-rates to 35x on AI leadership

**Bear Case** (Downside to $320, -22%):
- Recession reduces enterprise IT spending
- Azure growth decelerates to sub-20% (competitive pressure)
- AI monetization disappoints (adoption lag)
- Multiple compresses to 24x (historical trough)

**Catalysts** (Next 12 months):
- ✅ Q1 FY25 earnings (Oct 2024): Azure growth trajectory
- ✅ Copilot adoption metrics (Dec 2024): AI revenue inflection
- ✅ OpenAI GPT-5 release (2025): Technology leadership
- ⚠️ Macro slowdown: Defensive cloud spending holds up better

**Recommendation**: BUY on dips below $390 (26x P/E, 8% discount to fair value)

---

**Macro Lens's Timing Validation** (Top-Down):

**Current Macro Regime: Late Expansion (Peak Phase)**

**Supporting Macro Data**:
- GDP Growth: 2.4% (Q3 2024) → Slowing trend
- Unemployment: 3.9% → Near cycle lows
- CPI Inflation: 3.2% YoY → Sticky above target
- Fed Funds Rate: 5.25-5.50% → Restrictive territory
- 10Y-2Y Yield Spread: **-0.54% (INVERTED)** → Recession warning
- Inversion Duration: 16 months → In danger zone (12-18mo lead time)

**Sector Positioning**:
Technology sector in late expansion phase shows:
- ❌ **Underperform in early recession** (cyclical earnings)
- ⚠️ **Valuation vulnerability** (P/E compression risk)
- ✅ **Microsoft = Defensive tech** (enterprise subscriptions, sticky revenue)

**Timing Assessment**:

**Macro Headwinds**:
1. **Inverted Yield Curve**: 16 months into inversion suggests recession
   risk elevated for H1 2025. Tech multiples typically compress 20-30%
   in recession.
2. **Late Cycle Dynamics**: Corporate IT spending growth decelerates in
   late expansion as CFOs turn cautious.
3. **Valuation Risk**: Tech sector trading at 27x P/E (vs. 15x S&P 500)
   leaves room for multiple compression.

**Macro Tailwinds**:
1. **Defensive Characteristics**: Microsoft's enterprise subscription
   model (90%+ recurring revenue) more resilient than cyclical tech.
2. **Cloud Infrastructure**: Mission-critical workloads (Azure, Office 365)
   see lower churn in recession vs. discretionary tech spending.
3. **Fed Rate Cuts**: If Fed pivots in 2025, growth stocks benefit from
   lower discount rates (duration play).

**Recommendation**: ⚠️ **Proceed with Caution - Dollar-Cost Average**

Fundamentals are excellent, but macro timing is challenging. Given inverted
yield curve and late-cycle positioning, recommend building position gradually
over 3-6 months rather than full commitment today. If recession materializes,
expect 15-20% drawdown opportunity to add at better valuations.

**Macro Risks to Monitor**:
- Yield curve steepening (recession trigger within 3-6 months)
- Enterprise software spending indicators (Salesforce, ServiceNow guidance)
- Azure growth deceleration below 25% (cyclical headwind confirmation)
- Credit spread widening (corporate stress)

**Ideal Entry**: Wait for macro capitulation (10-15% market correction) or
accumulate on any dip below $380 (24x P/E, 30% margin of safety vs. fair value).
```
</details>

<details>
<summary><b>🎯 Quick Analysis with Confidence Levels</b></summary>

```
You: /analyze NVDA

Investment Analysis Workflow: Starting multi-agent analysis...
📊 Quill analyzing fundamentals...
🌍 Macro Lens validating timing...
🎯 Synthesizing recommendation...

Final Recommendation:

**Overall Rating: HOLD - Low Confidence**

**Key Reasoning**:
NVIDIA shows exceptional fundamental strength (AI leadership, 100%+ revenue
growth, 75% gross margins) but faces extreme valuation risk (65x P/E,
40x FY25E) and unfavorable macro timing. Late-cycle regime with recession
risk makes high-multiple growth stocks vulnerable to 30-50% drawdowns.
Wait for better entry point.

**Suggested Action**:
Current holders: Trim position, take profits. New buyers: Wait for correction
to $90-100 range (40-45x FY25E) before initiating. Consider stop-loss at $110
(-15%) to protect against macro-driven selloff.

**Risk Warning**:
AI hype cycle could deflate quickly if enterprise AI spending disappoints.
Recession would trigger P/E de-rating from 65x to 35-40x (historical growth
stock trough), implying 40-50% downside risk. Monitor data center capex
trends from hyperscalers (Microsoft, Google, Amazon).
```
</details>

### Macro Lens - Market Strategist Agent

<details>
<summary><b>🌍 Economic Regime Analysis & Sector Guidance</b></summary>

```
You: /macro
You: What's the current macro regime? Are we in expansion, peak, or recession?

Macro Lens (Market Strategist):
  → Calling get_key_macro_indicators()
  ✓ get_key_macro_indicators completed
  → Calling get_treasury_yield_curve()
  ✓ get_treasury_yield_curve completed
  → Calling get_economic_indicator(series_id=UNRATE)
  ✓ get_economic_indicator completed

**Current Macro Regime Assessment**

**Regime: Late Expansion (Peak Phase)**

**Supporting Indicators**:
- **GDP Growth**: 2.4% (Q3 2024) - Slowing from 3.2% in Q2, below trend
- **Unemployment**: 3.9% - Near multi-decade lows, tight labor market
- **Inflation (CPI)**: 3.2% YoY - Above Fed target, persistent services inflation
- **Fed Funds Rate**: 5.25-5.50% - Restrictive territory, likely at terminal rate
- **Yield Curve**: **Inverted** (10Y-2Y spread: -0.54%)
  - Classic recession warning signal
  - Historically precedes recession by 12-18 months
  - Currently 16 months into inversion

**Yield Curve Interpretation**:
The inverted yield curve (short rates > long rates) indicates market expectations
of Fed rate cuts due to economic slowdown. This is a highly reliable recession
indicator with a 12-18 month lead time. We're now 16 months into the inversion,
suggesting recession risk elevated for H1 2025.

**Sector Allocation Guidance**:

**Overweight** (Late Cycle/Defensive):
- ✅ **Energy** - Persistent inflation, geopolitical premium, strong FCF
- ✅ **Healthcare** - Defensive earnings, demographic tailwinds, low cyclicality
- ✅ **Utilities** - Recession hedge, stable dividends, rate cut beneficiary
- ✅ **Consumer Staples** - Defensive spending, pricing power intact

**Underweight** (Cyclical/Growth):
- ❌ **Technology** - Valuation risk, vulnerable to earnings downgrades
- ❌ **Consumer Discretionary** - Weakening consumer, high debt levels
- ❌ **Financials** - Credit cycle turning, recession = loan losses

**Factor Recommendations**:

**Favor**:
- **Quality** (high ROE, low debt) - Resilience in downturn
- **Low Volatility** - Defensive positioning
- **Value** - Lower downside in bear market, reasonable valuations
- **Large Cap** - Flight to safety in risk-off environment

**Avoid**:
- **Growth** - High valuations vulnerable to multiple compression
- **Small Cap** - Liquidity risk, credit stress, recession sensitivity
- **High Beta** - Amplified drawdowns in market sell-off

**Key Risks to Monitor** (Next 6 Months):

1. **Recession Timing**: Yield curve un-inversion often marks recession start
2. **Fed Policy Error**: Holding rates too high = hard landing risk
3. **Credit Stress**: Corporate debt refinancing at higher rates
4. **Consumer Weakness**: Excess savings depleted, student loan restart
5. **Geopolitical Shocks**: Oil supply disruptions, trade tensions

**Investment Strategy Summary**:
Position defensively with quality, low-volatility stocks in healthcare, utilities,
and staples. Reduce cyclical and growth exposure. Build cash for opportunities
when recession arrives. Consider long-duration bonds (10Y+ treasuries) as
Fed cuts rates in 2025.
```
</details>

### Quill - Equity Research Agent

<details>
<summary><b>📈 Investment Thesis with DCF Valuation</b></summary>

```
You: /quill
You: Analyze AAPL and provide an investment thesis with fair value

Quill (Equity Research):
  → Calling get_company_fundamentals(symbol=AAPL)
  ✓ get_company_fundamentals completed
  → Calling get_financial_ratios(symbol=AAPL)
  ✓ get_financial_ratios completed
  → Calling get_historical_fundamentals(symbol=AAPL, years=5)
  ✓ get_historical_fundamentals completed
  → Calling get_dcf_valuation(symbol=AAPL)
  ✓ get_dcf_valuation completed

**Investment Thesis: Apple Inc. (AAPL)**

**Business Overview**:
Apple is the world's most valuable technology company ($3.5T market cap),
operating a vertically integrated ecosystem spanning hardware (iPhone, Mac,
iPad), services (App Store, iCloud, Apple Music), and wearables (Apple Watch,
AirPods). The company's competitive moats include brand loyalty, ecosystem
lock-in, and premium positioning.

**Financial Health** (5-Year Analysis):

**Revenue Trends**:
- FY19: $260B → FY24: $383B (8% CAGR)
- iPhone: 52% of revenue (stable), Services: 22% (growing 16% YoY)
- Geographic: Americas 42%, Greater China 19%, Europe 24%

**Profitability**:
- Gross Margin: 38% → 46% (800bps expansion) - Industry-leading
- Operating Margin: 24% → 30% - Best-in-class for hardware
- Net Margin: 21% → 26% - Exceptional cash generation
- ROE: 49% → 147% (buybacks amplifying returns)

**Cash Flow**:
- Operating Cash Flow: $69B → $118B (+71%)
- Free Cash Flow: $58B → $100B - Massive capital return capacity
- FCF Margin: 22% → 26% - Among highest in mega-cap tech

**Balance Sheet**:
- Net Cash: $62B (vs. $137B gross cash, $75B debt)
- Debt-to-Equity: 1.8 → Manageable, used for buybacks
- Current Ratio: 0.88 → Efficient working capital management

**Valuation Assessment**:

**Current Metrics**:
- Price: $227 (as of analysis)
- P/E Ratio: 36x (TTM), 30x (FY25E)
- P/FCF: 27x - Premium valuation
- EV/EBITDA: 26x
- PEG Ratio: 3.0 (high for 10% growth)

**DCF Fair Value Calculation**:
- WACC: 9.5% (equity: 8%, debt: 3%, tax: 15%)
- Terminal Growth: 3% (GDP-like perpetuity)
- 5-Year FCF Forecast: $100B → $130B (5% CAGR)
- **Intrinsic Value: $210 per share**
- **Current Price: $227 → 8% overvalued**

**Investment Thesis**:

**Bull Case** (Price Target: $260, +15%):
- Services revenue inflection (Apple Vision Pro, subscriptions)
- iPhone upgrade supercycle (AI features, 5-year replacement)
- Gross margin expansion to 48% (services mix shift)
- $110B+ annual buybacks (6% yield at current price)
- Multiple sustains at 32-35x on quality premium

**Base Case** (Fair Value: $210, -7.5%):
- iPhone growth slows to 2-3% (market saturation)
- Services grow 12-15% (Apple One bundles)
- Margins stable at 45-46% (mix shift offsets inflation)
- FCF grows 6% annually (buybacks continue)
- P/E de-rates to 28x (normalized growth stock multiple)

**Bear Case** (Downside: $180, -21%):
- iPhone replacement cycle extends to 4+ years (saturation)
- China regulatory/competitive risks (Huawei resurgence)
- Services growth decelerates to sub-10% (market maturity)
- Margin compression from product mix shift to India (lower ASP)
- P/E compresses to 24x (market de-rating of mega-cap tech)

**Key Catalysts** (Next 12 months):
- ✅ iPhone 16 cycle with AI features (Sep 2024)
- ✅ Vision Pro international launch (2025)
- ✅ India manufacturing scale-up (supply chain diversification)
- ⚠️ China economic slowdown (18% of revenue at risk)
- ⚠️ DOJ antitrust case (App Store at risk)

**Recommendation**: **HOLD**

Apple is a world-class business with exceptional cash generation and capital
allocation, but current valuation (36x P/E, 8% premium to DCF fair value)
offers limited margin of safety. Recommend accumulating on dips to $200-210
range (28-30x P/E). Current holders: Trim on rallies above $240.

**Confidence**: Medium (85% of companies analyzed)

**Data Sources**:
- Fundamentals: Tiingo (5-year history), FMP (ratios)
- Valuation: Custom DCF model, consensus estimates
```
</details>

### Screen Forge - Equity Screening Agent

<details>
<summary><b>🔍 Multi-Factor Stock Screening</b></summary>

```
You: /screen
You: Screen for value stocks with P/E under 15, P/B under 2, and market cap over $1B

Screen Forge (Equity Screening):
  → Calling screen_stocks(pe_ratio_max=15, price_to_book_max=2, market_cap_min=1000000000)
  ✓ screen_stocks completed
  → Calling get_financial_ratios (batch for top 10 matches)
  ✓ get_financial_ratios completed

**Value Stock Screening Results**

**Criteria**:
- P/E Ratio: < 15x (vs. S&P 500: 22x)
- Price-to-Book: < 2x (vs. S&P 500: 4.5x)
- Market Cap: > $1B (mid-cap+)

**Matches Found**: 47 stocks

**Top 10 Ranked by Quality Score** (ROE × FCF Yield):

| Rank | Ticker | Company | P/E | P/B | Mkt Cap | ROE | FCF Yield | Quality Score |
|------|--------|---------|-----|-----|---------|-----|-----------|---------------|
| 1 | **BAC** | Bank of America | 11.2 | 1.1 | $285B | 9.8% | 8.2% | 80.4 |
| 2 | **WFC** | Wells Fargo | 10.5 | 1.3 | $182B | 11.2% | 7.1% | 79.5 |
| 3 | **INTC** | Intel | 13.8 | 1.4 | $165B | 8.9% | 6.8% | 60.5 |
| 4 | **F** | Ford Motor | 6.2 | 0.9 | $52B | 15.3% | 9.4% | 143.8 |
| 5 | **GM** | General Motors | 5.8 | 1.0 | $51B | 18.2% | 11.2% | 203.8 |
| 6 | **T** | AT&T | 8.9 | 1.5 | $135B | 7.2% | 8.9% | 64.1 |
| 7 | **VZ** | Verizon | 9.1 | 1.8 | $182B | 6.8% | 7.5% | 51.0 |
| 8 | **PFE** | Pfizer | 11.4 | 1.6 | $163B | 5.4% | 6.2% | 33.5 |
| 9 | **CVX** | Chevron | 12.5 | 1.7 | $295B | 13.8% | 5.8% | 80.0 |
| 10 | **XOM** | Exxon Mobil | 13.2 | 1.9 | $445B | 16.4% | 6.1% | 100.0 |

**Sector Breakdown**:
- Financials: 15 stocks (banks, insurance)
- Energy: 8 stocks (oil & gas)
- Industrials: 9 stocks (manufacturing)
- Utilities: 7 stocks (power, telecom)
- Consumer: 5 stocks (retail, autos)
- Technology: 3 stocks (semiconductors, legacy tech)

**Key Observations**:

1. **Value Concentration in Cyclicals**:
   - Banks (BAC, WFC): Trading below book value, elevated credit risk priced in
   - Autos (F, GM): Highest quality scores but cyclical earnings risk
   - Energy (CVX, XOM): High FCF yield, commodity price exposure

2. **Valuation Drivers**:
   - Financial sector: Credit cycle concerns, recession fears
   - Energy: Oil price volatility, energy transition uncertainty
   - Telecom: Mature markets, high debt loads

3. **Risk Factors**:
   - ⚠️ **Cyclical Exposure**: 34 of 47 stocks (72%) are cyclical sectors
   - ⚠️ **Value Trap Risk**: Low multiples may reflect structural headwinds
   - ⚠️ **Recession Timing**: Value stocks typically lag in late expansion

**Recommended Next Steps**:

1. **Deep Dive Candidates** (for Quill analysis):
   - **GM**: Highest quality score, EV transition optionality
   - **BAC**: Strong deposit franchise, Fed rate cut beneficiary
   - **CVX**: Energy discipline, $75B buyback, 4% dividend yield

2. **Sentiment Check** (Finnhub validation):
   - Run `get_social_sentiment` for top 5 candidates
   - Validate with `get_recommendation_trends` (analyst consensus)

3. **Portfolio Construction**:
   - Diversify across 8-10 stocks (avoid sector concentration)
   - Favor quality within value (ROE > 12%, FCF Yield > 6%)
   - Monitor macro regime (value outperforms in early recession)

**Use with Quill**:
Type `/quill` then "Analyze GM and provide investment thesis" for deep-dive
fundamental analysis on top candidate.
```
</details>

---

## 🏗️ Architecture

### Multi-Agent Workflow System

```
User Command: /analyze AAPL
    ↓
┌─────────────────────────────────────────────────────────┐
│  Investment Analysis Workflow (LangGraph StateGraph)    │
│                                                          │
│  Shared State:                                          │
│    - messages: [user query, agent responses]           │
│    - symbol: "AAPL"                                     │
│    - quill_analysis: (populated by Quill)              │
│    - macro_context: (populated by Macro Lens)          │
└─────────────────────────────────────────────────────────┘
    ↓
┌──────────────┐
│  Node 1:     │   Bottom-Up Fundamental Analysis
│  Quill Agent │ → 16 tools (FMP, Tiingo, SEC, Finnhub)
└──────────────┘   Results stored in quill_analysis
    ↓
┌──────────────────┐
│  Node 2:         │   Top-Down Macro Validation
│  Macro Lens      │ → 10 tools (FRED, Treasury, NewsAPI)
└──────────────────┘   Reads quill_analysis from shared state
    ↓
┌──────────────────┐
│  Node 3:         │   Combines Both Perspectives
│  Synthesize      │ → Overall rating: BUY/HOLD/SELL
└──────────────────┘   Confidence: High/Medium/Low
    ↓
Final Recommendation (Markdown formatted)
```

### Agent Architecture

Each specialized agent is built with:
- **LangGraph ReAct Pattern**: Reasoning → Tool Selection → Action → Observation loop
- **Focused Tool Set**: Only tools relevant to agent's specialty (prevents tool overload)
- **Streaming**: Real-time progress updates to TUI
- **Type Safety**: Pydantic models for all tool inputs/outputs

### Tools Registry

```python
agent_tool_map = {
    "quill": [
        # Fundamentals (8 tools)
        "get_company_fundamentals", "get_financial_ratios",
        "get_historical_fundamentals", "get_dcf_valuation",
        # Filings (3 tools)
        "get_sec_filings", "get_latest_10k", "get_latest_10q",
        # Sentiment (5 tools)
        "get_insider_sentiment", "get_recommendation_trends",
        "search_company_news", "get_company_news", "get_social_sentiment"
    ],  # 16 tools

    "macro_lens": [
        # Macro indicators (2 tools)
        "get_economic_indicator", "get_key_macro_indicators",
        # Treasury (4 tools)
        "get_treasury_yield_curve", "get_treasury_rate",
        "get_treasury_yield_spread", "get_debt_to_gdp",
        # News (2 tools)
        "search_market_news", "get_top_financial_headlines",
        # Files (2 tools)
        "read_local_file", "list_local_files"
    ],  # 10 tools

    "screen_forge": [
        # Screening (4 tools)
        "screen_stocks", "get_company_fundamentals",
        "get_financial_ratios", "batch_financial_ratios",
        # Sentiment validation (5 tools)
        "get_social_sentiment", "get_recommendation_trends",
        "get_insider_sentiment", "get_company_news_sentiment",
        "search_company_news"
    ],  # 9 tools
}
```

---

## 📚 Documentation

### Project Resources

- **[Backlog](backlog/active.md)**: Current development roadmap
- **[Release Notes](backlog/)**: Detailed changelog for each version
- **[Architecture Specs](refer/specs/)**: Technical design documents
- **[LangGraph Guide](refer/langgraph/)**: Multi-agent patterns & best practices

### API Reference

- **[Anthropic Claude](https://docs.anthropic.com/)**: AI reasoning engine
- **[LangGraph](https://langchain-ai.github.io/langgraph/)**: Agent orchestration framework
- **[Alpha Vantage](https://www.alphavantage.co/documentation/)**: Stock market data
- **[FMP](https://site.financialmodelingprep.com/developer/docs)**: Financial statements & screening
- **[Tiingo](https://www.tiingo.com/documentation/)**: Historical fundamentals
- **[Finnhub](https://finnhub.io/docs/api)**: Alternative data & sentiment
- **[FRED](https://fred.stlouisfed.org/docs/api/fred/)**: Economic indicators
- **[SEC EDGAR](https://www.sec.gov/edgar/sec-api-documentation)**: Corporate filings

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

### Current Release: v0.1.16
- ✅ Multi-agent workflows (Investment Analysis)
- ✅ `/analyze` command for comprehensive analysis
- ✅ Shared state architecture for agent collaboration

### Next: v0.1.17-0.1.20
- [ ] Additional workflows (Tax Optimization, Portfolio Rebalancing)
- [ ] Atlas agent (Investment Strategist) for strategic allocation
- [ ] Human-in-the-loop checkpoints for workflow approval
- [ ] Parallel agent execution for independent analyses

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
- **Data Providers** - Alpha Vantage, FMP, Tiingo, Finnhub, FRED, SEC, NewsAPI

---

<div align="center">

**Built with ❤️ for retail investors**

[⬆ Back to Top](#-navam-invest)

</div>
