import logging
import os
import tempfile

import pytest


def pytest_configure(config):  # noqa: yes config is not used. But it's the pytest hook signature.
    logging.basicConfig(level=logging.DEBUG)
    # let's format the logs output:
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    for handler in logging.getLogger().handlers:
        handler.setFormatter(formatter)


@pytest.fixture()
def reset_environment():
    """
    Fixture to back up env variables before, and restore after. Also, restore Config.settings after.
    WARNING: use it before any test environment variable setting in fixtures.
    """
    old_environ = dict(os.environ)
    yield
    os.environ.clear()
    os.environ.update(old_environ)


def update_settings_with_env(env: dict[str, str]):
    for env_name, env_value in env.items():
        os.environ[env_name] = env_value


@pytest.fixture
def fonctionsaver_in_tempfolder():
    with tempfile.TemporaryDirectory() as temp_folder:
        update_settings_with_env({
            "FUNCTION_SAVER_ALL": "1",
            "FUNCTION_SAVER_INTERNALS_ALL": "1",
            "FUNCTION_SAVER_LOG": "1",
            "FUNCTION_SAVER_ROOT_PATH": temp_folder
        })
        yield temp_folder
