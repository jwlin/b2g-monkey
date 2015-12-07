#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
The automata (finite state machine) referenced by the monkey.
"""

import json
import posixpath
import os
import time
import logging
from os.path import relpath
from dom_analyzer import DomAnalyzer
from clickable import Clickable, FormField, InputField

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Automata:
    def __init__(self, fname=None, load_dom=False):
        self._states = []
        self._edges = []
        self._initial_state = None
        self._current_state = None
        if fname:
            assert os.path.isfile(fname) and os.path.exists(fname)
            t_start = time.time()
            with open(fname) as f:
                data = json.load(f)
                for state in data['state']:
                    if load_dom:
                        with open(os.path.join(os.path.dirname(os.path.realpath(fname)), state['dom_path']), 'r') as df:
                            s = State(df.read())
                    else:
                        s = State(state['id'])
                    s.set_id(state['id'])
                    for form in state['form']:
                        f = FormField(form['id'], form['xpath'])
                        for the_input in form['input']:
                            f.add_input(InputField(the_input['id'], the_input['xpath'], the_input['type'], the_input['value']))
                        s.add_form(f)
                    for clickable in state['clickable']:
                        c = Clickable(clickable['id'], clickable['xpath'], clickable['tag'])
                        for form in clickable['form']:
                            f = s.get_form_by_id(form['id'])
                            assert f
                            c.add_form(f)
                        s.add_clickable(c)
                    self.add_state(s)
                for edge in data['edge']:
                    from_state = self.get_state_by_id(edge['from'])
                    to_state = self.get_state_by_id(edge['to'])
                    clickable = from_state.get_clickable_by_id(edge['clickable'])
                    assert from_state and to_state and clickable
                    self.add_edge(from_state, to_state, clickable)
            logger.info('automata loaded. loading time: %f sec', time.time() - t_start)

    def get_current_state(self):
        return self._current_state

    def get_initial_state(self):
        return self._initial_state

    def get_states(self):
        return self._states

    def get_edges(self):
        return self._edges

    def add_state(self, state):
        # check if the automata is empty
        if not self._initial_state:
            self._initial_state = state
            self._current_state = state
        else:
            # check if the dom is duplicated
            for s in self._states:
                if DomAnalyzer.is_equal(s.get_dom(), state.get_dom()):
                    return s, False
        state_id = state.get_id() if state.get_id() else str(len(self._states))
        state.set_id(state_id)
        self._states.append(state)
        return state, True

    def change_state(self, state):
        self._current_state = state

    def add_edge(self, state_from, state_to, clickable, cost=1):
        edge = (state_from, state_to, clickable, cost)
        self._edges.append(edge)

    def get_state_by_id(self, sid):
        for s in self._states:
            if s.get_id() == sid:
                return s
        return None

    def get_shortest_path(self, target):
        # Breath First Search
        explored = []
        frontier = [self._initial_state]
        unexplored = [s for s in self._states if s != self._initial_state]
        incoming_edges = {}
        current_state = None

        while (current_state != target) and frontier:
            current_state = frontier.pop(0)
            explored.append(current_state)
            for e in self._edges:  # edge = (state_from, state_to, clickable, cost)
                if e[0] == current_state and e[1] in unexplored:
                    frontier.append(e[1])
                    unexplored.remove(e[1])
                    incoming_edges[e[1]] = e
        edges = []
        if current_state == target:
            while current_state != self._initial_state:
                edges.insert(0, incoming_edges[current_state])
                current_state = incoming_edges[current_state][0]
        else:
            raise ValueError('Automata.get_shortest_path(): No path found when trying to reach state: %s' % target)

        return edges

    def get_forms_with_clickables(self):
        # return clickable sequences for each form in states with forms
        form_list = []
        for state in self._states:
            forms = state.get_forms()
            if forms:
                seq = []
                edges = self.get_shortest_path(state)
                for (state_from, state_to, clickable, cost) in edges:
                    seq.append(clickable)
                for form in forms:
                    form_element = {
                        'state': state.get_id(),
                        'form': form,
                        'execution_seq': list(seq)  # shallow copy of clickables
                    }
                    clickable_list = []
                    for clickable in state.get_clickables():
                        if form in clickable.get_forms():
                            clickable_list.append(clickable)
                        form_element['clickable'] = clickable_list
                    form_list.append(form_element)
        return form_list

    def save(self, config):
        data = {
            'state': [],
            'edge': [],
            'id_prefix': DomAnalyzer.serial_prefix  # the prefix used in ids given by our monkey
        }
        for state in self._states:
            state_data = {
                'id': state.get_id(),
                # output unix style path for website: first unpack dirs in get_path('dom'),
                # and then posixpath.join them with the filename
                'dom_path': posixpath.join(
                    posixpath.join(
                        *(relpath(
                            config.get_path('dom'),
                            config.get_path('root')
                            ).split(os.sep))
                    ),
                    state.get_id() + '.txt'
                ),
                'img_path': posixpath.join(
                    posixpath.join(
                        *(relpath(
                            config.get_path('state'),
                            config.get_path('root')
                            ).split(os.sep))
                    ),
                    state.get_id() + '.png'
                ),
                'clickable': [],
                'form': []
            }
            for form in state.get_forms():
                form_data = {
                    'id': form.get_id(),
                    'xpath': form.get_xpath(),
                    'input': []
                }
                for my_input in form.get_inputs():
                    input_data = {
                        'id': my_input.get_id(),
                        'xpath': my_input.get_xpath(),
                        'type': my_input.get_type(),
                        'value': my_input.get_value()
                    }
                    form_data['input'].append(input_data)
                state_data['form'].append(form_data)
            for clickable in state.get_clickables():
                clickable_data = {
                    'id': clickable.get_id(),
                    'xpath': clickable.get_xpath(),
                    'tag': clickable.get_tag(),
                    'img_path': posixpath.join(
                        posixpath.join(
                            *(relpath(
                                config.get_path('clickable'),
                                config.get_path('root')
                                ).split(os.sep))
                        ),
                        state.get_id() + '-' + clickable.get_id() + '.png'
                    ),
                    'form': []
                }
                for form in clickable.get_forms():
                    form_data = {
                        'id': form.get_id()
                    }
                    clickable_data['form'].append(form_data)
                state_data['clickable'].append(clickable_data)
            data['state'].append(state_data)
        for (state_from, state_to, clickable, cost) in self._edges:
            edge_data = {
                'from': state_from.get_id(),
                'to': state_to.get_id(),
                'clickable': clickable.get_id()
            }
            data['edge'].append(edge_data)

        with open(os.path.join(config.get_abs_path('root'), config.get_automata_fname()), 'w') as f:
            json.dump(data, f, indent=2, sort_keys=True, ensure_ascii=False)

        return os.path.join(config.get_abs_path('root'), config.get_automata_fname())


class State:
    def __init__(self, dom):
        self._id = None
        self._dom = dom
        self._prev_states = []
        self._clickables = []
        self._forms = []

    def add_clickable(self, clickable):
        if clickable in self._clickables:
            return False
        self._clickables.append(clickable)
        return True

    def set_id(self, state_id):
        self._id = state_id

    def add_prev_state(self, state):
        for s in self._prev_states:
            if s.get_dom() == state.get_dom():
                return False
        self._prev_states.append(state)
        return True

    def get_clickables(self):
        return self._clickables

    def get_clickable_by_id(self, cid):
        for c in self._clickables:
            if c.get_id() == cid:
                return c
        return None

    def get_prev_states(self):
        return self._prev_states

    def get_id(self):
        return self._id

    def get_dom(self):
        return self._dom

    def get_forms(self):
        if not self._forms:
            for c in self._clickables:
                for f in c.get_forms():
                    if f not in self._forms:
                        self._forms.append(f)
        return self._forms

    def add_form(self, form):
        for f in self._forms:
            if f.get_xpath() == form.get_xpath():
                return False
        self._forms.append(form)
        return True

    def get_form_by_id(self, fid):
        for f in self._forms:
            if f.get_id() == fid:
                return f
        return None

    def __str__(self):
        return 'state id: %s, prev states: %s, clickables: %s' % \
               (self._id, self._prev_states, len(self._clickables))

