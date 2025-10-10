import asyncio
import logging
from pathlib import Path

from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient, create_sdk_mcp_server
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.prompt import Prompt

from claudecut.agent_tools import (
    add_captions,
    analyze_silences,
    cut_video,
    generate_subtitles,
)

# Set up logging with Rich
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

logger = logging.getLogger(__name__)
console = Console()


SYSTEM_PROMPT = """You are a video editing assistant. Your job is simple:

1. Generate captions from video (word SRT, sentence SRT, plain text)
2. Add burned-in captions to video with progressive highlighting
3. Analyze captions to find audio segments or silences
4. Check video info
5. Cut the video based on user instructions
6. After cutting, ask if the user wants to delete the caption files

Instructions:
- User provides video path
- ALWAYS start by generating captions first (creates 3 files: word SRT,
  sentence SRT, transcript TXT)
- The plain text transcript file (*_transcript.txt) has no timestamps - use
  it for quick overview of content to decide which segments are cohesive
- For timing decisions, read the sentence SRT file to see timestamps
- ALWAYS use get_video_info first to get video duration, then use that exact
  duration as the end time for the final segment
- [Optional] Use analyze_silences tool to find gaps/silences
- If you cut around audio segments, add 0.2 seconds of silence padding before
  and after each segment.
- If you cut based on analyze_silences result, do NOT add padding. it already
  does this. Also make sure to not accidentally throw away the start or end.
- For add_captions: MUST use word-level SRT file (*_word.srt), NOT sentence SRT
- After successful video cut, ask: "Would you like me to delete the caption
  files?"
- If yes, use Bash tool to delete word SRT, sentence SRT, and transcript TXT

Tools:
- generate_subtitles (creates word SRT, sentence SRT, transcript TXT)
- add_captions (burns captions into video - requires word SRT)
- analyze_silences
- cut_video (list of [start, end] time pairs in sec (floats supported))

Examples:
- "Remove silences" → analyze_silences → cut those ranges
- "Create shorts" → Read transcript TXT for content → Read sentence SRT for
  timing → pick good segments → cut with 0.2s silence padding (no overlap)
- "Keep segments where X" → Read transcript TXT → find matches → Read
  sentence SRT for timing → cut those ranges

Keep responses concise. Focus on the task."""


def _create_agent_client(working_dir: Path) -> ClaudeSDKClient:
    """Create and configure the Claude agent client."""
    server = create_sdk_mcp_server(
        name="video-tools",
        version="1.0.0",
        tools=[generate_subtitles, add_captions, analyze_silences, cut_video],
    )

    options = ClaudeAgentOptions(
        mcp_servers={"video-tools": server},
        allowed_tools=[
            "mcp__video-tools__generate_subtitles",
            "mcp__video-tools__add_captions",
            "mcp__video-tools__analyze_silences",
            "mcp__video-tools__cut_video",
            "Read",
            "Bash",
        ],
        system_prompt=SYSTEM_PROMPT,
        cwd=str(working_dir),
        permission_mode="acceptEdits",
        model="claude-sonnet-4-5",
    )

    return ClaudeSDKClient(options=options)


async def _process_response(client: ClaudeSDKClient) -> None:
    """Process and display agent response."""
    async for msg in client.receive_response():
        if hasattr(msg, "content") and msg.content:  # type: ignore
            for block in msg.content:  # type: ignore
                # Text content
                if hasattr(block, "text") and block.text:  # type: ignore
                    console.print(block.text, end="")  # type: ignore
                # Tool use (show what tool is being called)
                elif hasattr(block, "name"):  # Tool use block
                    tool_name = getattr(block, "name", "unknown")
                    console.print(
                        f"\n[dim]→ Using tool: {tool_name}[/dim]", style="cyan"
                    )
                elif isinstance(block, str):
                    console.print(block, end="")


async def run_agent(working_dir: Path | None = None) -> None:
    """
    Run the interactive Claude agent.

    Args:
        working_dir: Working directory for the agent (default: current directory)
    """
    if working_dir is None:
        working_dir = Path.cwd()

    console.print(
        Panel.fit(
            "[bold cyan]Video Editing Agent[/bold cyan]\n\n"
            "Cut videos based on captions.\n\n"
            "Workflow: Provide video → Generate captions → Cut based on your needs\n\n"
            "[dim]Type 'quit' or 'exit' to end[/dim]",
            title="Ready",
        )
    )

    async with _create_agent_client(working_dir) as client:
        while True:
            console.print()
            user_input = Prompt.ask("[bold green]You[/bold green]")

            if user_input.lower() in ["quit", "exit", "q"]:
                console.print("[dim]Goodbye![/dim]")
                break

            if not user_input.strip():
                continue

            try:
                console.print("[bold blue]Agent[/bold blue]: ", end="")
                await client.query(user_input)
                await _process_response(client)
            except KeyboardInterrupt:
                console.print("\n[dim]Interrupted[/dim]")
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                logger.exception("Agent error")


async def run_agent_once(prompt: str, working_dir: Path | None = None) -> None:
    """
    Run a single query through the agent.

    Args:
        prompt: The query to send to the agent
        working_dir: Working directory for the agent (default: current directory)
    """
    if working_dir is None:
        working_dir = Path.cwd()

    console.print(f"[bold green]Query:[/bold green] {prompt}\n")
    console.print("[bold blue]Agent:[/bold blue]")

    async with _create_agent_client(working_dir) as client:
        try:
            await client.query(prompt)
            await _process_response(client)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            logger.exception("Agent error")


def main() -> None:
    """Main entry point for the agent."""
    import sys

    if len(sys.argv) > 1:
        # Run with a single prompt from command line
        prompt = " ".join(sys.argv[1:])
        asyncio.run(run_agent_once(prompt))
    else:
        # Run interactive mode
        asyncio.run(run_agent())


if __name__ == "__main__":
    main()
