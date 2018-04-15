import pytest
import fakesleep

from instrument import measure_iter
from tests import math_is_hard

@pytest.fixture(autouse=True)
def add_np(doctest_namespace):
    doctest_namespace['measure_iter'] = measure_iter
    doctest_namespace['math_is_hard'] = math_is_hard
