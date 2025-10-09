"""Textual-based TUI for Navam Invest."""

import asyncio
import random
from typing import Optional

from langchain_core.messages import HumanMessage
from rich.markdown import Markdown
from rich.table import Table
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Footer, Header, Input, RichLog

from navam_invest.agents.portfolio import create_portfolio_agent
from navam_invest.agents.research import create_research_agent
from navam_invest.agents.quill import create_quill_agent
from navam_invest.agents.screen_forge import create_screen_forge_agent
from navam_invest.agents.macro_lens import create_macro_lens_agent
from navam_invest.agents.earnings_whisperer import create_earnings_whisperer_agent
from navam_invest.workflows import create_investment_analysis_workflow
from navam_invest.config.settings import ConfigurationError
from navam_invest.utils import check_all_apis

# Example prompts for each agent
PORTFOLIO_EXAMPLES = [
    "What's the current price and overview of AAPL?",
    "Show me the fundamentals and financial ratios for TSLA",
    "What insider trades have happened at MSFT recently?",
    "Screen for tech stocks with P/E ratio under 20 and market cap over $10B",
    "Get the latest 10-K filing for GOOGL",
    "Show me institutional holdings (13F filings) for NVDA",
    "Compare the financial ratios of AAPL and MSFT",
    "What does the latest 10-Q for AMZN reveal about their business?",
]

RESEARCH_EXAMPLES = [
    "What's the current GDP growth rate?",
    "Show me key macro indicators: GDP, CPI, and unemployment",
    "What does the Treasury yield curve look like today?",
    "Calculate the 10-year minus 2-year yield spread",
    "What's the current debt-to-GDP ratio?",
    "How has inflation (CPI) trended over the past year?",
    "What's the current federal funds rate?",
    "Is the yield curve inverted? What does that signal?",
]

QUILL_EXAMPLES = [
    "Analyze AAPL and provide an investment thesis with fair value",
    "What's your investment recommendation for TSLA? Include catalysts and risks",
    "Deep dive on MSFT: business quality, financials, and valuation",
    "Build an investment case for GOOGL with DCF-based fair value",
    "Analyze NVDA's 5-year fundamental trends and provide a thesis",
    "What does the latest 10-K reveal about AMZN's business model?",
    "Compare META and SNAP: which is the better investment and why?",
    "Thesis on NFLX: analyze subscriber growth, margins, and competition",
]

SCREEN_FORGE_EXAMPLES = [
    "Screen for value stocks: P/E under 15, P/B under 2, market cap over $1B",
    "Find growth stocks with revenue growth >20% and expanding margins",
    "Screen for quality companies: ROE >15%, net margin >10%, low debt",
    "Identify dividend stocks with yield >3% and 5+ year payment history",
    "Find small-cap growth stocks: market cap $300M-$2B, growth >25%",
    "Screen for tech stocks with strong momentum and positive analyst sentiment",
    "Find undervalued healthcare stocks with strong fundamentals",
    "Screen for large-cap stocks with consistent earnings growth and low volatility",
]

MACRO_LENS_EXAMPLES = [
    "What's the current macro regime? Are we in expansion, peak, or recession?",
    "Analyze the yield curve. Is it signaling recession risk?",
    "What sectors should I overweight given current economic conditions?",
    "Assess inflation trends and Fed policy implications for markets",
    "What factor exposures (value/growth, size, quality) make sense now?",
    "Identify top 3 macro risks to monitor over the next 6 months",
    "How do current GDP, unemployment, and inflation compare to historical norms?",
    "Should I be defensive or cyclical given the economic cycle phase?",
]

EARNINGS_WHISPERER_EXAMPLES = [
    "Analyze AAPL earnings history - are they consistent beaters?",
    "What's TSLA's earnings surprise trend over the last 4 quarters?",
    "Is there a post-earnings drift opportunity in NVDA after recent earnings?",
    "When is MSFT's next earnings date? What are analyst estimates?",
    "Show me GOOGL's earnings quality - revenue vs EPS beats",
    "Track analyst estimate revisions for AMZN post-earnings",
    "Find stocks with 3+ consecutive quarters beating estimates",
    "Analyze META's earnings momentum and recommend a trade",
]

