core-tests
===============================================================================

This project contains basic elements for testing purposes and the ability 
to run (via console commands) tests and code coverage (unittest-based). This way, we can 
stick to the `DRY -- Don't Repeat Yourself` principle and avoid code duplication
in each python project where tests coverage and tests execution are
expected...

===============================================================================

.. image:: https://img.shields.io/pypi/pyversions/core-tests.svg
    :target: https://pypi.org/project/core-tests/
    :alt: Python Versions

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target: https://gitlab.com/bytecode-solutions/core/core-tests/-/blob/main/LICENSE
    :alt: License

.. image:: https://gitlab.com/bytecode-solutions/core/core-tests/badges/release/pipeline.svg
    :target: https://gitlab.com/bytecode-solutions/core/core-tests/-/pipelines
    :alt: Pipeline Status

.. image:: https://readthedocs.org/projects/core-tests/badge/?version=latest
    :target: https://readthedocs.org/projects/core-tests/
    :alt: Docs Status

.. image:: https://img.shields.io/badge/security-bandit-yellow.svg
    :target: https://github.com/PyCQA/bandit
    :alt: Security

|

How to Use
---------------------------------------

Install the package
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

    pip install core-tests
..

Create entry-point
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    # manager.py
    
    from click.core import CommandCollection
    from core_tests.tests.runner import cli_tests
    
    if __name__ == "__main__":
        cli = CommandCollection(sources=[cli_tests()])
        cli()
..

Shell commands
---------------------------------------

Running tests
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

    python manager.py run-tests --test-type unit
    python manager.py run-tests --test-type integration
    python manager.py run-tests --test-type "another folder that contains test cases under ./tests"
    python manager.py run-tests --test-type functional --pattern "*.py"
..

Using PyTest
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The `unittest` framework cannot discover or run pytest-style tests, it is designed to 
discover and run tests that are subclasses of `unittest.TestCase` and follow its 
conventions. Pytest-style tests (i.e., functions named test_* that are not inside a 
`unittest.TestCase` class, or tests using pytest fixtures, parametrize, etc.) are not 
recognized by unittest’s discovery mechanism, `unittest` will simply ignore standalone 
test functions and any pytest-specific features...

That's why you can use PyTest if required.

.. code-block:: shell

    pip install .[pytest]
    python manager.py run-tests --engine pytest
..

Test coverage
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

    python manager.py run-coverage                  # For `unittest` framework...
    python manager.py run-coverage --engine pytest  # For `PyTest`...
..

Execution Environment
---------------------------------------

Install libraries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

    pip install --upgrade pip 
    pip install virtualenv
..

Create the Python Virtual Environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

    virtualenv --python={{python-version}} .venv
    virtualenv --python=python3.11 .venv
..

Activate the Virtual Environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

    source .venv/bin/activate
..

Install required libraries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

    pip install .
..

Check tests and coverage...
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

    python manager.py run-tests
    python manager.py run-coverage
..
