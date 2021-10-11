#!/usr/bin/env python3
from typing import Callable

from hopla.hoplalib.hopla_option import no_interactive_option


class TestNoInteractiveOption:
    def test_no_interactive_option(self):
        f = no_interactive_option()
        assert isinstance(f, Callable)
