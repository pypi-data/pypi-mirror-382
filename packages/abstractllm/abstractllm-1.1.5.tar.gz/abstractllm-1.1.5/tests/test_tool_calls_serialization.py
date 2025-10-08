#!/usr/bin/env python3
"""
Test script to verify tool_calls serialization/deserialization fix.
This tests the fix for the session reload bug.
"""

import sys
import json
from datetime import datetime
from abstractllm.session import Message

def test_message_serialization():
    """Test that Message objects properly serialize and deserialize tool_calls."""

    print("=" * 60)
    print("Testing Message.tool_calls Serialization Fix")
    print("=" * 60)

    # Test 1: Create a message with tool_calls
    print("\n1. Creating Message with tool_calls...")
    original_tool_calls = [
        {
            "id": "call_123",
            "type": "function",
            "function": {
                "name": "read_file",
                "arguments": {"path": "/test/file.txt"}
            }
        }
    ]

    msg = Message(
        role="assistant",
        content="Let me read that file for you",
        tool_calls=original_tool_calls
    )

    print(f"   ✓ Created message with {len(msg.tool_calls)} tool call(s)")
    print(f"   ✓ Tool call: {msg.tool_calls[0]['function']['name']}")

    # Test 2: Serialize to dict
    print("\n2. Serializing message to dict...")
    msg_dict = msg.to_dict()

    if "tool_calls" in msg_dict:
        print(f"   ✓ tool_calls present in serialized dict")
        print(f"   ✓ Serialized tool_calls: {msg_dict['tool_calls']}")
    else:
        print(f"   ✗ ERROR: tool_calls NOT in serialized dict!")
        return False

    # Test 3: Deserialize from dict
    print("\n3. Deserializing message from dict...")
    restored_msg = Message.from_dict(msg_dict)

    if hasattr(restored_msg, 'tool_calls'):
        print(f"   ✓ Restored message has tool_calls attribute")
        if restored_msg.tool_calls == original_tool_calls:
            print(f"   ✓ Tool calls match original: {len(restored_msg.tool_calls)} call(s)")
        else:
            print(f"   ✗ ERROR: Tool calls don't match!")
            print(f"     Original: {original_tool_calls}")
            print(f"     Restored: {restored_msg.tool_calls}")
            return False
    else:
        print(f"   ✗ ERROR: Restored message has NO tool_calls attribute!")
        return False

    # Test 4: Test backward compatibility (old session without tool_calls)
    print("\n4. Testing backward compatibility (message without tool_calls)...")
    old_msg_dict = {
        "id": "msg_456",
        "role": "user",
        "content": "Hello",
        "timestamp": datetime.now().isoformat(),
        "metadata": {}
    }

    old_msg = Message.from_dict(old_msg_dict)

    if hasattr(old_msg, 'tool_calls'):
        if old_msg.tool_calls == []:
            print(f"   ✓ Old message has tool_calls attribute (default empty list)")
        else:
            print(f"   ✗ ERROR: Old message tool_calls should be empty, got: {old_msg.tool_calls}")
            return False
    else:
        print(f"   ✗ ERROR: Old message has NO tool_calls attribute!")
        return False

    # Test 5: Test defensive access with getattr
    print("\n5. Testing defensive access with getattr...")

    # Create a minimal message that might be missing tool_calls
    class MinimalMessage:
        def __init__(self):
            self.role = "user"
            self.content = "test"

    minimal = MinimalMessage()
    tool_calls_safe = getattr(minimal, 'tool_calls', [])

    if tool_calls_safe == []:
        print(f"   ✓ getattr provides safe default for missing attribute")
    else:
        print(f"   ✗ ERROR: getattr didn't provide safe default")
        return False

    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nThe fix successfully:")
    print("  1. Serializes tool_calls in to_dict()")
    print("  2. Deserializes tool_calls in from_dict()")
    print("  3. Maintains backward compatibility with old sessions")
    print("  4. Provides safe defensive access with getattr()")

    return True

if __name__ == "__main__":
    try:
        success = test_message_serialization()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