WORKFLOW_EXAMPLES = [
    "/analyze AAPL - Complete investment analysis (fundamental + macro)",
    "/analyze MSFT - Should I invest? Get both bottom-up and top-down view",
    "/analyze NVDA - Multi-agent analysis combining Quill and Macro Lens",
    "/analyze GOOGL - Comprehensive thesis with macro timing validation",
]


class ChatUI(App):
    """Navam Invest chat interface."""

    CSS = """
    Screen {
        layout: vertical;
    }

    #chat-log {
        height: 1fr;
        border: solid $primary;
        padding: 1;
    }

    #input-container {
        height: auto;
        padding: 1;
    }

    #user-input {
        width: 100%;
    }
    """

    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
        ("ctrl+c", "clear", "Clear"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.portfolio_agent: Optional[object] = None
        self.research_agent: Optional[object] = None
        self.quill_agent: Optional[object] = None
        self.screen_forge_agent: Optional[object] = None
        self.macro_lens_agent: Optional[object] = None
        self.investment_workflow: Optional[object] = None
        self.current_agent: str = "portfolio"
        self.agents_initialized: bool = False

    def compose(self) -> ComposeResult:
        """Compose the UI."""
        yield Header()
        yield RichLog(id="chat-log", highlight=True, markup=True)
        yield Container(
            Input(
                placeholder="Ask about stocks or economic indicators (/examples for ideas, /help for commands)...",
                id="user-input",
            ),
            id="input-container",
        )
        yield Footer()

    async def on_mount(self) -> None:
        """Initialize agents when app mounts."""
        chat_log = self.query_one("#chat-log", RichLog)
        chat_log.write(
            Markdown(
                "# Welcome to Navam Invest\n\n"
                "Your AI-powered investment advisor. Ask me about stocks, "
                "economic indicators, or portfolio analysis.\n\n"
                "**Commands:**\n"
                "- `/portfolio` - Switch to portfolio analysis agent\n"
                "- `/research` - Switch to market research agent\n"
                "- `/quill` - Switch to Quill equity research agent\n"
                "- `/screen` - Switch to Screen Forge screening agent\n"
                "- `/macro` - Switch to Macro Lens market strategist\n"
                "- `/earnings` - Switch to Earnings Whisperer earnings analyst\n"
                "- `/analyze <SYMBOL>` - Multi-agent investment analysis\n"
                "- `/examples` - Show example prompts for current agent\n"
                "- `/clear` - Clear chat history\n"
                "- `/quit` - Exit the application\n"
                "- `/help` - Show all commands\n\n"
                "**Keyboard Shortcuts:**\n"
                "- `Ctrl+C` - Clear chat\n"
                "- `Ctrl+Q` - Quit\n\n"
                "**Tip:** Type `/examples` to see what you can ask!\n"
            )
        )

        # Initialize agents
        try:
            self.portfolio_agent = await create_portfolio_agent()
            self.research_agent = await create_research_agent()
            self.quill_agent = await create_quill_agent()
            self.screen_forge_agent = await create_screen_forge_agent()
            self.macro_lens_agent = await create_macro_lens_agent()
            self.earnings_whisperer_agent = await create_earnings_whisperer_agent()
            self.investment_workflow = await create_investment_analysis_workflow()
            self.agents_initialized = True
            chat_log.write("[green]✓ Agents initialized successfully (Portfolio, Research, Quill, Screen Forge, Macro Lens, Earnings Whisperer)[/green]")
            chat_log.write("[green]✓ Multi-agent workflow ready (Investment Analysis)[/green]")
        except ConfigurationError as e:
            self.agents_initialized = False
            # Show helpful setup instructions for missing API keys
            chat_log.write(
                Markdown(
                    f"# ⚠️ Configuration Required\n\n"
                    f"{str(e)}\n\n"
                    f"---\n\n"
                    f"**Quick Setup:**\n\n"
                    f"1. Copy the example file: `cp .env.example .env`\n"
                    f"2. Edit `.env` and add your API key\n"
                    f"3. Restart the application: `navam invest`\n\n"
                    f"Press `Ctrl+Q` to quit."
                )
            )
        except Exception as e:
            self.agents_initialized = False
            chat_log.write(
                Markdown(
                    f"# ❌ Error Initializing Agents\n\n"
                    f"```\n{str(e)}\n```\n\n"
                    f"Please check your configuration and try again.\n\n"
                    f"Press `Ctrl+Q` to quit."
                )
            )

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle user input submission."""
        text = event.value.strip()
        if not text:
            return

        # Prevent input if agents failed to initialize
        if not self.agents_initialized:
            return

        # Clear input
        input_widget = self.query_one("#user-input", Input)
        input_widget.value = ""

        chat_log = self.query_one("#chat-log", RichLog)

        # Handle commands
        if text.startswith("/"):
            await self._handle_command(text, chat_log)
            return

        # Display user message
        chat_log.write(f"\n[bold cyan]You:[/bold cyan] {text}\n")

        # Get agent response
        try:
            # Select agent based on current mode
            if self.current_agent == "portfolio":
                agent = self.portfolio_agent
                agent_name = "Portfolio Analyst"
            elif self.current_agent == "research":
                agent = self.research_agent
                agent_name = "Market Researcher"
            elif self.current_agent == "quill":
                agent = self.quill_agent
                agent_name = "Quill (Equity Research)"
            elif self.current_agent == "screen":
                agent = self.screen_forge_agent
                agent_name = "Screen Forge (Equity Screening)"
            elif self.current_agent == "macro":
                agent = self.macro_lens_agent
                agent_name = "Macro Lens (Market Strategist)"
            elif self.current_agent == "earnings":
                agent = self.earnings_whisperer_agent
                agent_name = "Earnings Whisperer"
            else:
                agent = self.portfolio_agent
                agent_name = "Portfolio Analyst"

            if not agent:
                chat_log.write("[red]Error: Agent not initialized[/red]")
                return

            chat_log.write(f"[bold green]{agent_name}:[/bold green] ")

            # Stream response with detailed progress
            tool_calls_shown = set()
            async for event in agent.astream(
                {"messages": [HumanMessage(content=text)]},
                stream_mode=["values", "updates"]
            ):
                # Parse the event tuple
                if isinstance(event, tuple) and len(event) == 2:
                    event_type, event_data = event

                    # Handle node updates (shows which node executed)
                    if event_type == "updates":
                        for node_name, node_output in event_data.items():
                            # Show tool execution completion
                            if node_name == "tools" and "messages" in node_output:
                                for msg in node_output["messages"]:
                                    if hasattr(msg, "name"):
                                        tool_name = msg.name
                                        chat_log.write(f"[dim]  ✓ {tool_name} completed[/dim]\n")

                            # Show agent making tool calls
                            elif node_name == "agent" and "messages" in node_output:
                                for msg in node_output["messages"]:
                                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                                        for tool_call in msg.tool_calls:
                                            call_id = tool_call.get("id", "")
                                            if call_id not in tool_calls_shown:
                                                tool_calls_shown.add(call_id)
                                                tool_name = tool_call.get("name", "unknown")
                                                tool_args = tool_call.get("args", {})

                                                # Format args for display
                                                args_preview = ", ".join(
                                                    f"{k}={str(v)[:30]}" for k, v in list(tool_args.items())[:3]
                                                )
                                                if len(tool_args) > 3:
                                                    args_preview += "..."

                                                chat_log.write(
                                                    f"[dim]  → Calling {tool_name}({args_preview})[/dim]\n"
                                                )

                    # Handle complete state values
                    elif event_type == "values":
                        if "messages" in event_data and event_data["messages"]:
                            last_msg = event_data["messages"][-1]
                            if hasattr(last_msg, "content") and last_msg.content:
                                # Show final response only
                                if not hasattr(last_msg, "tool_calls") or not last_msg.tool_calls:
                                    chat_log.write(Markdown(last_msg.content))

        except Exception as e:
            chat_log.write(f"\n[red]Error: {str(e)}[/red]")

    async def _handle_command(self, command: str, chat_log: RichLog) -> None:
        """Handle slash commands."""
        if command.startswith("/analyze"):
            # Extract symbol from command
            parts = command.split()
            if len(parts) != 2:
                chat_log.write(
                    Markdown(
                        "\\n**Usage**: `/analyze <SYMBOL>`\\n\\n"
                        "Example: `/analyze AAPL`\\n"
                    )
                )
                return

            symbol = parts[1].upper()
            chat_log.write(f"\\n[bold cyan]You:[/bold cyan] Analyze {symbol}\\n")
            chat_log.write(f"[bold green]Investment Analysis Workflow:[/bold green] Starting multi-agent analysis...\\n")

            try:
                # Run the workflow
                tool_calls_shown = set()
                async for event in self.investment_workflow.astream(
                    {
                        "messages": [HumanMessage(content=f"Analyze {symbol}")],
                        "symbol": symbol,
                        "quill_analysis": "",
                        "macro_context": "",
                    },
                    stream_mode=["values", "updates"]
                ):
                    # Parse the event tuple
                    if isinstance(event, tuple) and len(event) == 2:
                        event_type, event_data = event

                        # Handle node updates
                        if event_type == "updates":
                            for node_name, node_output in event_data.items():
                                # Show which agent is working
                                if node_name == "quill":
                                    chat_log.write("[dim]  📊 Quill analyzing fundamentals...[/dim]\\n")
                                elif node_name == "macro_lens":
                                    chat_log.write("[dim]  🌍 Macro Lens validating timing...[/dim]\\n")
                                elif node_name == "synthesize":
                                    chat_log.write("[dim]  🎯 Synthesizing recommendation...[/dim]\\n")

                                # Show tool calls
                                if "messages" in node_output:
                                    for msg in node_output["messages"]:
                                        if hasattr(msg, "tool_calls") and msg.tool_calls:
                                            for tool_call in msg.tool_calls:
                                                call_id = tool_call.get("id", "")
                                                if call_id not in tool_calls_shown:
                                                    tool_calls_shown.add(call_id)
                                                    tool_name = tool_call.get("name", "unknown")
                                                    chat_log.write(f"[dim]    → {tool_name}[/dim]\\n")

                        # Handle final values
                        elif event_type == "values":
                            if "messages" in event_data and event_data["messages"]:
                                last_msg = event_data["messages"][-1]
                                if hasattr(last_msg, "content") and last_msg.content:
                                    # Show final recommendation
                                    if not hasattr(last_msg, "tool_calls") or not last_msg.tool_calls:
                                        chat_log.write("\\n[bold green]Final Recommendation:[/bold green]\\n")
                                        chat_log.write(Markdown(last_msg.content))

            except Exception as e:
                chat_log.write(f"\\n[red]Error running workflow: {str(e)}[/red]")

        elif command == "/api":
            chat_log.write("\\n[bold cyan]Checking API Status...[/bold cyan]\\n")
            chat_log.write("[dim]Testing connectivity to all configured APIs...\\n\\n[/dim]")

            try:
                # Run API checks
                results = await check_all_apis()

                # Create Rich table
                table = Table(
                    title="API Status Report",
                    show_header=True,
                    header_style="bold magenta",
                    show_lines=True,
                )
                table.add_column("API Provider", style="cyan", width=18)
                table.add_column("Status", width=18)
                table.add_column("Details", style="dim", width=40)

                # Add rows
                for result in results:
                    # Color code status
                    status = result["status"]
                    if "✅" in status:
                        status_styled = f"[green]{status}[/green]"
                    elif "❌" in status:
                        status_styled = f"[red]{status}[/red]"
                    elif "⚠️" in status:
                        status_styled = f"[yellow]{status}[/yellow]"
                    else:
                        status_styled = f"[dim]{status}[/dim]"

                    table.add_row(
                        result["api"],
                        status_styled,
                        result["details"]
                    )

                # Display table
                chat_log.write(table)

                # Add summary
                working = sum(1 for r in results if "✅" in r["status"])
                failed = sum(1 for r in results if "❌" in r["status"])
                not_configured = sum(1 for r in results if "⚪" in r["status"])

                chat_log.write(
                    Markdown(
                        f"\\n**Summary:** {working} working • {failed} failed • {not_configured} not configured\\n\\n"
                        f"💡 **Tips:**\\n"
                        f"- Failed APIs: Check your `.env` file for correct API keys\\n"
                        f"- Not configured: Optional - get free keys to unlock more features\\n"
                        f"- Rate limited: Wait a few minutes and try again\\n\\n"
                        f"Run `python scripts/validate_newsapi_key.py` to validate NewsAPI.org specifically.\\n"
                    )
                )

            except Exception as e:
                chat_log.write(f"\\n[red]Error checking APIs: {str(e)}[/red]")

        elif command == "/help":
            chat_log.write(
                Markdown(
                    "\n**Available Commands:**\n"
                    "- `/portfolio` - Switch to portfolio analysis agent\n"
                    "- `/research` - Switch to market research agent\n"
                    "- `/quill` - Switch to Quill equity research agent\n"
                    "- `/screen` - Switch to Screen Forge screening agent\n"
                    "- `/macro` - Switch to Macro Lens market strategist\n"
                    "- `/earnings` - Switch to Earnings Whisperer earnings analyst\n"
                    "- `/analyze <SYMBOL>` - Multi-agent investment analysis\n"
                    "- `/api` - Check API connectivity and status\n"
                    "- `/examples` - Show example prompts for current agent\n"
                    "- `/clear` - Clear chat history\n"
                    "- `/quit` - Exit the application\n"
                    "- `/help` - Show this help message\n"
                )
            )
        elif command == "/portfolio":
            self.current_agent = "portfolio"
            chat_log.write("\n[green]✓ Switched to Portfolio Analysis agent[/green]\n")
        elif command == "/research":
            self.current_agent = "research"
            chat_log.write("\n[green]✓ Switched to Market Research agent[/green]\n")
        elif command == "/quill":
            self.current_agent = "quill"
            chat_log.write("\n[green]✓ Switched to Quill (Equity Research) agent[/green]\n")
        elif command == "/screen":
            self.current_agent = "screen"
            chat_log.write("\n[green]✓ Switched to Screen Forge (Equity Screening) agent[/green]\n")
        elif command == "/macro":
            self.current_agent = "macro"
            chat_log.write("\n[green]✓ Switched to Macro Lens (Market Strategist) agent[/green]\n")
        elif command == "/earnings":
            self.current_agent = "earnings"
            chat_log.write("\n[green]✓ Switched to Earnings Whisperer agent[/green]\n")
        elif command == "/examples":
            # Show examples for current agent
            if self.current_agent == "portfolio":
                examples = PORTFOLIO_EXAMPLES
                agent_name = "Portfolio Analysis"
            elif self.current_agent == "research":
                examples = RESEARCH_EXAMPLES
                agent_name = "Market Research"
            elif self.current_agent == "quill":
                examples = QUILL_EXAMPLES
                agent_name = "Quill (Equity Research)"
            elif self.current_agent == "screen":
                examples = SCREEN_FORGE_EXAMPLES
                agent_name = "Screen Forge (Equity Screening)"
            elif self.current_agent == "macro":
                examples = MACRO_LENS_EXAMPLES
                agent_name = "Macro Lens (Market Strategist)"
            elif self.current_agent == "earnings":
                examples = EARNINGS_WHISPERER_EXAMPLES
                agent_name = "Earnings Whisperer"
            else:
                examples = PORTFOLIO_EXAMPLES
                agent_name = "Portfolio Analysis"

            # Randomly select 4 examples to show
            selected_examples = random.sample(examples, min(4, len(examples)))

            examples_text = "\n".join(f"{i+1}. {ex}" for i, ex in enumerate(selected_examples))

            # Add workflow examples
            workflow_text = "\n".join(f"{i+1}. {ex}" for i, ex in enumerate(WORKFLOW_EXAMPLES))

            chat_log.write(
                Markdown(
                    f"\n**Example prompts for {agent_name} agent:**\n\n"
                    f"{examples_text}\n\n"
                    f"**Multi-Agent Workflows:**\n\n"
                    f"{workflow_text}\n\n"
                    f"💡 Try copying one of these or ask your own question!\n"
                )
            )
        elif command == "/clear":
            self.action_clear()
        elif command == "/quit":
            self.exit()
        else:
            chat_log.write(f"\n[yellow]Unknown command: {command}[/yellow]\n")

    def action_clear(self) -> None:
        """Clear the chat log."""
        chat_log = self.query_one("#chat-log", RichLog)
        chat_log.clear()
        chat_log.write(
            Markdown("# Chat Cleared\n\nType your question or use /help for commands.")
        )


async def run_tui() -> None:
    """Run the TUI application."""
    app = ChatUI()
    await app.run_async()
