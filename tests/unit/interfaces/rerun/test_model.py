import pytest
from pydantic import ValidationError

from make87.interfaces.rerun.model import (
    ChunkBatcherConfig,
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

        assert config.max_bytes is None

    def test_custom_values(self):
        """Test custom values can be set."""
        config = RerunGRpcServerConfig(max_bytes=1073741824)  # 1GB

        assert config.max_bytes == 1073741824

    def test_none_max_bytes(self):
        """Test that max_bytes can be None (no limit)."""
        config = RerunGRpcServerConfig(max_bytes=None)

        assert config.max_bytes is None

    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {"max_bytes": 2147483648}  # 2GB
        config = RerunGRpcServerConfig(**data)

        assert config.max_bytes == 2147483648

    def test_large_values(self):
        """Test large memory values."""
        large_value = 1099511627776  # 1TB
        config = RerunGRpcServerConfig(max_bytes=large_value)

        assert config.max_bytes == large_value

    def test_zero_max_bytes(self):
        """Test zero max_bytes value."""
        config = RerunGRpcServerConfig(max_bytes=0)

        assert config.max_bytes == 0

    def test_validation_errors(self):
        """Test validation errors for invalid values."""
        with pytest.raises(ValidationError):
            RerunGRpcServerConfig(max_bytes="invalid")

    def test_negative_max_bytes(self):
        """Test negative max_bytes value."""
        # Note: You might want to add validation to prevent negative values
        config = RerunGRpcServerConfig(max_bytes=-1000)

        # Currently allowed, but you might want to add validation
        assert config.max_bytes == -1000


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
        config = RerunGRpcServerConfig(max_bytes=1073741824)

        # Test JSON serialization
        json_data = config.model_dump()
        assert json_data["max_bytes"] == 1073741824

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
        server_data = {"max_bytes": 1073741824}

        config = RerunGRpcServerConfig.model_validate(server_data)
        assert config.max_bytes == 1073741824
