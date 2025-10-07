def test_red(pytester):
    """
    Should have red in failure.
    """
    pytester.copy_example("examples/test_example_simple.py")
    result = pytester.runpytest("--color=yes")
    result.assert_outcomes(failed=1, passed=1)
    result.stdout.fnmatch_lines(
        [
            "*[31mFAILURE:*[0massert*",
            "*[31mtest_example_simple.py*[0m:14 in test_fail*",
            "*[31mAssertionError: assert 1 == 2*",
            "*[0m*"
        ],
    )


def test_no_red(pytester):
    """
    Should NOT have red in failure.
    """
    pytester.copy_example("examples/test_example_simple.py")
    result = pytester.runpytest("--color=no")
    result.assert_outcomes(failed=1, passed=1)
    result.stdout.fnmatch_lines(
        [
            "*FAILURE: assert*",  # no red before assert
        ],
    )
    result.stdout.no_fnmatch_line("*[31m*")  # no red anywhere
    result.stdout.no_fnmatch_line("*[0m*")  # no reset anywhere
