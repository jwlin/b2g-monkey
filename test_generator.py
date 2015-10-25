#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Module docstring
"""


class TestGenerator:
    def __init__(self, automata, config, executor):
        self.automata = automata
        self.config = config
        self.executor = executor

    def path_to_state(self, state):
        return self.automata.get_shortest_path(state)