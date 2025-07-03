import os
import tempfile
import pytest

from make87.config import load_config_from_json, get_config_value


class DummyAppConfig:
    def __init__(self, config):
        self.config = config


def test_secret_resolution(monkeypatch):
    # Create a temporary secret file
    with tempfile.TemporaryDirectory() as tmpdir:
        secret_name = "MYSECRET"
        secret_value = "supersecret"
        secret_file = os.path.join(tmpdir, f"{secret_name}.secret")
        with open(secret_file, "w") as f:
            f.write(secret_value)

        # Patch open to redirect /run/secrets/MYSECRET.secret to our temp file
        import builtins

        real_open = builtins.open

        def fake_open(path, *args, **kwargs):
            if path == f"/run/secrets/{secret_name}.secret":
                return real_open(secret_file, *args, **kwargs)
            return real_open(path, *args, **kwargs)

        monkeypatch.setattr("builtins.open", fake_open)

        # Provide all required fields for ApplicationConfig
        config_dict = {
            "application_info": {
                "application_id": "app-id",
                "application_name": "dummy",
                "deployed_application_id": "deploy-id",
                "deployed_application_name": "dummy-deploy",
                "is_release_version": False,
                "name": "dummy",  # legacy/extra, ignored if not in model
                "system_id": "sys-id",
                "version": "1.0",
            },
            "interfaces": {},
            "peripherals": {"peripherals": []},
            "config": {"password": "{{ secret.MYSECRET }}"},
        }
        config = load_config_from_json(config_dict)
        assert config.config["password"] == secret_value


@pytest.mark.parametrize(
    "pattern",
    [
        "{{secret.MYSECRET}}",
        "{{ secret.MYSECRET}}",
        "{{secret.MYSECRET }}",
        "{{  secret.MYSECRET  }}",
        "{{    secret.MYSECRET}}",
        "{{secret.MYSECRET    }}",
        "{{    secret.MYSECRET    }}",
        "   {{secret.MYSECRET}}   ",
        "\t{{ secret.MYSECRET }}\n",
    ],
)
def test_secret_resolution_whitespace(monkeypatch, pattern):
    with tempfile.TemporaryDirectory() as tmpdir:
        secret_name = "MYSECRET"
        secret_value = "supersecret"
        secret_file = os.path.join(tmpdir, f"{secret_name}.secret")
        with open(secret_file, "w") as f:
            f.write(secret_value)

        import builtins

        real_open = builtins.open

        def fake_open(path, *args, **kwargs):
            if path == f"/run/secrets/{secret_name}.secret":
                return real_open(secret_file, *args, **kwargs)
            return real_open(path, *args, **kwargs)

        monkeypatch.setattr("builtins.open", fake_open)

        config_dict = {
            "application_info": {
                "application_id": "app-id",
                "application_name": "dummy",
                "deployed_application_id": "deploy-id",
                "deployed_application_name": "dummy-deploy",
                "is_release_version": False,
                "name": "dummy",
                "system_id": "sys-id",
                "version": "1.0",
            },
            "interfaces": {},
            "peripherals": {"peripherals": []},
            "config": {"password": pattern},
        }
        config = load_config_from_json(config_dict)
        assert config.config["password"] == secret_value


def test_get_config_value():
    config = DummyAppConfig({"foo": 123, "bar": "baz"})
    assert get_config_value(config, "foo") == 123
    assert get_config_value(config, "bar") == "baz"
    assert get_config_value(config, "missing", default="x") == "x"
    with pytest.raises(KeyError):
        get_config_value(config, "missing2")
