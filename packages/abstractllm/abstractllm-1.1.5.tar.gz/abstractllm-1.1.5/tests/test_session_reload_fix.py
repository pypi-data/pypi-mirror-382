#!/usr/bin/env python3
"""
End-to-end test for session reload fix.
This simulates the exact scenario the user encountered:
1. Create a session with tools and messages containing tool_calls
2. Save the session
3. Load the session
4. Try to use it (which calls get_messages_for_provider)
"""

import sys
import os
import tempfile
from abstractllm.session import Session
from abstractllm.interface import ModelParameter

def test_session_reload_with_tool_calls():
    """Test that sessions with tool_calls can be saved and reloaded."""

    print("=" * 70)
    print("End-to-End Test: Session Reload with Tool Calls")
    print("=" * 70)

    # Create a temporary file for the session
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        session_file = f.name

    try:
        # Step 1: Create a session with messages
        print("\n1. Creating session with messages...")
        session = Session(system_prompt="You are a helpful assistant")

        # Add a user message
        session.add_message("user", "Can you read a file for me?")

        # Manually create an assistant message with tool_calls (simulating native tool calling)
        from abstractllm.session import Message
        from datetime import datetime

        assistant_msg = Message(
            role="assistant",
            content="I'll read that file for you.",
            timestamp=datetime.now(),
            tool_calls=[
                {
                    "id": "call_abc123",
                    "type": "function",
                    "function": {
                        "name": "read_file",
                        "arguments": {"path": "/test/file.txt"}
                    }
                }
            ]
        )
        session.messages.append(assistant_msg)

        # Add a tool result
        tool_result_msg = Message(
            role="assistant",
            content="",
            timestamp=datetime.now(),
            tool_results=[
                {
                    "call_id": "call_abc123",
                    "name": "read_file",
                    "output": "File contents here",
                    "arguments": {"path": "/test/file.txt"}
                }
            ]
        )
        session.messages.append(tool_result_msg)

        print(f"   ✓ Created session with {len(session.messages)} messages")
        print(f"   ✓ Message 2 has {len(assistant_msg.tool_calls)} tool call(s)")

        # Step 2: Save the session
        print("\n2. Saving session to JSON...")
        session.save(session_file)
        print(f"   ✓ Session saved to: {session_file}")

        # Verify the saved file contains tool_calls
        import json
        with open(session_file, 'r') as f:
            saved_data = json.load(f)

        # Check if tool_calls were serialized
        messages_with_tool_calls = [
            msg for msg in saved_data.get('messages', [])
            if 'tool_calls' in msg and msg['tool_calls']
        ]

        if messages_with_tool_calls:
            print(f"   ✓ Found {len(messages_with_tool_calls)} message(s) with tool_calls in saved file")
        else:
            print(f"   ✗ ERROR: No tool_calls found in saved file!")
            return False

        # Step 3: Load the session
        print("\n3. Loading session from JSON...")
        loaded_session = Session.load(session_file)
        print(f"   ✓ Session loaded successfully")
        print(f"   ✓ Loaded {len(loaded_session.messages)} messages")

        # Verify tool_calls were restored
        loaded_msg_with_tool_calls = [
            msg for msg in loaded_session.messages
            if hasattr(msg, 'tool_calls') and msg.tool_calls
        ]

        if loaded_msg_with_tool_calls:
            print(f"   ✓ Found {len(loaded_msg_with_tool_calls)} message(s) with tool_calls after loading")
            tool_call = loaded_msg_with_tool_calls[0].tool_calls[0]
            print(f"   ✓ Tool call preserved: {tool_call.get('function', {}).get('name', 'unknown')}")
        else:
            print(f"   ✗ ERROR: Tool calls were lost during save/load!")
            return False

        # Step 4: Test get_messages_for_provider (this is where the bug occurred)
        print("\n4. Testing get_messages_for_provider (where bug occurred)...")

        try:
            # This should work for providers that support native tool calls
            for provider_name in ["lmstudio", "ollama", "openai"]:
                messages = loaded_session.get_messages_for_provider(provider_name)
                print(f"   ✓ {provider_name}: Successfully formatted {len(messages)} messages")

                # Check if tool_calls were included
                msgs_with_tool_calls = [m for m in messages if 'tool_calls' in m]
                if msgs_with_tool_calls:
                    print(f"      → Tool calls preserved in provider format")

        except AttributeError as e:
            if "'Message' object has no attribute 'tool_calls'" in str(e):
                print(f"   ✗ ERROR: The original bug still exists!")
                print(f"      {e}")
                return False
            else:
                raise

        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print("\nThe fix successfully handles:")
        print("  1. ✓ Saving sessions with tool_calls")
        print("  2. ✓ Loading sessions with tool_calls")
        print("  3. ✓ Using loaded sessions (get_messages_for_provider)")
        print("  4. ✓ Preserving tool_calls through save/load cycle")
        print("\nThe user's 'incredible-session' should now work correctly!")

        return True

    finally:
        # Clean up
        if os.path.exists(session_file):
            os.unlink(session_file)
            print(f"\n🗑️  Cleaned up test file: {session_file}")

if __name__ == "__main__":
    try:
        success = test_session_reload_with_tool_calls()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
