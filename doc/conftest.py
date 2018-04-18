def monkeypatch_pytest():
    """monkeypatch pytest to capture logging output in doctests"""

    import logging
    import sys
    import _pytest.doctest
    _original_init_runner_class = _pytest.doctest._init_runner_class

    def _my_init_runner_class():
        # hack to wire doctest's stdout capture to logging
        # via https://stackoverflow.com/a/22301726
        cls = _original_init_runner_class()

        class MyPytestDoctestRunner(cls):
            def run(self, test, compileflags=None, out=None, clear_globs=True):
                if out is None:
                    handler = None
                else:
                    handler = logging.StreamHandler(self._fakeout)
                    fmt = logging.Formatter(fmt=logging.BASIC_FORMAT)
                    handler.setFormatter(fmt)
                    out = sys.stdout.write

                root = logging.getLogger()
                root.setLevel(logging.DEBUG)

                if handler:
                    root.addHandler(handler)
                try:
                    super().run(test, compileflags, out, clear_globs)
                finally:
                    if handler:
                        root.removeHandler(handler)
                        handler.close()

        return MyPytestDoctestRunner

    _pytest.doctest._init_runner_class = _my_init_runner_class

monkeypatch_pytest()

import pytest

import instrument
from tests import math_is_hard

@pytest.fixture(autouse=True)
def add_np(doctest_namespace):
    doctest_namespace['instrument'] = instrument
    doctest_namespace['math_is_hard'] = math_is_hard
