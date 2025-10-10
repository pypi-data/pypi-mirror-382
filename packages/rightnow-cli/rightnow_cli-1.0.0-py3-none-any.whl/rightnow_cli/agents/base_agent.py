"""
Base Agent - Abstract base class for all specialized agents.
"""

import os
import sys
import asyncio
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from ..tools import ToolRegistry
from ..tools.base import ToolContext
from ..openrouter_v2 import OpenRouterClientV2, Message
from ..config.schema import Config
from ..permissions import PermissionManager
from ..ui.tool_display import execute_tool_with_display

console = Console()


class BaseAgent(ABC):
    """
    Abstract base class for all specialized agents.

    Provides common functionality:
    - Tool execution
    - Conversation management
    - Permission handling
    - Configuration
    - UI/UX helpers

    Specialized agents implement:
    - name: Agent identifier
    - description: What the agent does
    - system_prompt: Agent expertise definition
    - default_model: Preferred model
    - can_handle: Intent detection
    """

    def __init__(
        self,
        working_dir: Path,
        config: Config,
        permission_manager: PermissionManager,
        registry: ToolRegistry,
        api_key: str,
        model: Optional[str] = None,
        orchestrator: Optional[Any] = None  # AgentOrchestrator (avoid circular import)
    ):
        """
        Initialize base agent.

        Args:
            working_dir: Working directory for file operations
            config: Configuration
            permission_manager: Shared permission manager
            registry: Shared tool registry
            api_key: OpenRouter API key
            model: Model override (defaults to agent's default_model)
            orchestrator: Reference to orchestrator for delegation
        """
        self.working_dir = working_dir
        self.config = config
        self.permission_manager = permission_manager
        self.registry = registry
        self.api_key = api_key
        self.orchestrator = orchestrator

        # Use provided model or agent's default
        self.model = model or self.default_model()

        # Conversation state
        self.conversation: List[Message] = []
        self.session_id = f"session_{int(__import__('time').time())}"

        # Setup API client
        self.client = OpenRouterClientV2(self.api_key, model=self.model)

        # Add system message with enhanced instructions
        enhanced_prompt = self._build_enhanced_system_prompt()
        self.conversation.append(Message(
            role="system",
            content=enhanced_prompt
        ))

    # ============================================================================
    # Abstract Methods - Must be implemented by specialized agents
    # ============================================================================

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Agent name (e.g., 'optimizer', 'debugger').

        Used for:
        - Display in UI
        - Agent switching commands
        - Logging
        """
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """
        Human-readable agent name for display.

        Examples:
        - "CUDA Optimizer"
        - "CUDA Debugger"
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """
        Short description of what this agent does.

        Used in:
        - Help messages
        - Agent selection UI
        """
        pass

    @abstractmethod
    def system_prompt(self) -> str:
        """
        System prompt that defines agent's expertise.

        This is the most important part - it defines:
        - Agent's specialization
        - How it should approach tasks
        - What tools it should prioritize
        - Communication style
        """
        pass

    @abstractmethod
    def default_model(self) -> str:
        """
        Default model for this agent.

        Examples:
        - Optimizer: "deepseek/deepseek-coder"
        - Debugger: "anthropic/claude-3.5-sonnet"
        - Analyzer: "deepseek/deepseek-chat"
        """
        pass

    def can_handle(self, query: str) -> float:
        """
        Determine if this agent can handle the query.

        Returns confidence score 0-1:
        - 0.0-0.3: Low confidence (not a good fit)
        - 0.3-0.7: Medium confidence (could handle)
        - 0.7-1.0: High confidence (perfect fit)

        Default implementation returns 0.5 (neutral).
        Specialized agents should override with keyword detection.

        Args:
            query: User's query

        Returns:
            Confidence score (0-1)
        """
        return 0.5

    # ============================================================================
    # Enhanced System Prompt Builder
    # ============================================================================

    def _build_enhanced_system_prompt(self) -> str:
        """Build system prompt with critical operational instructions."""
        base_prompt = self.system_prompt()

        enhanced_instructions = """

╔═══════════════════════════════════════════════════════════════════╗
║  ROCK-SOLID OPERATIONAL RULES - HANDLE CRITICAL CODE WITH CARE   ║
╚═══════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. FILE OPERATIONS - ZERO DATA LOSS POLICY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**BEFORE EDITING:**
✓ ALWAYS read_file FIRST - never edit blind
✓ Verify content loaded completely (check line count)
✓ For new files: write_file directly (no read needed)
✓ Large files (>500 lines): confirm you have FULL content

**DURING EDITING:**
✓ Include COMPLETE file - NEVER truncate with "..." or "rest unchanged"
✓ One write_file = entire file content (all imports, all functions, everything)
✓ Make ALL changes in ONE write - no partial edits
✓ Preserve exact formatting, imports, comments you're not changing
✓ If file is 1000 lines, your write_file must have ~1000 lines

**AFTER WRITING:**
✓ State what changed in 1 sentence
✓ STOP immediately - user controls next action
✓ Do NOT auto-run compile/analyze/bash
✓ Post-edit prompt lets user choose (c/a/p/b/s)

**EDGE CASES:**
→ File not found: "File X doesn't exist. Create it?"
→ Read truncated: "Warning: Large file, may be incomplete"
→ Write fails: Show error, don't retry
→ Encoding issues: Report to user

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2. TOOL USAGE - DO WHAT YOU SAY, SAY WHAT YOU DO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**GOLDEN RULE: ACTION = TOOL CALL**
→ Say "I'll read X" = MUST call read_file(X)
→ Say "I'll write X" = MUST call write_file(X)
→ Say "I'll list files" = MUST call list_files()

**FORBIDDEN:**
❌ "I would read the file..." (without calling read_file)
❌ "Let me analyze..." (without calling analyze_cuda)
❌ "I'll check..." (without calling list_files/read_file)
❌ Describing tools without using them

**REQUIRED:**
✅ Think → Act → Report (always use tools)
✅ 15 tool calls available - use efficiently
✅ Complete entire multi-step tasks
✅ Check each tool result before continuing

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3. TASK COMPLETION - FINISH WHAT YOU START
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Complete Tasks:**
✓ User: "Fix bug in line 45" → read + write fix + stop
✓ User: "Add X and Y" → add BOTH X and Y, not just X
✓ User: "Update all kernels" → update ALL, not some
✓ Multiple edits → do ALL in one write_file

**Multi-Step Flow:**
User: "Create kernel and analyze it"
→ You: write_file → STOP (user picks analyze) → (analyze when user chooses)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
4. ERROR HANDLING - CLEAR AND NON-BLOCKING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**When Tool Fails:**
✓ Show error message AS-IS
✓ NO explanations, NO tutorials, NO "here's how to fix"
✓ Error output already contains instructions
✓ Don't retry automatically
✓ Don't loop on same failure

**Example:**
❌ BAD: "Error: Tool failed. To fix: 1. Install dependencies..."
✅ GOOD: [error output only]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
5. COMMUNICATION - BRIEF, TECHNICAL, ACCURATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Engineers value precision over verbosity
✓ NEVER paste code in responses (it's in files)
✓ 1-2 sentences for file operations
✓ Just facts, no tutorials unless asked
✓ Errors = show output, nothing more

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
6. STABILITY - DETERMINISTIC AND PREDICTABLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Forbidden Patterns:**
❌ Editing without reading first
❌ Partial writes ("... rest of code unchanged")
❌ Auto-running compile after write
❌ Retrying same failed command
❌ Tool call loops (read→write→read→write)
❌ Claiming success when tool errored
❌ Hallucinating file contents

**Required Patterns:**
✅ Read → Verify → Edit completely → Stop
✅ Tool error → Show error → Wait for user
✅ One clear action → One clear result
✅ Verify before claiming success

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ABSOLUTE RULES - NEVER VIOLATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Files are sacred - NEVER lose data with truncation
2. Say it = Do it - NEVER describe tools without calling them
3. Complete writes only - NEVER partial file edits
4. Stop after write - NEVER auto-execute
5. Errors speak - NEVER over-explain failures
6. Finish tasks - NEVER stop halfway
7. Be deterministic - NEVER random exploration

**Engineers trust you with production code. Be reliable, complete, precise.**
"""

        return base_prompt + enhanced_instructions

    # ============================================================================
    # Tool Execution - Common across all agents
    # ============================================================================

    def _execute_tool(self, tool_name: str, params: Dict[str, Any]) -> str:
        """
        Execute a tool with beautiful animated display.

        Args:
            tool_name: Name of the tool
            params: Tool parameters

        Returns:
            Tool result as string
        """
        def _internal_executor(tool_name: str, params: Dict[str, Any]) -> str:
            """Internal executor that does the actual work."""
            # Create context with permission manager
            ctx = ToolContext(
                session_id=self.session_id,
                message_id=f"msg_{len(self.conversation)}",
                agent=self.name,
                working_dir=str(self.working_dir),
                permission_manager=self.permission_manager
            )

            # Execute tool (wrapping async call)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.registry.execute(tool_name, params, ctx)
            )
            loop.close()

            return str(result)

        # Use display wrapper for beautiful output
        return execute_tool_with_display(tool_name, params, _internal_executor)

    # ============================================================================
    # Chat - Common conversation handling
    # ============================================================================

    def chat(self, user_message: str) -> str:
        """
        Send a message and get response with automatic tool execution.

        Args:
            user_message: User's message

        Returns:
            Agent's response
        """
        # Add user message
        self.conversation.append(Message(
            role="user",
            content=user_message
        ))

        # Get tools in OpenRouter format
        tools = self.registry.to_openrouter_format()

        # Chat with automatic tool execution
        response = self.client.chat_with_tools(
            messages=self.conversation,
            tools=tools,
            tool_executor=self._execute_tool,
            stream=True
        )

        # Add response to conversation
        self.conversation.append(response)

        console.print()  # Small padding at bottom

        return response.content

    def clear_conversation(self):
        """Clear conversation history (keeps system prompt)."""
        system_msg = self.conversation[0]  # Preserve system prompt
        self.conversation = [system_msg]

    # ============================================================================
    # Agent Delegation - For cross-agent collaboration
    # ============================================================================

    def delegate_to(self, agent_name: str, query: str) -> str:
        """
        Delegate task to another specialized agent.

        Args:
            agent_name: Name of agent to delegate to
            query: Query for the other agent

        Returns:
            Response from delegated agent
        """
        if not self.orchestrator:
            return "❌ Cannot delegate - no orchestrator available"

        # Get target agent
        target_agent = self.orchestrator.get_agent(agent_name)
        if not target_agent:
            return f"❌ Unknown agent: {agent_name}"

        # Show delegation
        console.print(f"\n[dim]→ {self.display_name} delegating to {target_agent.display_name}[/dim]\n")

        # Execute on target agent
        response = target_agent.chat(query)

        return response

    # ============================================================================
    # UI/UX Helpers - Common display functions
    # ============================================================================

    def show_agent_header(self):
        """Show agent-specific header."""
        console.print(f"\n[bold cyan]🤖 {self.display_name}[/bold cyan]")
        console.print(f"[dim]{self.description}[/dim]")
        console.print(f"[dim]Model: {self.model}[/dim]\n")

    def show_thinking(self, message: str = "Thinking..."):
        """Show thinking indicator."""
        console.print(f"[dim]💭 {message}[/dim]")

    def show_tool_call(self, tool_name: str, params: Dict[str, Any]):
        """Show tool call in progress."""
        # Truncate params for display
        params_str = str(params)[:50]
        if len(str(params)) > 50:
            params_str += "..."

        console.print(f"[dim]🛠️  Calling: {tool_name}({params_str})[/dim]")

    def show_error(self, message: str):
        """Show error message."""
        console.print(f"\n[red]❌ {message}[/red]\n")

    def show_success(self, message: str):
        """Show success message."""
        console.print(f"\n[green]✓ {message}[/green]\n")

    # ============================================================================
    # Info Methods - Agent metadata
    # ============================================================================

    def get_info(self) -> Dict[str, Any]:
        """
        Get agent information.

        Returns:
            Dict with agent metadata
        """
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "model": self.model,
            "conversation_length": len(self.conversation),
            "session_id": self.session_id
        }

    def get_conversation_summary(self) -> str:
        """
        Get summary of conversation.

        Returns:
            Human-readable conversation summary
        """
        # Count messages by role
        user_msgs = sum(1 for m in self.conversation if m.role == "user")
        assistant_msgs = sum(1 for m in self.conversation if m.role == "assistant")

        return f"{user_msgs} user messages, {assistant_msgs} assistant messages"

    def __str__(self) -> str:
        """String representation."""
        return f"{self.display_name} ({self.model})"

    def __repr__(self) -> str:
        """Debug representation."""
        return f"<{self.__class__.__name__} name={self.name} model={self.model}>"
