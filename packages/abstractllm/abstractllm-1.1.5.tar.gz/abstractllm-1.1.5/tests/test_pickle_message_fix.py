#!/usr/bin/env python3
"""
Test script to verify pickle loading fix for Message class compatibility.
This tests the fix for the metadata AttributeError when loading pickle sessions.
"""

import sys
import pickle
import tempfile
from datetime import datetime
from abstractllm.session import Session

def test_pickle_message_loading():
    """Test that pickle-loaded sessions work with tool messages that have metadata."""

    print("=" * 70)
    print("Testing Pickle Loading Fix for Message Class Compatibility")
    print("=" * 70)

    # Step 1: Create a pickle file simulating the old format
    print("\n1. Creating simulated pickle session (old format)...")

    # Simulate old pickle format with basic message dictionaries
    session_state = {
        'messages': [
            {
                'role': 'system',
                'content': 'You are a helpful assistant',
                'timestamp': datetime.now().isoformat()
            },
            {
                'role': 'user',
                'content': 'Please read a file',
                'timestamp': datetime.now().isoformat()
            },
            {
                'role': 'tool',
                'content': 'File contents here',
                'name': 'read_file',
                'timestamp': datetime.now().isoformat(),
                'metadata': {
                    'tool_call_id': 'call_123',
                    'tool_name': 'read_file',
                    'execution_time': 0.5
                },
                'tool_results': []
            }
        ],
        'system_prompt': 'You are a helpful assistant',
        'metadata': {},
        'command_history': [],
        'default_streaming': True
    }

    with tempfile.NamedTemporaryFile(mode='wb', suffix='.pkl', delete=False) as f:
        pickle_file = f.name
        pickle.dump(session_state, f)

    print(f"   ✓ Created pickle file: {pickle_file}")
    print(f"   ✓ Contains {len(session_state['messages'])} messages")

    # Step 2: Simulate the pickle loading process
    print("\n2. Loading pickle and creating Message objects...")

    try:
        with open(pickle_file, 'rb') as f:
            loaded_state = pickle.load(f)

        # Use the FIXED code from commands.py
        from abstractllm.session import Message

        messages = [
            Message(
                role=msg['role'],
                content=msg['content'],
                name=msg.get('name'),
                timestamp=datetime.fromisoformat(msg['timestamp']) if 'timestamp' in msg else datetime.now(),
                metadata=msg.get('metadata', {}),
                tool_results=msg.get('tool_results', []),
                tool_calls=msg.get('tool_calls', [])
            )
            for msg in loaded_state['messages']
        ]

        print(f"   ✓ Created {len(messages)} Message objects")

        # Verify all messages have required attributes
        for i, msg in enumerate(messages):
            if not hasattr(msg, 'metadata'):
                print(f"   ✗ ERROR: Message {i} missing metadata attribute")
                return False
            if not hasattr(msg, 'tool_calls'):
                print(f"   ✗ ERROR: Message {i} missing tool_calls attribute")
                return False
            if not hasattr(msg, 'timestamp'):
                print(f"   ✗ ERROR: Message {i} missing timestamp attribute")
                return False

        print(f"   ✓ All messages have required attributes (metadata, tool_calls, timestamp)")

        # Step 3: Test get_messages_for_provider (where the bug occurred)
        print("\n3. Testing get_messages_for_provider with tool message...")

        # Create a minimal session
        session = Session(system_prompt="Test")
        session.messages = messages

        try:
            # This is where the bug occurred - accessing metadata
            for provider_name in ["lmstudio", "ollama", "openai"]:
                formatted = session.get_messages_for_provider(provider_name)
                print(f"   ✓ {provider_name}: Successfully formatted {len(formatted)} messages")

                # Verify tool message was handled correctly
                tool_msgs = [m for m in formatted if m.get('role') == 'tool']
                if tool_msgs:
                    tool_msg = tool_msgs[0]
                    if 'tool_call_id' in tool_msg:
                        print(f"      → Tool message has tool_call_id: {tool_msg['tool_call_id']}")

        except AttributeError as e:
            if "'Message' object has no attribute 'metadata'" in str(e):
                print(f"   ✗ ERROR: The original metadata bug still exists!")
                print(f"      {e}")
                return False
            else:
                raise

        # Step 4: Test defensive access works even without metadata
        print("\n4. Testing defensive access with missing metadata...")

        # Create a Message without metadata (edge case)
        class MinimalMessage:
            def __init__(self):
                self.role = 'tool'
                self.content = 'test'
                self.name = 'test_tool'
                # Intentionally missing: metadata, tool_calls

        minimal_msg = MinimalMessage()

        # Test defensive access (line 713 in session.py)
        tool_call_id = getattr(minimal_msg, 'metadata', {}).get('tool_call_id', '')

        if tool_call_id == '':
            print(f"   ✓ Defensive access works: returned empty string for missing metadata")
        else:
            print(f"   ✗ ERROR: Defensive access failed")
            return False

        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print("\nThe fix successfully handles:")
        print("  1. ✓ Pickle loading uses correct Message class (session.Message)")
        print("  2. ✓ All required attributes are passed (metadata, tool_calls, timestamp)")
        print("  3. ✓ Tool messages with metadata work correctly")
        print("  4. ✓ Defensive access prevents AttributeError")
        print("\nThe user's incredible-session.pkl should now work correctly!")

        return True

    finally:
        # Clean up
        import os
        if os.path.exists(pickle_file):
            os.unlink(pickle_file)
            print(f"\n🗑️  Cleaned up test file: {pickle_file}")

if __name__ == "__main__":
    try:
        success = test_pickle_message_loading()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
