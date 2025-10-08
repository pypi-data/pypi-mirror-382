import json
from typing import Any, Dict
from ..agent import AgentEvent

class ConsoleFormatter:
    """Handles formatting of agent events for console output"""
    
    def format_event(self, event: AgentEvent) -> None:
        if event.event_type == "new_message":
            role = event.data["role"]
            name = event.meta.get("agent_name", None)
            content = event.data.get("content", None)
            tool_call_id = event.data.get("tool_call_id", None)
            tool_calls = event.data.get("tool_calls", None)
            
            # Create a clean separator and header
            print("\n" + "=" * 60)
            if role == "tool":
                print(f"🔧 TOOL RESULT: (ID: {tool_call_id})")
            elif role == "user":
                print(f"👤 USER MESSAGE:")
            elif role == "assistant":
                print(f"🤖 ASSISTANT {name} MESSAGE:")
            else:
                print(f"🤖 {role.upper()} MESSAGE")
            print("=" * 60)
            
            # Handle content formatting
            if content:
                if isinstance(content, str):
                    # Simple string content
                    self._print_formatted_text(content)
                else:
                    # List content (multimodal)
                    for item in content:
                        if item.get("type") == "text":
                            self._print_formatted_text(item.get('text', ''))
                        elif item.get("type") == "image_url":
                            print("   🖼️  [Image attached]")
                        else:
                            print(f"   📎 [{item.get('type', 'unknown').title()} content]")
            
            # Handle tool calls formatting
            if tool_calls:
                print("\n🔧 Tool Calls:")
                for i, tool_call in enumerate(tool_calls, 1):
                    function_info = tool_call.get('function', {})
                    function_name = function_info.get('name', 'unknown')
                    function_args = function_info.get('arguments', '{}')
                    tool_call_id = tool_call.get('id', None)
                    print(f"   [{i}] {function_name} (ID: {tool_call_id})")
                    try:
                        args_dict = json.loads(function_args) if isinstance(function_args, str) else function_args
                        if args_dict:
                            for key, value in args_dict.items():
                                # Truncate long values for readability
                                if isinstance(value, str) and len(value) > 100:
                                    display_value = value[:97] + "..."
                                else:
                                    display_value = value
                                print(f"       {key}: {display_value}")
                        else:
                            print("       (no arguments)")
                    except (json.JSONDecodeError, TypeError):
                        print(f"       arguments: {function_args}")
            
            print("=" * 60 + "\n")
            
        else:
            # Handle other event types
            print(f"\n📡 Event: {event.event_type}")
            if event.data:
                print(f"   Data: {json.dumps(event.data, indent=2)}")
            print()
    
    def _print_formatted_text(self, text: str) -> None:
        """Helper method to format text content with proper indentation"""
        if not text:
            return
        # try to json load the text
        try:
            json_text = json.loads(text)
            text = json.dumps(json_text, indent=2)
        except (json.JSONDecodeError, TypeError):
            pass
        # Split into lines and add indentation
        lines = text.strip().split('\n')
        for line in lines:
            if line.strip():  # Only print non-empty lines
                print(f"   {line}")
            else:
                print()  # Preserve empty lines for spacing
    
