# full_match

[![Downloads](https://static.pepy.tech/badge/full_match/month)](https://pepy.tech/project/full_match)
[![Downloads](https://static.pepy.tech/badge/full_match)](https://pepy.tech/project/full_match)
[![Coverage Status](https://coveralls.io/repos/github/pomponchik/full_match/badge.svg?branch=main)](https://coveralls.io/github/pomponchik/full_match?branch=main)
[![Lines of code](https://sloc.xyz/github/pomponchik/full_match/?category=code)](https://github.com/boyter/scc/)
[![Hits-of-Code](https://hitsofcode.com/github/pomponchik/full_match?branch=main)](https://hitsofcode.com/github/pomponchik/full_match/view?branch=main)
[![Test-Package](https://github.com/pomponchik/full_match/actions/workflows/tests_and_coverage.yml/badge.svg)](https://github.com/pomponchik/full_match/actions/workflows/tests_and_coverage.yml)
[![Python versions](https://img.shields.io/pypi/pyversions/full_match.svg)](https://pypi.python.org/pypi/full_match)
[![PyPI version](https://badge.fury.io/py/full_match.svg)](https://badge.fury.io/py/full_match)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)


When catching exceptions in [`Pytest`](https://docs.pytest.org/en/latest/), sometimes you need to check messages. Since the user sends a pattern for searching, and not a message for exact matching, sometimes similar, but not identical messages pass through the filter. This micro-library contains a function that makes `Pytest` check exception messages accurately.

It may also be useful to you if you use mutation testing tools such as [mutmut](https://github.com/boxed/mutmut).

Install it:

```bash
pip install full_match
```

And use:

```python
import pytest
from full_match import match

def test_something():
  with pytest.raises(AssertionError, match='Regex pattern did not match.'):
    with pytest.raises(ValueError, match=match('Some message.')):
      raise ValueError('XXSome message.XX')
```

The message in the inner `with` block does not match the pattern exactly, so an `AssertionError` exception will occur in this example.
