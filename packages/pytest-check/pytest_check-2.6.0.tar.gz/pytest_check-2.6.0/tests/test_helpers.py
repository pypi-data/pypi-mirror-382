import sys

import pytest


# the output is different in prior versions.
@pytest.mark.skipif(sys.version_info < (3, 10), reason="requires python3.10 or higher")
def test_sequence_with_helper_funcs(pytester):
    """
    Should show a sequence of calls
    """
    pytester.copy_example("examples/test_example_helpers.py")
    result = pytester.runpytest("--check-max-tb=2")
    result.assert_outcomes(failed=1, passed=0)
    result.stdout.fnmatch_lines(
        [
            "*FAILURE: assert 1 == 0, first",
            "*in test_func() -> helper1()",
            "*in helper1() -> helper2()",
            "*in helper2() -> with check(\"first\"):",
            "*in helper2 -> assert 1 == 0",
            "*AssertionError: assert 1 == 0",


            "*FAILURE: assert 1 > 2, second",
            "*in test_func() -> helper1()",
            "*in helper1() -> helper2()",
            "*in helper2() -> with check(\"second\"):",
            "*in helper2 -> assert 1 > 2",
            "*AssertionError: assert 1 > 2"
        ],
    )

