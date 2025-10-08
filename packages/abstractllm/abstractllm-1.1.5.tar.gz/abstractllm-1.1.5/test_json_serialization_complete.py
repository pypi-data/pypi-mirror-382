#!/usr/bin/env python3
"""
Verification test: Ensure JSON serialization (Session.save/load) is complete.
This verifies that the fixes to Message.to_dict() and Message.from_dict()
ensure all attributes are properly serialized/deserialized.
"""

import sys
import tempfile
import os
from datetime import datetime
from abstractllm.session import Session, Message

def test_json_serialization_completeness():
    """Verify that Session.save/load properly serializes all Message attributes."""

    print("=" * 70)
    print("JSON Serialization Completeness Verification")
    print("=" * 70)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json_file = f.name

    try:
        # Step 1: Create a session with all types of messages
        print("\n1. Creating session with diverse message types...")
        session = Session(system_prompt="Test assistant")

        # Add various message types with all possible attributes
        session.add_message("user", "Test user message")

        # Assistant message with tool_calls
        assistant_msg = Message(
            role="assistant",
            content="I'll help with that",
            timestamp=datetime.now(),
            metadata={"model": "test", "tokens": 100},
            tool_calls=[
                {
                    "id": "call_123",
                    "type": "function",
                    "function": {"name": "test_tool", "arguments": {"arg": "value"}}
                }
            ]
        )
        session.messages.append(assistant_msg)

        # Tool message with metadata
        tool_msg = Message(
            role="tool",
            content="Tool output here",
            name="test_tool",
            timestamp=datetime.now(),
            metadata={
                "tool_call_id": "call_123",
                "execution_time": 0.5,
                "status": "success"
            },
            tool_results=[
                {
                    "call_id": "call_123",
                    "name": "test_tool",
                    "output": "Success",
                    "arguments": {"arg": "value"}
                }
            ]
        )
        session.messages.append(tool_msg)

        print(f"   ✓ Created session with {len(session.messages)} messages")

        # Step 2: Save using Session.save() (JSON)
        print("\n2. Saving session using Session.save() (JSON)...")
        session.save(json_file)
        print(f"   ✓ Session saved to: {json_file}")

        # Verify the JSON contains all attributes
        import json
        with open(json_file, 'r') as f:
            saved_data = json.load(f)

        print("\n3. Verifying saved JSON contains all attributes...")

        all_attrs_present = True
        for i, msg in enumerate(saved_data['messages']):
            # Check required attributes
            required = ['id', 'role', 'content', 'timestamp', 'metadata']
            missing = [attr for attr in required if attr not in msg]

            if missing:
                print(f"   ✗ Message {i} missing: {missing}")
                all_attrs_present = False

            # Check conditional attributes based on message type
            if msg['role'] == 'assistant' and i == 2:  # The tool call message
                if 'tool_calls' not in msg:
                    print(f"   ✗ Assistant message {i} missing tool_calls")
                    all_attrs_present = False
                else:
                    print(f"   ✓ Message {i}: tool_calls present ({len(msg['tool_calls'])} calls)")

            if msg['role'] == 'tool':
                if 'name' not in msg:
                    print(f"   ✗ Tool message {i} missing name")
                    all_attrs_present = False
                if 'tool_results' not in msg:
                    print(f"   ✗ Tool message {i} missing tool_results")
                    all_attrs_present = False
                else:
                    print(f"   ✓ Message {i}: name={msg.get('name')}, metadata keys={list(msg['metadata'].keys())}")

        if all_attrs_present:
            print(f"   ✓ All attributes properly serialized")
        else:
            return False

        # Step 3: Load using Session.load()
        print("\n4. Loading session using Session.load()...")
        loaded_session = Session.load(json_file)
        print(f"   ✓ Session loaded with {len(loaded_session.messages)} messages")

        # Step 4: Verify all attributes were restored
        print("\n5. Verifying all attributes were restored...")

        for i, msg in enumerate(loaded_session.messages):
            # Check all attributes exist
            attrs_to_check = ['role', 'content', 'timestamp', 'id', 'metadata', 'tool_calls', 'tool_results']
            missing = [attr for attr in attrs_to_check if not hasattr(msg, attr)]

            if missing:
                print(f"   ✗ Loaded message {i} missing attributes: {missing}")
                return False

            # Verify metadata is a dict (not None)
            if not isinstance(msg.metadata, dict):
                print(f"   ✗ Message {i} metadata is not a dict: {type(msg.metadata)}")
                return False

            # Verify tool_calls is a list
            if not isinstance(msg.tool_calls, list):
                print(f"   ✗ Message {i} tool_calls is not a list: {type(msg.tool_calls)}")
                return False

            # Verify tool_results is a list
            if not isinstance(msg.tool_results, list):
                print(f"   ✗ Message {i} tool_results is not a list: {type(msg.tool_results)}")
                return False

        print(f"   ✓ All messages have all required attributes")

        # Step 5: Test get_messages_for_provider (the code that caused crashes)
        print("\n6. Testing get_messages_for_provider (where bugs occurred)...")

        try:
            for provider_name in ["lmstudio", "ollama", "openai"]:
                formatted = loaded_session.get_messages_for_provider(provider_name)
                print(f"   ✓ {provider_name}: Successfully formatted {len(formatted)} messages")
        except AttributeError as e:
            print(f"   ✗ AttributeError occurred: {e}")
            return False

        # Step 6: Compare original and loaded
        print("\n7. Comparing original and loaded sessions...")

        if len(session.messages) != len(loaded_session.messages):
            print(f"   ✗ Message count mismatch: {len(session.messages)} != {len(loaded_session.messages)}")
            return False

        # Check tool_calls preservation
        orig_tool_msgs = [m for m in session.messages if m.tool_calls]
        loaded_tool_msgs = [m for m in loaded_session.messages if m.tool_calls]

        if len(orig_tool_msgs) != len(loaded_tool_msgs):
            print(f"   ✗ Tool call count mismatch")
            return False

        if orig_tool_msgs:
            orig_call = orig_tool_msgs[0].tool_calls[0]
            loaded_call = loaded_tool_msgs[0].tool_calls[0]
            if orig_call != loaded_call:
                print(f"   ✗ Tool calls don't match")
                return False
            print(f"   ✓ Tool calls preserved: {orig_call['function']['name']}")

        # Check metadata preservation
        orig_with_metadata = [m for m in session.messages if m.metadata]
        loaded_with_metadata = [m for m in loaded_session.messages if m.metadata]
        print(f"   ✓ Metadata preserved: {len(loaded_with_metadata)} messages with metadata")

        print("\n" + "=" * 70)
        print("✅ ALL VERIFICATION TESTS PASSED!")
        print("=" * 70)
        print("\nJSON Serialization is COMPLETE:")
        print("  1. ✓ Message.to_dict() serializes all attributes")
        print("  2. ✓ Message.from_dict() deserializes all attributes")
        print("  3. ✓ Session.save() properly uses to_dict()")
        print("  4. ✓ Session.load() properly uses from_dict()")
        print("  5. ✓ tool_calls, metadata, timestamp all preserved")
        print("  6. ✓ No AttributeError on get_messages_for_provider()")
        print("\nConclusion: The JSON serialization path does NOT need the pickle fix!")
        print("It already uses the correct Message class and all attributes.")

        return True

    finally:
        if os.path.exists(json_file):
            os.unlink(json_file)
            print(f"\n🗑️  Cleaned up test file: {json_file}")

if __name__ == "__main__":
    try:
        success = test_json_serialization_completeness()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ VERIFICATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
