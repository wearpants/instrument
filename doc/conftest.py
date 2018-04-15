import pytest
import fakesleep

import instrument
from tests import math_is_hard

@pytest.fixture(autouse=True)
def add_np(doctest_namespace):
    doctest_namespace['instrument'] = instrument
    doctest_namespace['math_is_hard'] = math_is_hard
