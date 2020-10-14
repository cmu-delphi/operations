# `delphi_python`

This image is based on a standard Debian Python environment and includes most
of Delphi's python code. Code is fetched from GitHub and is structured in the
image as a single, monolithic python package named "delphi".

This image also contains the [py3tester](https://github.com/undefx/py3tester)
test runner, which is a thin wrapper around python's built-in unit testing
framework, [`unittest`](https://docs.python.org/3/library/unittest.html). In
addition to test-case pass/fail, py3tester provides line-based coverage and
profiling.

See the [backend development guide](../../../docs/backend_development.md) for
details on how to run code and tests contained in this image.
