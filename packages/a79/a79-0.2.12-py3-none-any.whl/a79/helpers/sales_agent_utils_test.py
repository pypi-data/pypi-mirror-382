"""Tests for sales_agent_utils module."""

from .sales_agent_utils import find_best_transcript_message


class TestFindBestTranscriptMessage:
    """Test cases for find_best_transcript_message function."""

    def test_find_exact_match(self):
        """Test finding an exact match in transcript messages."""
        transcript_messages = [
            {"speaker": "Agent", "message": "Hello, how can I help you today?"},
            {"speaker": "Customer", "message": "I need help with my order"},
            {"speaker": "Agent", "message": "I'd be happy to assist you"},
        ]

        result = find_best_transcript_message(
            "I need help with my order", transcript_messages
        )

        assert result is not None
        assert result["message"] == "I need help with my order"
        assert result["speaker"] == "Customer"

    def test_find_partial_match(self):
        """Test finding a partial match in transcript messages."""
        transcript_messages = [
            {
                "speaker": "Agent",
                "message": "Welcome to our service, how may I assist you today?",
            },
            {"speaker": "Customer", "message": "I have a problem with my account"},
        ]

        result = find_best_transcript_message("assist you", transcript_messages)

        assert result is not None
        assert "assist you" in result["message"].lower()

    def test_no_match_below_threshold(self):
        """Test that no match is returned when similarity is below threshold."""
        transcript_messages = [
            {"speaker": "Agent", "message": "Hello there"},
            {"speaker": "Customer", "message": "Goodbye"},
        ]

        result = find_best_transcript_message(
            "This is completely different text", transcript_messages
        )

        assert result is None

    def test_handle_none_message(self):
        """Test that None messages are handled gracefully."""
        transcript_messages = [
            {"speaker": "Agent", "message": None},
            {"speaker": "Customer", "message": "Valid message"},
            {"speaker": "Agent", "message": None},
        ]

        result = find_best_transcript_message("Valid message", transcript_messages)

        assert result is not None
        assert result["message"] == "Valid message"

    def test_handle_missing_message_key(self):
        """Test that messages without 'message' key are skipped."""
        transcript_messages = [
            {"speaker": "Agent"},  # Missing 'message' key
            {"speaker": "Customer", "message": "Hello world"},
            {"text": "Some text"},  # Different key name
        ]

        result = find_best_transcript_message("Hello world", transcript_messages)

        assert result is not None
        assert result["message"] == "Hello world"

    def test_handle_non_dict_messages(self):
        """Test that non-dict messages are skipped."""
        transcript_messages = [
            "Just a string",
            None,
            {"speaker": "Agent", "message": "Real message"},
            123,
            ["list", "item"],
        ]

        result = find_best_transcript_message("Real message", transcript_messages)

        assert result is not None
        assert result["message"] == "Real message"

    def test_empty_transcript_messages(self):
        """Test handling of empty transcript messages list."""
        result = find_best_transcript_message("Any quote", [])
        assert result is None

    def test_case_insensitive_matching(self):
        """Test that matching is case-insensitive."""
        transcript_messages = [
            {"speaker": "Agent", "message": "HELLO THERE"},
            {"speaker": "Customer", "message": "Good Morning"},
        ]

        result = find_best_transcript_message("hello there", transcript_messages)

        assert result is not None
        assert result["message"] == "HELLO THERE"

    def test_whitespace_handling(self):
        """Test that leading/trailing whitespace is handled."""
        transcript_messages = [
            {"speaker": "Agent", "message": "  Hello with spaces  "},
            {"speaker": "Customer", "message": "No extra spaces"},
        ]

        result = find_best_transcript_message("Hello with spaces", transcript_messages)

        assert result is not None
        assert "Hello with spaces" in result["message"]

    def test_best_match_selection(self):
        """Test that the best match is selected when multiple candidates exist."""
        transcript_messages = [
            {"speaker": "Agent", "message": "Can I help you?"},
            {"speaker": "Customer", "message": "I need help with my order today"},
            {"speaker": "Agent", "message": "I need help"},
        ]

        result = find_best_transcript_message("I need help", transcript_messages)

        assert result is not None
        # Should match the exact "I need help" message
        assert result["message"] == "I need help"

    def test_error_resilience_with_unexpected_data(self):
        """Test that function handles unexpected data gracefully."""
        transcript_messages = [
            {"speaker": "Agent", "message": "Normal message"},
            {"speaker": "Bot", "message": None},  # None message
            {"speaker": "System"},  # Missing message key
            "Invalid entry",  # Non-dict entry
            {"speaker": "Customer", "message": "Target message"},
        ]

        # Should not raise an exception and find the target
        result = find_best_transcript_message("Target message", transcript_messages)

        assert result is not None
        assert result["message"] == "Target message"

    def test_quote_with_special_characters(self):
        """Test matching quotes with special characters."""
        transcript_messages = [
            {"speaker": "Agent", "message": "Hello! How's everything?"},
            {"speaker": "Customer", "message": "I'm doing well, thank you!"},
        ]

        result = find_best_transcript_message("How's everything?", transcript_messages)

        assert result is not None
        assert "How's everything?" in result["message"]
