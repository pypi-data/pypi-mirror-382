"""Investment Analysis Workflow - Quill → Macro Lens sequential analysis.

This workflow coordinates two specialized agents to provide comprehensive investment analysis:
1. Quill (Equity Research) - Bottom-up fundamental analysis
2. Macro Lens (Market Strategist) - Top-down macro validation

The workflow combines both perspectives to deliver a complete investment recommendation.
"""

from typing import Annotated, TypedDict

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, StateGraph, add_messages
from langgraph.prebuilt import ToolNode

from navam_invest.config.settings import get_settings
from navam_invest.tools import bind_api_keys_to_tools, get_tools_for_agent


class InvestmentAnalysisState(TypedDict):
    """State for investment analysis workflow.

    This state is shared across both agents in the sequential workflow,
    allowing Macro Lens to see Quill's analysis when providing context.
    """

    messages: Annotated[list, add_messages]
    symbol: str  # Stock symbol being analyzed
    quill_analysis: str  # Results from Quill's fundamental analysis
    macro_context: str  # Results from Macro Lens's regime analysis


async def create_investment_analysis_workflow() -> StateGraph:
    """Create a sequential multi-agent workflow for investment analysis.

    Workflow sequence:
    1. User provides symbol via /analyze command
    2. Quill analyzes fundamentals and provides investment thesis
    3. Macro Lens assesses macro regime and validates timing
    4. Combined output delivered to user

    Returns:
        Compiled LangGraph workflow
    """
    settings = get_settings()

    # Initialize LLM
    llm = ChatAnthropic(
        model=settings.anthropic_model,
        api_key=settings.anthropic_api_key,
        temperature=settings.temperature,
    )

    # Get tools for each agent
    quill_tools = get_tools_for_agent("quill")
    macro_tools = get_tools_for_agent("macro_lens")

    # Bind API keys to tools
    quill_tools_with_keys = bind_api_keys_to_tools(
        quill_tools,
        alpha_vantage_key=settings.alpha_vantage_api_key or "",
        fmp_key=settings.fmp_api_key or "",
        finnhub_key=settings.finnhub_api_key or "",
        tiingo_key=settings.tiingo_api_key or "",
        newsapi_key=settings.newsapi_api_key or "",
    )

    macro_tools_with_keys = bind_api_keys_to_tools(
        macro_tools,
        fred_key=settings.fred_api_key or "",
        newsapi_key=settings.newsapi_api_key or "",
    )

    # Agent 1: Quill - Fundamental Analysis
    async def quill_agent(state: InvestmentAnalysisState) -> dict:
        """Quill performs bottom-up fundamental analysis."""
        symbol = state["symbol"]

        system_prompt = f"""You are Quill, an expert equity research analyst. Analyze {symbol} and provide a comprehensive investment thesis.

Your analysis should include:
1. **Business Overview**: What does the company do? Competitive position?
2. **Financial Health**: Revenue growth, profitability, cash flow trends (5-year view if available)
3. **Valuation**: Is the stock fairly valued? P/E, P/B, DCF-based fair value estimate
4. **Investment Thesis**: Bull case, bear case, key catalysts
5. **Recommendation**: BUY/HOLD/SELL with confidence level

Focus on **fundamental quality** and **long-term value**. Use all available tools to gather data.

Format your response as a concise investment thesis (3-4 paragraphs) that will be combined with macro analysis."""

        # Bind tools and system prompt to LLM
        quill_llm = llm.bind_tools(quill_tools_with_keys).bind(system=system_prompt)

        response = await quill_llm.ainvoke(state["messages"])

        # Store Quill's analysis in state for Macro Lens to reference
        analysis_text = response.content if hasattr(response, "content") else str(response)

        return {
            "messages": [response],
            "quill_analysis": analysis_text,
        }

    # Agent 2: Macro Lens - Macro Validation
    async def macro_lens_agent(state: InvestmentAnalysisState) -> dict:
        """Macro Lens validates timing based on macro regime."""
        symbol = state["symbol"]
        quill_analysis = state.get("quill_analysis", "")

        system_prompt = f"""You are Macro Lens, an expert market strategist. You've received a fundamental analysis of {symbol} from Quill (equity research).

**Quill's Analysis**:
{quill_analysis}

Your task: Assess whether **NOW is the right time** to invest in {symbol} based on:
1. **Current Macro Regime**: What economic cycle phase are we in?
2. **Sector Positioning**: How does {symbol}'s sector perform in this regime?
3. **Timing Assessment**: Is this a good entry point given macro conditions?
4. **Risk Factors**: What macro risks could derail the investment thesis?

Provide a **macro validation** (2-3 paragraphs) that either:
- ✅ **Confirms timing**: "Macro conditions support this investment because..."
- ⚠️ **Suggests caution**: "Wait for better entry point because..."
- ❌ **Contradicts thesis**: "Macro headwinds make this risky because..."

Use treasury yield curve, economic indicators, and current regime analysis."""

        # Bind tools and system prompt to LLM
        macro_llm = llm.bind_tools(macro_tools_with_keys).bind(system=system_prompt)

        response = await macro_llm.ainvoke(state["messages"])

        macro_text = response.content if hasattr(response, "content") else str(response)

        return {
            "messages": [response],
            "macro_context": macro_text,
        }

    # Synthesis: Combine both analyses
    async def synthesize_recommendation(state: InvestmentAnalysisState) -> dict:
        """Combine Quill and Macro Lens analyses into final recommendation."""
        symbol = state["symbol"]
        quill_analysis = state.get("quill_analysis", "No fundamental analysis available")
        macro_context = state.get("macro_context", "No macro analysis available")

        synthesis_prompt = f"""Synthesize the following analyses for {symbol} into a final investment recommendation:

**FUNDAMENTAL ANALYSIS (Quill)**:
{quill_analysis}

**MACRO VALIDATION (Macro Lens)**:
{macro_context}

Provide a **final recommendation** with:
1. **Overall Rating**: BUY / HOLD / SELL (with confidence: High/Medium/Low)
2. **Key Reasoning**: 2-3 sentences combining both fundamental and macro perspectives
3. **Suggested Action**: What should an investor do right now?
4. **Risk Warning**: Most important risk to monitor

Keep it concise (4-5 sentences total)."""

        synthesis_msg = HumanMessage(content=synthesis_prompt)
        final_response = await llm.ainvoke([synthesis_msg])

        return {"messages": [final_response]}

    # Build the sequential workflow graph
    workflow = StateGraph(InvestmentAnalysisState)

    # Add agent nodes
    workflow.add_node("quill", quill_agent)
    workflow.add_node("macro_lens", macro_lens_agent)
    workflow.add_node("synthesize", synthesize_recommendation)

    # Add tool execution nodes
    workflow.add_node("quill_tools", ToolNode(quill_tools_with_keys))
    workflow.add_node("macro_tools", ToolNode(macro_tools_with_keys))

    # Helper functions to check if tools were called
    def quill_should_continue(state: InvestmentAnalysisState) -> str:
        """Check if Quill made tool calls."""
        messages = state["messages"]
        last_message = messages[-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "quill_tools"
        return "macro_lens"

    def macro_should_continue(state: InvestmentAnalysisState) -> str:
        """Check if Macro Lens made tool calls."""
        messages = state["messages"]
        last_message = messages[-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "macro_tools"
        return "synthesize"

    # Define the workflow with tool execution loops
    workflow.add_edge(START, "quill")
    workflow.add_conditional_edges(
        "quill",
        quill_should_continue,
        {"quill_tools": "quill_tools", "macro_lens": "macro_lens"}
    )
    workflow.add_edge("quill_tools", "quill")  # Loop back to quill after tool execution

    workflow.add_conditional_edges(
        "macro_lens",
        macro_should_continue,
        {"macro_tools": "macro_tools", "synthesize": "synthesize"}
    )
    workflow.add_edge("macro_tools", "macro_lens")  # Loop back to macro_lens after tool execution

    workflow.add_edge("synthesize", END)

    return workflow.compile()
