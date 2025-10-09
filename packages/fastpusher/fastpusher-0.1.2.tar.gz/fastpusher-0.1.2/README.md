# 🚀 FastPusher

FastPusher is a simple and efficient Python library for sending push notifications via REST API. It provides an easy-to-use interface for sending messages to channels with built-in error handling, retry logic, and bulk messaging support.

## ✨ Features

- **Simple API**: Clean and intuitive interface for sending notifications
- **Error Handling**: Comprehensive exception handling with specific error types
- **Retry Logic**: Automatic retry mechanism for failed requests
- **Bulk Messaging**: Send messages to multiple channels at once
- **Connection Testing**: Built-in health check functionality
- **Session Management**: Efficient HTTP session handling
- **Logging Support**: Configurable logging with debug mode
- **Type Hints**: Full Python type hints support

## 📦 Installation

```bash
pip install fastpusher
```

Or install from source:

```bash
git clone https://github.com/javohir/fastpusher.git
cd fastpusher
pip install -e .
```

## 🚀 Quick Start

### Basic Usage

```python
from fastpusher import FastPusher

# Create FastPusher instance
pusher = FastPusher(
    url="http://your-api-server.com",
    token="your_api_token"
)

# Send a simple message
result = pusher.push(
    channel="admin",
    data={
        "title": "Hello World!",
        "body": "This is a test message."
    }
)

print(f"Message sent: {result}")

# Always close the session when done
pusher.close()
```

### Advanced Configuration

```python
from fastpusher import FastPusher, ValidationError, ConnectionError

# Create pusher with custom settings
pusher = FastPusher(
    url="http://your-api-server.com",
    token="your_api_token",
    timeout=30,           # Request timeout in seconds
    retry_attempts=3,     # Number of retry attempts
    debug=True           # Enable debug logging
)

try:
    result = pusher.push(
        channel="notifications",
        data={
            "title": "Important Update",
            "body": "Your account has been updated successfully.",
            "priority": "high",
            "timestamp": "2025-10-08T10:30:00Z"
        }
    )
    print("✅ Message sent successfully!")

except ValidationError as e:
    print(f"❌ Validation error: {e}")
except ConnectionError as e:
    print(f"❌ Connection error: {e}")
finally:
    pusher.close()
```

## 📚 API Reference

### FastPusher Class

#### `__init__(url, token, timeout=10, retry_attempts=3, debug=False)`

Initialize FastPusher instance.

**Parameters:**
- `url` (str): API server URL
- `token` (str): Authentication token
- `timeout` (int): Request timeout in seconds (default: 10)
- `retry_attempts` (int): Number of retry attempts on failure (default: 3)
- `debug` (bool): Enable debug mode (default: False)

#### `push(channel, data)`

Send message to a single channel.

**Parameters:**
- `channel` (str): Channel name/ID
- `data` (dict): Message data to send

**Returns:** API response as dictionary

**Example:**
```python
result = pusher.push("admin", {
    "title": "System Alert",
    "body": "Server maintenance scheduled for tonight."
})
```

#### `push_bulk(channels, data)`

Send message to multiple channels.

**Parameters:**
- `channels` (List[str]): List of channel names
- `data` (dict): Message data to send

**Returns:** List of results for each channel

**Example:**
```python
channels = ["admin", "users", "moderators"]
results = pusher.push_bulk(channels, {
    "title": "General Announcement",
    "body": "New features are now available!"
})

for result in results:
    if result["success"]:
        print(f"✅ {result['channel']}: Success")
    else:
        print(f"❌ {result['channel']}: {result['error']}")
```

#### `test_connection()`

Test connection to the API server.

**Returns:** `True` if connection is successful, `False` otherwise

**Example:**
```python
if pusher.test_connection():
    print("✅ Server is reachable")
else:
    print("❌ Cannot connect to server")
```

#### `close()`

Close the HTTP session. Always call this when finished.

## 📋 Message Structure

The `data` parameter should be a dictionary containing your message payload:

```python
data = {
    "title": "Message Title",           # Required or body required
    "body": "Message content",          # Required or title required
    "priority": "normal",               # Optional: "normal" or "high"
    "timestamp": "2025-10-08T10:30:00Z", # Optional
    "custom_field": "custom_value"      # Any additional fields
}
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=fastpusher --cov-report=html

# Run specific test
python -m pytest tests/test_pusher.py::TestFastPusher::test_push_success -v
```

## 🔧 Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/javohir/fastpusher.git
cd fastpusher

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest pytest-cov
```

### Running Examples

```bash
python fastpusher/examples.py
```


## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`python -m pytest`)
6. Commit your changes (`git commit -am 'Add new feature'`)
7. Push to the branch (`git push origin feature/new-feature`)
8. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Rustamov Javohir** - [rustamovj366@gmail.com](mailto:rustamovj366@gmail.com)

## 🔗 Links

- [GitHub Repository](https://github.com/fastpusheruz/fastpusher_client)
- [Issue Tracker](https://github.com/fastpusheruz/fastpusher_client/issues)
- [PyPI Package](https://pypi.org/project/fastpusher/)

## 📝 Changelog

### v0.1.0
- Initial release
- Basic push notification functionality
- Bulk messaging support
- Error handling and retry logic
- Connection testing
- Comprehensive test suite

---

**FastPusher** - Send push notifications fast and reliably! 🚀
