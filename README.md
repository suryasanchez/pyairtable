# pyAirtable (formerly airtable-python-wrapper)

![CI](https://github.com/gtalarico/pyairtable/actions/workflows/test_lint_deploy.yml/badge.svg)
[![PyPI](https://img.shields.io/pypi/v/pyairtable.svg)](https://pypi.org/project/pyairtable/)
[![PyPI Downloads - 0.x](https://img.shields.io/pypi/dm/airtable-python-wrapper.svg?label=downloads%200.x)](https://pypi.org/project/airtable-python-wrapper/)
[![PyPI Downloads - 1.x](https://img.shields.io/pypi/dm/pyairtable.svg?label=downloads%201.x)](https://pypi.org/project/pyairtable/)
[![Documentation Status](https://readthedocs.org/projects/pyairtable/badge/?version=latest)](http://pyairtable.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/gtalarico/pyairtable/branch/main/graph/badge.svg?token=askmZgmMoV)](https://codecov.io/gh/gtalarico/pyairtable)

Python client for the Airtable API.

## Installing

```
pip install pyairtable
```

## Documentation

Check out the docs on [pyairtable.readthedocs.io](http://pyairtable.readthedocs.io/).

## Contributing

Everyone who has an idea or suggestion is welcome to contribute! As maintainers, we expect our community of users and contributors to adhere to the guidelines and expectations set forth in the [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). Be kind and empathetic, respect differing opinions, and stay focused on what is best for the community.

### Getting started

If it's your first time working on this library, clone the repo, set up pre-commit hooks, and make sure you can run tests (and they pass). If that doesn't work out of the box, please check your local development environment before filing an issue.

```sh
% make setup
% tox
```

### Reporting a bug

We encourage anyone to [submit an issue](https://github.com/gtalarico/pyairtable/issues/new) to let us know about bugs, as long as you've followed these steps:

1. Confirm you're on the latest version of the library and you can run the test suite locally.
2. Check [open issues](https://github.com/gtalarico/pyairtable/issues) to see if someone else has already reported it.
3. Provide as much context as possible, i.e. expected vs. actual behavior, steps to reproduce, and runtime environment.
4. If possible, reproduce the problem in a small example that you can share in the issue summary.

We ask that you _never_ report security vulnerabilities to the GitHub issue tracker. Sensitive issues of this nature must be sent directly to the maintainers via email.

### Submitting a patch

Anyone who uses this library is welcome to [submit a pull request](https://github.com/gtalarico/pyairtable/pulls) for a bug fix or a new feature. We do ask that all pull requests adhere to the following guidelines:

1. Public functions/methods have docstrings and type annotations.
2. New functionality is accompanied by clear, descriptive unit tests.
3. You can run `make test && make docs` successfully.

If you have an enterprise API key that can run end-to-end tests, please also run `env AIRTABLE_API_KEY=... make test-e2e`.

If you want to discuss an idea you're working on but haven't yet finished all of the above, please [open a draft pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests#draft-pull-requests). That will be a clear signal that you're not asking to merge your code (yet) and are just looking for discussion or feedback.

## Looking for **airtable-python-wrapper**?

airtable-python-wrapper is now **pyAirtable**.
For the previous version go to https://github.com/gtalarico/airtable-python-wrapper/tree/airtable-python-wrapper
