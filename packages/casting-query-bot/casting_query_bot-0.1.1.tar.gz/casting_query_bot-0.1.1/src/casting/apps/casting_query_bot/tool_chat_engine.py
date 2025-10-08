import asyncio

# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownVariableType=false, reportUnknownParameterType=false
import json
import uuid
from dataclasses import dataclass
from typing import Optional

from casting.platform.config import bootstrap_env, find_app_dir
from litellm import acompletion

from casting.cast.query import cast_query
from llmgine.bus.bus import MessageBus
from llmgine.llm import SessionID
from llmgine.llm.tools import ToolCall
from llmgine.llm.tools.tool_manager import ToolManager
from llmgine.llm.context.memory import SimpleChatHistory
from llmgine.llm.tools.tool_events import ToolExecuteResultEvent
from llmgine.messages.commands import Command, CommandResult
from llmgine.messages.events import Event
from llmgine.ui.cli.cli import EngineCLI
from llmgine.ui.cli.components import EngineResultComponent, ToolComponent, ToolResultEvent

from casting.discord.framework.protocol import PromptRequestCommand

# Optional pydantic-ai support could be added here if needed


@dataclass
class DarcyToolChatEngineCommand(Command):
    """Command for the Tool Chat Engine."""

    prompt: str = ""


@dataclass
class DarcyToolChatEngineStatusEvent(Event):
    """Status event for the Tool Chat Engine."""

    status: str = ""


# Confirmation is handled via PromptRequestCommand through the Discord adapter


def get_weather(city: str) -> str:
    """Get the current weather for a given city."""
    # Mock implementation
    return f"The weather in {city} is sunny and 72°F"


def calculate(expression: str) -> str:
    """Calculate a mathematical expression."""
    try:
        result = eval(expression)
        return f"The result of {expression} is {result}"
    except Exception as e:
        return f"Error calculating {expression}: {str(e)}"


async def search_web(query: str) -> str:
    """Search the web for information."""
    # Mock implementation
    await asyncio.sleep(1)  # Simulate network delay
    return f"Search results for '{query}': [Mock results - This would contain actual search results]"


def play_music(song: str, artist: str = "") -> str:
    """Play a song."""
    if artist:
        return f"Now playing '{song}' by {artist}"
    return f"Now playing '{song}'"


