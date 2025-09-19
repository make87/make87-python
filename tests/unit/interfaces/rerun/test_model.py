import pytest
from pydantic import ValidationError

from make87.interfaces.rerun.model import (
    ChunkBatcherConfig,
    PlaybackBehavior,
    RerunGRpcClientConfig,
    RerunGRpcServerConfig,
)


class TestChunkBatcherConfig:
    """Test suite for ChunkBatcherConfig model."""

    def test_default_values(self):
        """Test default values are correctly set."""
        config = ChunkBatcherConfig()

        assert config.flush_tick == 0.2
        assert config.flush_num_bytes == 1048576  # 1MiB
        assert config.flush_num_rows == 18446744073709551615  # u64::MAX

    def test_custom_values(self):
        """Test custom values can be set."""
        config = ChunkBatcherConfig(
            flush_tick=0.5,
            flush_num_bytes=2097152,  # 2MiB
            flush_num_rows=1000,
        )

        assert config.flush_tick == 0.5
        assert config.flush_num_bytes == 2097152
        assert config.flush_num_rows == 1000

    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {
            "flush_tick": 0.1,
            "flush_num_bytes": 512000,
            "flush_num_rows": 500,
        }
        config = ChunkBatcherConfig(**data)

        assert config.flush_tick == 0.1
        assert config.flush_num_bytes == 512000
        assert config.flush_num_rows == 500

    def test_validation_errors(self):
        """Test validation errors for invalid values."""
        with pytest.raises(ValidationError):
            ChunkBatcherConfig(flush_tick="invalid")

        with pytest.raises(ValidationError):
            ChunkBatcherConfig(flush_num_bytes="invalid")

        with pytest.raises(ValidationError):
            ChunkBatcherConfig(flush_num_rows="invalid")

    def test_negative_values(self):
        """Test that negative values are handled."""
        # Note: Depending on your validation requirements, you might want to
        # add validators to prevent negative values
        config = ChunkBatcherConfig(
            flush_tick=-0.1,
            flush_num_bytes=-1000,
            flush_num_rows=-100,
        )

        # Currently these are allowed, but you might want to add validation
        assert config.flush_tick == -0.1
        assert config.flush_num_bytes == -1000
        assert config.flush_num_rows == -100


class TestRerunGRpcClientConfig:
    """Test suite for RerunGRpcClientConfig model."""

    def test_default_values(self):
        """Test default values are correctly set."""
        config = RerunGRpcClientConfig()

        assert isinstance(config.batcher_config, ChunkBatcherConfig)

    def test_custom_values(self):
        """Test custom values can be set."""
        custom_batcher = ChunkBatcherConfig(
            flush_tick=0.5,
            flush_num_bytes=2097152,
            flush_num_rows=1000,
        )

        config = RerunGRpcClientConfig(
            batcher_config=custom_batcher,
        )

        assert config.batcher_config == custom_batcher

    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {
            "batcher_config": {
                "flush_tick": 0.3,
                "flush_num_bytes": 1500000,
                "flush_num_rows": 2000,
            },
        }
        config = RerunGRpcClientConfig(**data)

        assert config.batcher_config.flush_tick == 0.3
        assert config.batcher_config.flush_num_bytes == 1500000
        assert config.batcher_config.flush_num_rows == 2000

    def test_nested_default_batcher(self):
        """Test that nested batcher config uses defaults when not specified."""
        config = RerunGRpcClientConfig()

        # Batcher config should use defaults
        assert config.batcher_config.flush_tick == 0.2
        assert config.batcher_config.flush_num_bytes == 1048576
        assert config.batcher_config.flush_num_rows == 18446744073709551615


