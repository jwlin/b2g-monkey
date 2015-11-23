#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
The automata (finite state machine) referenced by the monkey.
"""

import os, sys, json, posixpath, time
from os.path import relpath
from dom_analyzer import DomAnalyzer
from hashUtil import Hash

class Automata:
    def __init__(self):
        self._states = []
        self._edges = []
        self._initial_state = None
        self._current_state = None
        self.hash = Hash(19, self)
        self._automata_fname = 'automata.json'

    def get_current_state(self):
        return self._current_state

    def get_initial_state(self):
        return self._initial_state

    def get_states(self):
        return self._states

    def get_edges(self):
        return self._edges

    def add_state(self, state):
        if not state.get_id():
            state.set_id( str(len( self.get_states() )) )

        # check if the automata is empty
        if not self._initial_state:
            self._initial_state = state
            self._current_state = state
            is_new, state_id = self.hash.put(state)
        else:
            # check if the dom is duplicated
            is_new, state_id = self.hash.put(state)

        if is_new:
            self._states.append(state)
            return state, True
        else:
            return self.get_state_by_id(state_id), False

    def change_state(self, state):
        self._current_state = state

    def add_edge(self, state_from, state_to, clickable, iframe_list, cost=1):
        edge = (state_from, state_to, clickable, iframe_list, cost)
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

    def save_automata(self, configuration, automata_fname=None):
        automata_fname = self._automata_fname if not automata_fname else automata_fname
        data = {
            'state': [],
            'edge': [], 
            # the prefix used in ids given by our monkey
            'id_prefix': DomAnalyzer.serial_prefix
        }
        for state in self._states:
            state_data = {
                'id': state.get_id(),
                # output unix style path for website: first unpack dirs in get_path('dom'),
                # and then posixpath.join them with the filename
                'dom_path': posixpath.join(
                    posixpath.join(
                        *(relpath(
                            configuration.get_path('dom'),
                            configuration.get_path('root')
                            ).split(os.sep))
                    ),
                    state.get_id() + '.txt'
                ),
                'img_path': posixpath.join(
                    posixpath.join(
                        *(relpath(
                            configuration.get_path('state'),
                            configuration.get_path('root')
                            ).split(os.sep))
                    ),
                    state.get_id() + '.png'
                ),
                'clickable': [],
                'inputs': [],
                'selects': []
            }
            for clickable, iframe_list in state.get_clickables():
                clickable_data = {
                    'id': clickable.get_id(),
                    'xpath': clickable.get_xpath(),
                    'tag': clickable.get_tag(),
                    'iframe_list': str(iframe_list),
                    'img_path': posixpath.join(
                        posixpath.join(
                            *(relpath(
                                configuration.get_path('clickable'),
                                configuration.get_path('root')
                                ).split(os.sep))
                        ),
                        state.get_id() + '-' + clickable.get_id() + '.png'
                    )
                }
                state_data['clickable'].append(clickable_data)
            for my_inputs, iframe_list in state.get_all_inputs():
                for my_input in my_inputs:
                    input_data = {
                        'id': my_input.get_id(),
                        'xpath': my_input.get_xpath(),
                        'type': my_input.get_type(),
                        'value': my_input.get_value(),
                        'iframe_list': str(iframe_list)
                    }
                    state_data['inputs'].append(input_data)
            for selects, iframe_list in state.get_all_selects():
                for select in selects:
                    select_data = {
                        'id': select.get_id(),
                        'xpath': select.get_xpath(),
                        'value': select.get_value(),
                        'iframe_list': str(iframe_list)
                    }
                    state_data['selects'].append(select_data)
            data['state'].append(state_data)
        for (state_from, state_to, clickable, iframe_list, cost) in self._edges:
            edge_data = {
                'from': state_from.get_id(),
                'to': state_to.get_id(),
                'clickable': clickable.get_id(),
                'iframe_list': str(iframe_list)
            }
            data['edge'].append(edge_data)

        with open(os.path.join(configuration.get_abs_path('root'), configuration.get_automata_fname()), 'w') as f:
            json.dump(data, f, indent=2, sort_keys=True, ensure_ascii=False)


class State:
    def __init__(self, dom_list):
        self._id = None
        self._dom_list = dom_list
        self._prev_states = []
        self._clickables = []
        #=============================================================================================
        #Diff: inputs information save in state, indiviual to clickbles, add normalize_dom
        self._inputs = [] #list of iframes of inputs
        self._selects = []
        #=============================================================================================

    def add_clickable(self, clickable, iframe_list):
        # check if the clickable is duplicated
        if clickable.get_id():
            for c, i_list in self._clickables:
                if c.get_id() == clickable.get_id():
                    return False
        else:
            for c, i_list in self._clickables:
                if c.get_xpath() == clickable.get_xpath():
                    return False
        self._clickables.append( (clickable, iframe_list) )
        return True

    def get_clickable_by_id(self, cid):
        for c in self._clickables:
            if c.get_id() == cid:
                return c
        return None

    def get_clickables(self):
        return self._clickables

    def set_id(self, state_id):
        self._id = state_id

    def get_id(self):
        return self._id

    def add_prev_state(self, state):
        for s in self._prev_states:
            if s.get_dom() == state.get_dom():
                return False
        self._prev_states.append(state)
        return True

    def get_prev_states(self):
        return self._prev_states

    def __str__(self):
        return 'state id: %s, prev states: %s, clickables: %s' % \
               (self._id, self._prev_states, len(self._clickables))

    #=============================================================================================
    #Diff: inputs information save in state, indiviual to clickbles
    def set_inputs(self, inputs):
        self._inputs = inputs

    def get_inputs(self, iframe_list):
        for inputs, iframe_path_list in self._inputs:
            if not iframe_list and not iframe_path_list:
                return inputs 
            if iframe_list == iframe_path_list:
                return inputs 

    def get_all_inputs(self):
        return self._inputs 

    def set_selects(self, selects):
        self._selects = selects

    def get_selects(self, iframe_list):
        for selects, iframe_path_list in self._selects:
            if not iframe_list and not iframe_path_list:
                return selects
            if iframe_list == iframe_path_list:
                return selects

    def get_all_selects(self):
        return self._selects

    def get_dom_list(self):
        return self._dom_list

    def get_all_dom(self):
        dom = ''
        for stateDom in self._dom_list:
            dom += stateDom.get_dom()
        return dom

    def get_all_normalize_dom(self):
        dom = ''
        for stateDom in self._dom_list:
            dom += stateDom.get_normalize_dom()
        return dom

    #============================================================================

class StateDom:
    def __init__(self, iframe_path_list, dom, url):
        self.iframe_path_list = iframe_path_list
        self.dom = dom
        self.url = url
        self.normalize_dom = DomAnalyzer.normalize(dom)

    def get_url(self):
        return self.url

    def get_iframe_path_list(self):
        return self.iframe_path_list

    def get_dom(self):
        return self.dom

    def get_normalize_dom(self):
        return self.normalize_dom

    def is_same(self, stateDom):
        return self.url == stateDom.get_url() and \
               self.iframe_path_list == stateDom.get_iframe_path_list() and \
               DomAnalyzer.is_normalize_equal(self.normalize_dom, stateDom.get_normalize_dom())