class DarcyToolChatEngine:
    """An engine that can chat and use tools."""

    def __init__(self, model: str = "gpt-4o-mini", session_id: Optional[str] = None):
        self.session_id = SessionID(session_id or str(uuid.uuid4()))
        self.bus = MessageBus()
        self.model = model

        # Engine-local but reusable context manager
        self.chat = SimpleChatHistory(engine_id="darcy_tool_chat_engine", session_id=self.session_id)
        self.chat.set_system_prompt(
            "You are a helpful assistant with access to various tools. "
            "Use tools when appropriate to help answer user questions. "
            "You have access to a Cast knowledge base through the cast_query tool - use this when users ask questions about concepts, documentation, or organizational knowledge."
            "You will be given discord messages, respond to them as if they are user input. The latest message is at the end."
        )

        # Initialize tool manager
        self.tool_manager = ToolManager()

        # Register tools
        self._register_tools()

    def _register_tools(self):
        """Register all available tools."""
        self.tool_manager.register_tool(get_weather)
        # self.tool_manager.register_tool(calculate)
        # self.tool_manager.register_tool(search_web)
        # self.tool_manager.register_tool(play_music)
        self.tool_manager.register_tool(cast_query)

    async def handle_command(self, command: Command) -> CommandResult:
        """Handle a chat command."""
        try:
            # Publish initial status
            await self.bus.publish(DarcyToolChatEngineStatusEvent(status="Processing", session_id=self.session_id))

            # 1. Add user message to chat history
            self.chat.add_user_message(getattr(command, "prompt", ""))

            # 2. Prepare current context and tools
            current_context = self.chat.get_messages()
            tools = self.tool_manager.parse_tools_to_list()

            # 3. Call the LLM (litellm here; engines may also use pydantic-ai internally)
            await self.bus.publish(DarcyToolChatEngineStatusEvent(status="Calling LLM", session_id=self.session_id))

            print(f"Calling LLM with context: {current_context} and tools: {tools}")

            response = await acompletion(
                model=self.model, messages=current_context, tools=tools if tools else None, max_tokens=500
            )

            # 4. Extract the message from response
            if not response.choices:
                return CommandResult(success=False, error="No response from LLM")

            message = response.choices[0].message

            # 5. Check for tool calls
            if hasattr(message, "tool_calls") and message.tool_calls:
                await self.bus.publish(
                    DarcyToolChatEngineStatusEvent(status="Executing tools", session_id=self.session_id)
                )

                # Convert litellm tool calls to our ToolCall format
                tool_calls = [
                    ToolCall(id=tc.id, name=tc.function.name or "", arguments=tc.function.arguments or "")
                    for tc in message.tool_calls
                ]

                # Confirm and execute tools one by one via Discord prompt
                tool_results = []
                for tc in tool_calls:
                    confirm_cmd = PromptRequestCommand(
                        session_id=self.session_id,
                        prompt=f"Allow tool '{tc.name}'?",
                        kind="yes_no",
                        timeout_sec=60,
                    )
                    confirm_result = await self.bus.execute(confirm_cmd)
                    proceed = bool(getattr(confirm_result, "result", False))
                    if not proceed:
                        tool_results.append(f"Error: Tool '{tc.name}' was denied by user")
                        continue
                    [exec_result] = await self.tool_manager.execute_tool_calls([tc])
                    tool_results.append(exec_result)
                    print(f"Tool '{tc.name}' executed with result: {exec_result}")

                # Add assistant message with tool calls
                self.chat.add_assistant_message(content=message.content or "", tool_calls=tool_calls)

                # Add tool results
                for tool_call, result in zip(tool_calls, tool_results):
                    self.chat.add_tool_message(tool_call_id=tool_call.id, content=str(result))
                    # Publish a UI-oriented event and an observability event
                    await self.bus.publish(
                        ToolResultEvent(tool_name=tool_call.name, result=str(result), session_id=self.session_id)
                    )
                    try:
                        tool_args_obj = (
                            json.loads(tool_call.arguments)
                            if isinstance(tool_call.arguments, str)
                            else (tool_call.arguments or {})
                        )
                    except Exception:
                        tool_args_obj = {"__raw__": tool_call.arguments}
                    await self.bus.publish(
                        ToolExecuteResultEvent(
                            execution_succeed=not str(result).startswith("Error"),
                            tool_info={"name": tool_call.name},
                            tool_args=tool_args_obj or {},
                            tool_result=str(result),
                            tool_name=tool_call.name,
                            tool_call_id=tool_call.id,
                            engine_id="darcy_tool_chat_engine",
                            session_id=self.session_id,
                        )
                    )

                # Get final response after tool execution
                await self.bus.publish(
                    DarcyToolChatEngineStatusEvent(status="Getting final response", session_id=self.session_id)
                )

                final_context = self.chat.get_messages()
                final_response = await acompletion(model=self.model, messages=final_context)
                if final_response.choices and final_response.choices[0].message.content:
                    final_content = final_response.choices[0].message.content
                    self.chat.add_assistant_message(final_content)

                    await self.bus.publish(
                        DarcyToolChatEngineStatusEvent(status="Finished", session_id=self.session_id)
                    )
                    return CommandResult(success=True, result=final_content)
                # Fallback when no content is returned after tools
                await self.bus.publish(DarcyToolChatEngineStatusEvent(status="Finished", session_id=self.session_id))
                return CommandResult(success=True, result="Done.")
            else:
                # No tool calls, just return the response
                content = message.content or ""
                self.chat.add_assistant_message(content)

                await self.bus.publish(DarcyToolChatEngineStatusEvent(status="Finished", session_id=self.session_id))
                return CommandResult(success=True, result=content)

        except Exception as e:
            await self.bus.publish(DarcyToolChatEngineStatusEvent(status="finished", session_id=self.session_id))
            return CommandResult(success=False, error=str(e))


async def main():
    """Main function to run the Tool Chat Engine."""
    from llmgine.bootstrap import ApplicationBootstrap, ApplicationConfig

    config = ApplicationConfig(enable_console_handler=False)
    bootstrap = ApplicationBootstrap(config)
    await bootstrap.bootstrap()

    # Create engine; model selection stays inside the engine
    engine = DarcyToolChatEngine(model="gpt-4o-miniº")

    # Set up CLI
    cli = EngineCLI(engine.session_id)
    cli.register_engine(engine)
    cli.register_engine_command(DarcyToolChatEngineCommand, engine.handle_command)
    cli.register_engine_result_component(EngineResultComponent)
    cli.register_loading_event(DarcyToolChatEngineStatusEvent)
    # Show tool results in the CLI
    cli.register_component_event(ToolResultEvent, ToolComponent)

    # Run the CLI
    await cli.main()


if __name__ == "__main__":
    asyncio.run(main())