class TestRerunGRpcServerConfig:
    """Test suite for RerunGRpcServerConfig model."""

    def test_default_values(self):
        """Test default values are correctly set."""
        config = RerunGRpcServerConfig()

        assert config.memory_limit is None
        assert config.playback_behavior == PlaybackBehavior.OLDEST_FIRST

    def test_custom_values(self):
        """Test custom values can be set."""
        config = RerunGRpcServerConfig(
            memory_limit=1073741824,  # 1GB
            playback_behavior=PlaybackBehavior.NEWEST_FIRST,
        )

        assert config.memory_limit == 1073741824
        assert config.playback_behavior == PlaybackBehavior.NEWEST_FIRST

    def test_none_memory_limit(self):
        """Test that memory_limit can be None (no limit)."""
        config = RerunGRpcServerConfig(memory_limit=None)

        assert config.memory_limit is None

    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {
            "memory_limit": 2147483648,  # 2GB
            "playback_behavior": "NewestFirst",
        }
        config = RerunGRpcServerConfig(**data)

        assert config.memory_limit == 2147483648
        assert config.playback_behavior == PlaybackBehavior.NEWEST_FIRST

    def test_large_values(self):
        """Test large memory values."""
        large_value = 1099511627776  # 1TB
        config = RerunGRpcServerConfig(memory_limit=large_value)

        assert config.memory_limit == large_value

    def test_zero_memory_limit(self):
        """Test zero memory_limit value."""
        config = RerunGRpcServerConfig(memory_limit=0)

        assert config.memory_limit == 0

    def test_validation_errors(self):
        """Test validation errors for invalid values."""
        with pytest.raises(ValidationError):
            RerunGRpcServerConfig(memory_limit="invalid")

        with pytest.raises(ValidationError):
            RerunGRpcServerConfig(playback_behavior="invalid")

    def test_negative_memory_limit(self):
        """Test negative memory_limit value."""
        # Note: You might want to add validation to prevent negative values
        config = RerunGRpcServerConfig(memory_limit=-1000)

        # Currently allowed, but you might want to add validation
        assert config.memory_limit == -1000


class TestPlaybackBehavior:
    """Test suite for PlaybackBehavior enum."""

    def test_enum_values(self):
        """Test enum values are correctly defined."""
        assert PlaybackBehavior.OLDEST_FIRST.value == "OldestFirst"
        assert PlaybackBehavior.NEWEST_FIRST.value == "NewestFirst"

    def test_string_coercion(self):
        """Test that string values are correctly coerced."""
        assert PlaybackBehavior("OldestFirst") == PlaybackBehavior.OLDEST_FIRST
        assert PlaybackBehavior("NewestFirst") == PlaybackBehavior.NEWEST_FIRST

    def test_default_behavior(self):
        """Test default playback behavior in server config."""
        config = RerunGRpcServerConfig()
        assert config.playback_behavior == PlaybackBehavior.OLDEST_FIRST

    def test_invalid_value(self):
        """Test invalid enum values raise errors."""
        with pytest.raises(ValueError):
            PlaybackBehavior("InvalidValue")


class TestModelSerialization:
    """Test suite for model serialization and deserialization."""

    def test_chunk_batcher_config_serialization(self):
        """Test ChunkBatcherConfig serialization."""
        config = ChunkBatcherConfig(
            flush_tick=0.3,
            flush_num_bytes=2048000,
            flush_num_rows=5000,
        )

        # Test JSON serialization
        json_data = config.model_dump()
        assert json_data["flush_tick"] == 0.3
        assert json_data["flush_num_bytes"] == 2048000
        assert json_data["flush_num_rows"] == 5000

        # Test deserialization
        restored_config = ChunkBatcherConfig(**json_data)
        assert restored_config == config

    def test_client_config_serialization(self):
        """Test RerunGRpcClientConfig serialization."""
        config = RerunGRpcClientConfig(
            batcher_config=ChunkBatcherConfig(flush_tick=0.4),
        )

        # Test JSON serialization
        json_data = config.model_dump()
        assert json_data["batcher_config"]["flush_tick"] == 0.4

        # Test deserialization
        restored_config = RerunGRpcClientConfig(**json_data)
        assert restored_config.batcher_config.flush_tick == config.batcher_config.flush_tick

    def test_server_config_serialization(self):
        """Test RerunGRpcServerConfig serialization."""
        config = RerunGRpcServerConfig(
            memory_limit=1073741824,
            playback_behavior=PlaybackBehavior.NEWEST_FIRST,
        )

        # Test JSON serialization
        json_data = config.model_dump()
        assert json_data["memory_limit"] == 1073741824
        assert json_data["playback_behavior"] == "NewestFirst"

        # Test deserialization
        restored_config = RerunGRpcServerConfig(**json_data)
        assert restored_config == config

    def test_model_validate_usage(self):
        """Test using model_validate as used in the interface."""
        # Test client config validation (as used in interface)
        client_data = {
            "batcher_config": {
                "flush_tick": 0.5,
                "flush_num_bytes": 2048576,
                "flush_num_rows": 1000,
            }
        }

        config = RerunGRpcClientConfig.model_validate(client_data)
        assert config.batcher_config.flush_tick == 0.5

        # Test server config validation (as used in interface)
        server_data = {
            "memory_limit": 1073741824,
            "playback_behavior": "OldestFirst",
        }

        config = RerunGRpcServerConfig.model_validate(server_data)
        assert config.memory_limit == 1073741824
        assert config.playback_behavior == PlaybackBehavior.OLDEST_FIRST
