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

    def clickables_to_forms(self):
        # return clickable sequences for each form in states with forms
        states_with_seqs = {}
        for state in self.automata.get_states():
            forms = state.get_forms()
            if forms:
                seq = []
                edges = self.automata.get_shortest_path(state)
                for (state_from, state_to, clickable, cost) in edges:
                    seq.append(clickable)
                for form in forms:
                    for clickable in state.get_clickables():
                        if form in clickable.get_forms():
                            key = state.get_id() + ' > ' + form.get_id() + ' > ' + clickable.get_id()
                            states_with_seqs[key] = list(seq)
                            states_with_seqs[key].append(clickable)
        return states_with_seqs


