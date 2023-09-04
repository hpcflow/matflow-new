import pytest
import matflow as mf


def pytest_configure(config):
    mf.run_time_info.in_pytest = True


def pytest_unconfigure(config):
    mf.run_time_info.in_pytest = False


@pytest.fixture
def null_config(tmp_path):
    if not mf.is_config_loaded:
        mf.load_config(config_dir=tmp_path)
    mf.run_time_info.in_pytest = True
