# -*- coding: utf-8 -*-

"""
It's just the base class should be used for all
test cases unittest-based within the code
ecosystem.
"""

import os

from unittest import TestCase


class BaseTestCase(TestCase):
    """
    Base class for test cases that adds common behavior.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.resources_directory = f"{os.getcwd()}/tests/resources"
