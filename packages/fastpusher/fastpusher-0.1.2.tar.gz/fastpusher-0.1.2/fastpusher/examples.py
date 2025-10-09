"""
Examples for FastPusher library
"""

import logging

from fastpusher.exceptions import ConnectionError, ValidationError
from fastpusher.pusher import FastPusher

# Setup logging
logging.basicConfig(level=logging.INFO)

# Create FastPusher object
pusher = FastPusher(
    url="http://127.0.0.1:8000",
    token="OFJd0rU2J0iqFsPerLZNnmHpP9d7Fsm34fB1I74hHu0",
    timeout=30,
    retry_attempts=3,
    debug=True,
)


def basic_push_example():
    """Basic message sending example"""
    try:
        result = pusher.push(
            channel="admin", data={"title": "Hello!", "body": "This is a test message."}
        )
        print(f"Message sent: {result}")
    except ValidationError as e:
        print(f"Validation error: {e}")
    except ConnectionError as e:
        print(f"Connection error: {e}")


def bulk_push_example():
    """Send message to multiple channels"""
    channels = ["admin", "users", "moderators"]
    data = {
        "title": "General Announcement",
        "body": "Important information for all users.",
    }

    results = pusher.push_bulk(channels, data)

    for result in results:
        if result["success"]:
            print(f"✅ {result['channel']}: Success")
        else:
            print(f"❌ {result['channel']}: {result['error']}")


def connection_test_example():
    """Test server connection"""
    if pusher.test_connection():
        print("✅ Server connection available")
    else:
        print("❌ No server connection")


if __name__ == "__main__":
    print("🚀 FastPusher examples starting...\n")

    print("1. Basic message sending:")
    basic_push_example()
    print()
    #
    # print("2. Bulk sending:")
    # bulk_push_example()
    # print()

    print("3. Connection test:")
    connection_test_example()
    print()

    print("✅ All examples completed!")
