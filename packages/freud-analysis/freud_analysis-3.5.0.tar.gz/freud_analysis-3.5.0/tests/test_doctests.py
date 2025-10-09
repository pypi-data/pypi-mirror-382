# Copyright (c) 2010-2025 The Regents of the University of Michigan
# This file is from the freud project, released under the BSD 3-Clause License.

import doctest
import inspect

import pytest

import freud


def fetch_doctests():
    finder = doctest.DocTestFinder()
    for _name, member in inspect.getmembers(freud):
        if inspect.ismodule(member):
            for docstring in finder.find(member):
                if docstring.examples:
                    yield docstring


class TestDoctests:
    @pytest.mark.parametrize(
        "docstring", fetch_doctests(), ids=lambda docstring: docstring.name
    )
    def test_docstring(self, docstring):
        optionflags = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE
        runner = doctest.DocTestRunner(optionflags=optionflags)
        runner.run(docstring)
        results = runner.summarize()
        if results.failed:
            raise AssertionError(results)
