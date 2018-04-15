import pytest
import fakesleep


@pytest.fixture(autouse=True)
def auto_fakesleep():
    fakesleep.monkey_patch()
    yield
    fakesleep.monkey_restore()
