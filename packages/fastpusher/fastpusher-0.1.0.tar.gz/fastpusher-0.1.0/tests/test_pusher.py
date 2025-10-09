"""
Unit tests for FastPusher library
"""

import unittest
from unittest.mock import Mock, patch

import requests

from fastpusher import (
    AuthenticationError,
    ConnectionError,
    FastPusher,
    RateLimitError,
    ValidationError,
)


class TestFastPusher(unittest.TestCase):
    def setUp(self):
        """Setup that runs before each test"""
        self.pusher = FastPusher(
            url="http://test.example.com",
            token="test_token",
            timeout=10,
            retry_attempts=2,
            debug=False,
        )

    def tearDown(self):
        """Cleanup that runs after each test"""
        self.pusher.close()

    def test_init(self):
        """Test FastPusher object creation"""
        self.assertEqual(self.pusher.url, "http://test.example.com")
        self.assertEqual(self.pusher.token, "test_token")
        self.assertEqual(self.pusher.timeout, 10)
        self.assertEqual(self.pusher.retry_attempts, 2)

    def test_validate_input_valid(self):
        """Test valid input data"""
        try:
            self.pusher._validate_input("test_channel", {"title": "Test"})
        except ValidationError:
            self.fail("ValidationError raised for valid input")

    def test_validate_input_empty_channel(self):
        """Test empty channel name"""
        with self.assertRaises(ValidationError):
            self.pusher._validate_input("", {"title": "Test"})

    def test_validate_input_none_channel(self):
        """Test None channel name"""
        with self.assertRaises(ValidationError):
            self.pusher._validate_input(None, {"title": "Test"})

    def test_validate_input_empty_data(self):
        """Test empty data"""
        with self.assertRaises(ValidationError):
            self.pusher._validate_input("test_channel", {})

    def test_validate_input_none_data(self):
        """Test None data"""
        with self.assertRaises(ValidationError):
            self.pusher._validate_input("test_channel", None)

    @patch("requests.Session.post")
    def test_push_success(self, mock_post):
        """Test successful message sending"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "message_id": "123"}
        mock_post.return_value = mock_response

        result = self.pusher.push("test_channel", {"title": "Test", "body": "Message"})

        self.assertEqual(result["success"], True)
        self.assertEqual(result["message_id"], "123")
        mock_post.assert_called_once()

        # Check the payload structure
        call_args = mock_post.call_args
        payload = call_args.kwargs["json"]
        self.assertEqual(payload["client_id"], "test_channel")
        self.assertEqual(payload["data"]["title"], "Test")
        self.assertEqual(payload["data"]["body"], "Message")

    @patch("requests.Session.post")
    def test_push_authentication_error(self, mock_post):
        """Test authentication error"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response

        with self.assertRaises(AuthenticationError) as context:
            self.pusher.push("test_channel", {"title": "Test"})

        self.assertIn("Token is invalid or expired", str(context.exception))

    @patch("requests.Session.post")
    def test_push_rate_limit_error(self, mock_post):
        """Test rate limit error"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_post.return_value = mock_response

        with self.assertRaises(RateLimitError):
            self.pusher.push("test_channel", {"title": "Test"})

    @patch("requests.Session.post")
    def test_push_server_error(self, mock_post):
        """Test server error"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        with self.assertRaises(ConnectionError):
            self.pusher.push("test_channel", {"title": "Test"})

    @patch("requests.Session.post")
    def test_push_retry_logic(self, mock_post):
        """Test retry logic"""
        # First 2 attempts timeout, 3rd succeeds
        mock_post.side_effect = [
            requests.exceptions.Timeout(),
            requests.exceptions.Timeout(),
            Mock(
                status_code=200,
                json=lambda: {"success": True, "message_id": "retry_success"},
            ),
        ]

        result = self.pusher.push("test_channel", {"title": "Test"})

        self.assertEqual(result["success"], True)
        self.assertEqual(result["message_id"], "retry_success")
        self.assertEqual(mock_post.call_count, 3)

    @patch("requests.Session.post")
    def test_push_retry_exhausted(self, mock_post):
        """Test retry logic when all attempts fail"""
        mock_post.side_effect = requests.exceptions.Timeout()

        with self.assertRaises(requests.exceptions.Timeout):
            self.pusher.push("test_channel", {"title": "Test"})

        # Should retry retry_attempts + 1 times (3 total for retry_attempts=2)
        self.assertEqual(mock_post.call_count, 3)

    def test_push_bulk_success(self):
        """Test bulk sending to multiple channels"""
        with patch.object(self.pusher, "push") as mock_push:
            mock_push.return_value = {"success": True, "message_id": "bulk_test"}

            channels = ["channel1", "channel2", "channel3"]
            results = self.pusher.push_bulk(channels, {"title": "Test"})

            self.assertEqual(len(results), 3)
            self.assertEqual(mock_push.call_count, 3)

            for result in results:
                self.assertTrue(result["success"])
                self.assertEqual(result["result"]["message_id"], "bulk_test")
                self.assertIsNone(result["error"])

    def test_push_bulk_mixed_results(self):
        """Test bulk sending with mixed results"""

        def mock_push_side_effect(channel, data):
            if channel == "bad_channel":
                raise ValidationError("Bad channel")
            return {"success": True, "message_id": f"msg_{channel}"}

        with patch.object(self.pusher, "push", side_effect=mock_push_side_effect):
            channels = ["good_channel", "bad_channel", "another_good_channel"]
            results = self.pusher.push_bulk(channels, {"title": "Test"})

            self.assertEqual(len(results), 3)
            self.assertTrue(results[0]["success"])
            self.assertFalse(results[1]["success"])
            self.assertTrue(results[2]["success"])

            self.assertEqual(results[1]["error"], "Bad channel")

    def test_push_bulk_empty_channels(self):
        """Test bulk sending with empty channel list"""
        with self.assertRaises(ValidationError) as context:
            self.pusher.push_bulk([], {"title": "Test"})

        self.assertIn("Channel list is empty", str(context.exception))

    @patch("requests.Session.get")
    def test_test_connection_success(self, mock_get):
        """Test successful connection test"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = self.pusher.test_connection()
        self.assertTrue(result)

        # Check the URL called
        mock_get.assert_called_once_with(
            "http://test.example.com/api/health", timeout=10
        )

    @patch("requests.Session.get")
    def test_test_connection_failure(self, mock_get):
        """Test failed connection test"""
        mock_get.side_effect = requests.exceptions.RequestException()

        result = self.pusher.test_connection()
        self.assertFalse(result)

    @patch("requests.Session.get")
    def test_test_connection_wrong_status(self, mock_get):
        """Test connection test with wrong status code"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = self.pusher.test_connection()
        self.assertFalse(result)

    def test_close_session(self):
        """Test session closing"""
        with patch.object(self.pusher.session, "close") as mock_close:
            self.pusher.close()
            mock_close.assert_called_once()


class TestIntegration(unittest.TestCase):
    """Integration tests"""

    def test_full_workflow(self):
        """Test complete workflow"""
        pusher = FastPusher(url="http://test.example.com", token="test_token")

        with patch("requests.Session.post") as mock_post, patch(
            "requests.Session.get"
        ) as mock_get:
            # Test connection
            mock_get.return_value = Mock(status_code=200)
            self.assertTrue(pusher.test_connection())

            # Send single message
            mock_post.return_value = Mock(
                status_code=200,
                json=lambda: {"success": True, "message_id": "integration_123"},
            )

            result = pusher.push(
                "test_channel",
                {"title": "Integration Test", "body": "This is a test message"},
            )

            self.assertEqual(result["success"], True)
            self.assertEqual(result["message_id"], "integration_123")

        pusher.close()

    def test_error_workflow(self):
        """Test error handling workflow"""
        pusher = FastPusher(url="http://test.example.com", token="invalid_token")

        with patch("requests.Session.post") as mock_post:
            # Simulate authentication error
            mock_post.return_value = Mock(status_code=401)

            with self.assertRaises(AuthenticationError):
                pusher.push("test_channel", {"title": "Test"})

        pusher.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
