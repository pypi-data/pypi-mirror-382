import pytest
from datetime import datetime
from dataclasses import asdict
from baselog.api.models import LogModel, EventModel, LogLevel, LogModelError, InvalidLogLevelError, MissingMessageError


def test_logmodel_successful_instantiation():
    log = LogModel(level=LogLevel.INFO, message="Test message")
    assert log.level == LogLevel.INFO
    assert log.message == "Test message"
    assert log.category is None
    assert log.tags == []


def test_logmodel_with_optional_fields():
    log = LogModel(
        level=LogLevel.ERROR, message="Test error", category="auth", tags=["tag1", "tag2"]
    )
    assert log.level == LogLevel.ERROR
    assert log.message == "Test error"
    assert log.category == "auth"
    assert log.tags == ["tag1", "tag2"]


def test_logmodel_missing_message():
    with pytest.raises(MissingMessageError, match="Message is required"):
        LogModel(level=LogLevel.INFO, message="")


def test_loglevel_from_string_rejects_invalid():
    with pytest.raises(InvalidLogLevelError):
        LogLevel.from_string("invalid")


def test_logmodel_case_insensitive_level():
    log = LogModel(level=LogLevel.from_string("INFO"), message="Test")
    assert log.level == LogLevel.INFO


def test_logmodel_runtime_string_coercion():
    # Test that strings are automatically converted to LogLevel
    log = LogModel(level="INFO", message="Test")
    assert log.level == LogLevel.INFO
    assert isinstance(log.level, LogLevel)


def test_logmodel_invalid_runtime_string():
    # Test that invalid strings still raise InvalidLogLevelError
    with pytest.raises(InvalidLogLevelError):
        LogModel(level="invalid", message="Test")


def test_logmodel_invalid_non_string_type():
    # Test that non-string, non-LogLevel types raise InvalidLogLevelError
    with pytest.raises(InvalidLogLevelError):
        LogModel(level=123, message="Test")


def test_logmodel_serialization_to_dict():
    log = LogModel(level=LogLevel.INFO, message="Test", category="test_cat", tags=["one"])
    serialized = asdict(log)
    # Since LogLevel is a str-backed enum, it serializes as a string
    expected = {
        "level": "info",
        "message": "Test",
        "category": "test_cat",
        "tags": ["one"],
        "correlation_id": None,
    }
    assert serialized == expected


def test_logmodel_exclude_optionals_none():
    log = LogModel(level=LogLevel.INFO, message="Test")
    serialized = asdict(log)
    assert "category" in serialized  # Includes None
    assert serialized["category"] is None
    assert "tags" in serialized
    assert serialized["tags"] == []


# LogLevel Enum Tests
def test_loglevel_enum_values():
    assert LogLevel.DEBUG.value == "debug"
    assert LogLevel.INFO.value == "info"
    assert LogLevel.WARNING.value == "warning"
    assert LogLevel.ERROR.value == "error"
    assert LogLevel.CRITICAL.value == "critical"


def test_loglevel_from_string_valid():
    assert LogLevel.from_string("debug") == LogLevel.DEBUG
    assert LogLevel.from_string("INFO") == LogLevel.INFO
    assert LogLevel.from_string("Warning") == LogLevel.WARNING
    assert LogLevel.from_string("ERROR") == LogLevel.ERROR
    assert LogLevel.from_string("critical") == LogLevel.CRITICAL


def test_loglevel_from_string_invalid():
    with pytest.raises(InvalidLogLevelError):
        LogLevel.from_string("invalid")

    with pytest.raises(InvalidLogLevelError):
        LogLevel.from_string("unknown")

    with pytest.raises(InvalidLogLevelError):
        LogLevel.from_string("")


def test_loglevel_serialization_value():
    assert LogLevel.INFO.value == "info"
    assert LogLevel.ERROR.value == "error"


def test_loglevel_enum_membership():
    assert LogLevel.DEBUG in LogLevel
    assert LogLevel.INFO in LogLevel
    assert LogLevel.WARNING in LogLevel
    assert LogLevel.ERROR in LogLevel
    assert LogLevel.CRITICAL in LogLevel


def test_loglevel_string_semantics():
    # Test that LogLevel behaves like a string
    level = LogLevel.INFO
    assert str(level.value) == "info"
    assert level.value == "info"
    assert level.value != "debug"
    assert level.value.upper() == "INFO"
    assert level.value.lower() == "info"
    assert len(level.value) == 4


# Custom Exception Tests
def test_invalid_log_level_error_attributes():
    """Test InvalidLogLevelError stores and provides relevant information"""
    error = InvalidLogLevelError("invalid", ["debug", "info", "error"])
    assert error.level == "invalid"
    assert error.valid_levels == ["debug", "info", "error"]
    assert "Invalid log level: 'invalid'" in str(error)


def test_missing_message_error_attributes():
    """Test MissingMessageError has correct message"""
    error = MissingMessageError()
    assert str(error) == "Message is required for LogModel"


def test_exception_hierarchy():
    """Test that custom exceptions inherit correctly"""
    assert issubclass(InvalidLogLevelError, LogModelError)
    assert issubclass(MissingMessageError, LogModelError)
    assert not issubclass(InvalidLogLevelError, MissingMessageError)
    assert not issubclass(MissingMessageError, InvalidLogLevelError)


def test_logmodel_raises_base_exception():
    """Test that LogModel errors can be caught as base LogModelError"""
    # Test missing message as base exception
    with pytest.raises(LogModelError):
        LogModel(level=LogLevel.INFO, message="")

    # Test invalid level as base exception
    with pytest.raises(LogModelError):
        LogModel(level="invalid", message="test")


def test_loglevel_from_string_raises_correct_exception():
    """Test LogLevel.from_string raises InvalidLogLevelError"""
    with pytest.raises(InvalidLogLevelError) as exc_info:
        LogLevel.from_string("invalid")

    assert exc_info.value.level == "invalid"
    assert "debug" in exc_info.value.valid_levels
    assert "info" in exc_info.value.valid_levels


def test_eventmodel_successful_instantiation():
    timestamp = datetime.now()
    event = EventModel(
        event_type="user_login",
        payload={"user_id": 123},
        timestamp=timestamp,
        source_service="web",
    )
    assert event.event_type == "user_login"
    assert event.payload == {"user_id": 123}
    assert event.timestamp == timestamp
    assert event.source_service == "web"
    assert event.user_id is None
    assert event.correlation_id is None


def test_eventmodel_with_optionals():
    event = EventModel(
        event_type="user_login",
        payload={"user_id": 123},
        timestamp=datetime.now(),
        source_service="web",
        user_id="user456",
        correlation_id="corr789",
    )
    assert event.user_id == "user456"
    assert event.correlation_id == "corr789"


def test_eventmodel_missing_event_type():
    with pytest.raises(ValueError, match="Event type is required"):
        EventModel(
            event_type="",
            payload={"test": "data"},
            timestamp=datetime.now(),
            source_service="test",
        )


def test_eventmodel_empty_payload():
    with pytest.raises(ValueError, match="Payload is required"):
        EventModel(
            event_type="test_event",
            payload={},
            timestamp=datetime.now(),
            source_service="test",
        )


def test_eventmodel_serialization_to_dict():
    timestamp = datetime.now()
    event = EventModel(
        event_type="test_event",
        payload={"key": "value"},
        timestamp=timestamp,
        source_service="test_service",
    )
    expected = {
        "event_type": "test_event",
        "payload": {"key": "value"},
        "timestamp": timestamp,
        "source_service": "test_service",
        "user_id": None,
        "correlation_id": None,
    }
    assert asdict(event) == expected
