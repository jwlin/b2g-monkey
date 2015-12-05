#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
The automata (finite state machine) referenced by the monkey.
"""

import os, sys, json, posixpath, time, codecs
from os.path import relpath
from dom_analyzer import DomAnalyzer
from hashUtil import Hash

class Automata:
    def __init__(self):
        self._states = []
        self._edges = []
        self._edges_dict = {}
        self._initial_state = None
        self._current_state = None
        self._hash = Hash(19, self)
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
            is_new, state_id = self._hash.put(state)
        else:
            # check if the dom is duplicated
            is_new, state_id = self._hash.put(state)

        if is_new:
            self._states.append(state)
            return state, True
        else:
            return self.get_state_by_id(state_id), False

    def change_state(self, state):
        self._current_state = state

    def add_edge(self, edge):
        self._edges.append(edge)
        if not edge.get_state_from() in self._edges_dict.keys():
            self._edges_dict[edge.get_state_from()] = [edge.get_state_to()]
        else:
            self._edges_dict[edge.get_state_from()].append(edge.get_state_to())

    def get_state_by_id(self, sid):
        for s in self._states:
            if s.get_id() == sid:
                return s
        return None

    def get_edge_by_from_to(self, state_from, state_to ):
        for edge in self._edges:
            if edge.get_state_from() == state_from and edge.get_state_to() == state_to:
                return edge
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
            for edge in self._edges:  
                if edge.get_state_from() == current_state and edge.get_state_to() in unexplored:
                    frontier.append(edge.get_state_to())
                    unexplored.remove(edge.get_state_to())
                    incoming_edges[edge.get_state_to()] = e
        edges = []
        if current_state == target:
            while current_state != self._initial_state:
                edges.insert(0, incoming_edges[current_state])
                current_state = incoming_edges[current_state][0]
        else:
            raise ValueError('Automata.get_shortest_path(): No path found when trying to reach state: %s' % target)

        return edges

    def make_explored_history(self):
        ready = [self.get_state_by_id('0')]
        explored = []
        explored_history = {}
        while len(ready) > 0:
            current = ready.pop(0)
            explored.append(current)
            if current in self._edges_dict.keys():
                for to in self._edges_dict[current]:
                    if not to in explored:
                        ready.append(to)
                        explored_history[to] = current
        return explored_history

    def make_state_and_edge_traces(self, configuration):
        explored_history = self.make_explored_history()
        traces = []
        for s in self._states:
            if s.get_depth() == configuration.get_max_depth():
                state_trace = [s]
                edge_trace = []
                while s in explored_history.keys():
                    parent = explored_history[s]
                    state_trace.insert(0, parent)
                    edge = self.get_edge_by_from_to(parent, s)
                    if edge:
                        edge_trace.insert(0, edge)
                    s = parent
                traces.append( (state_trace, edge_trace) )
        return traces

    def save_traces(self, configuration):
        traces = self.make_state_and_edge_traces(configuration)
        traces_data = {
            'traces': []
        }
        for state_trace, edge_trace in traces:
            trace_data = {
                'states':[],
                'edges':[],
            }
            for s in state_trace:
                state_data = {
                    'id': s.get_id(),
                    'url': s.get_url(),
                    'img_path': posixpath.join(
                        posixpath.join(
                            *(relpath(
                                configuration.get_path('state'),
                                configuration.get_path('root')
                                ).split(os.sep))
                        ),
                        s.get_id() + '.png'
                    ),
                }
                trace_data['states'].append(state_data)
            for edge in edge_trace:                
                trace_data['edges'].append(edge.get_edge_json())
            traces_data['traces'].append(trace_data)

        with codecs.open(os.path.join(configuration.get_abs_path('root'), configuration.get_traces_fname()), 'w', encoding='utf-8' ) as f:
            json.dump(traces_data, f, indent=2, sort_keys=True, ensure_ascii=False)

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
                'url': state.get_url(),
                'depth': state.get_depth(),
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
                'clickable': state.get_all_clickables_json(),
                'inputs': state.get_all_inputs_json(),
                'selects': state.get_all_selects_json()
            }
            data['state'].append(state_data)
        for edge in self._edges:
            data['edge'].append(edge.get_edge_json())

        with codecs.open(os.path.join(configuration.get_abs_path('root'), configuration.get_automata_fname()), 'w', encoding='utf-8' ) as f:
            json.dump(data, f, indent=2, sort_keys=True, ensure_ascii=False)


class State:
    def __init__(self, dom_list, url):
        self._id = None
        #list of Statedom( dom, iframe )
        self._dom_list = dom_list
        self._prev_states = []
        self._clickables = {}
        self._url = url
        self._depth = 0
        #=============================================================================================
        #Diff: inputs information save in state, indiviual to clickables, add normalize_dom
        self._inputs = {} #dict [iframes] of inputs
        self._selects = {}
        self._candidate_clickables = {}
        self._radios = {}
        self._checkboxes = {}
        #=============================================================================================

    def add_clickable(self, clickable, iframe_list):
        # check if the clickable is duplicated
        if iframe_list in self._clickables.keys():
            if clickable.get_id():
                for c in self._clickables[iframe_list]:
                    if c.get_id() == clickable.get_id():
                        return False
            else:
                for c in self._clickables[iframe_list]:
                    if c.get_xpath() == clickable.get_xpath():
                        return False
            self._clickables[iframe_list].append( clickable )
        else:
            self._clickables[iframe_list] = [clickable]
        return True

    def get_clickable_by_id(self, c_id):
        for iframe_list in self._clickables.keys():
            for c in self._clickables[iframe_list]:
                if c.get_id() == c_id:
                    return c
        return None

    def get_clickables(self):
        return self._clickables

    def get_all_clickables_json(self):
        note = []
        for iframe_key in self._clickables.keys():
            iframe = {
                'iframe_list': iframe_key.split(';'),
                'clickables': []
            }
            for clickable in self._clickables[iframe_key]:
                clickable_data = {
                    'id': clickable.get_id(),
                    'name': clickable.get_name(),
                    'xpath': clickable.get_xpath(),
                    'tag': clickable.get_tag(),
                    'iframe_list': []
                }
                iframe['clickables'].append(clickable_data)
            note.append(iframe)
        return note

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
    #Diff: inputs information save in state, indiviual to clickables
    def set_inputs(self, inputs):
        self._inputs = inputs

    def get_inputs(self, iframe_list):
        return self._inputs[iframe_list]

    def get_all_inputs(self):
        return self._inputs 

    def get_all_inputs_json(self):
        note = []
        for iframe_key in self._inputs.keys():
            iframe = {
                'iframe_list': iframe_key.split(';'),
                'inputs': []
            }
            for my_input in self._inputs[iframe_key]:
                input_data = {
                    'id': my_input.get_id(),
                    'name': my_input.get_name(),
                    'xpath': my_input.get_xpath(),
                    'type': my_input.get_type(),
                }
                iframe['inputs'].append(input_data) 
            note.append(iframe)
        return note

    def set_selects(self, selects):
        self._selects = selects

    def get_selects(self, iframe_list):
        return self._selects[iframe_list]

    def get_all_selects(self):
        return self._selects

    def get_all_selects_json(self):
        note = []
        for iframe_key in self._selects.keys():
            iframe = {
                'iframe_list': iframe_key.split(';'),
                'selects': []
            }
            for my_select in self._selects[iframe_key]:
                select_data = {
                    'id': my_select.get_id(),
                    'name': my_select.get_name(),
                    'xpath': my_select.get_xpath(),
                }
                iframe['selects'].append(select_data) 
            note.append(iframe)
        return notedef set_inputs(self, inputs):
        self._inputs = inputs

    def set_checkboxes(self, checkboxes):
        self._checkboxes = checkboxes

    def get_checkboxes(self, iframe_list):
        return self._checkboxes[iframe_list]

    def get_all_checkboxes(self):
        return self._checkboxes

    def get_all_checkboxes_json(self):
        note = []
        for iframe_key in self._checkboxes.keys():
            iframe = {
                'iframe_list': iframe_key.split(';'),
                'checkboxes': []
            }
            for my_checkbox in self._checkboxes[iframe_key]:
                checkbox_data = {
                    'id': my_checkbox.get_id(),
                    'name': my_checkbox.get_name(),
                    'xpath': my_checkbox.get_xpath()
                }
                iframe['inputs'].append(checkbox_data) 
            note.append(iframe)
        return note

    def set_checkboxes(self, checkboxes):
        self._checkboxes = checkboxes

    def get_radios(self, iframe_list):
        return self._radios[iframe_list]

    def get_all_radios(self):
        return self._radios

    def get_all_radios_json(self):
        note = []
        for iframe_key in self._radios.keys():
            iframe = {
                'iframe_list': iframe_key.split(';'),
                'radios': []
            }
            for my_radio_field in self._radios[iframe_key]:
                radio_field_data = {
                    'name': my_radio_field.get_radio_name(),
                    'radios': []
                }
                for my_radio in my_radio_field.get_radio_list():
                    radio_data = {
                        'id': my_radio.get_id(),
                        'xpath': my_radio.get_xpath()
                    }
                    my_radio_field['radios'].append(radio_data)
                iframe['inputs'].append(radio_data) 
            note.append(iframe)
        return note

    def set_candidate_clickables(self, candidate_clickables):
        self._candidate_clickables = candidate_clickables

    def get_all_candidate_clickables(self):
        return self._candidate_clickables

    def get_all_candidate_clickables_json(self):
        note = []
        for iframe_key in self._candidate_clickables.keys():
            iframe = {
                'iframe_list': iframe_key.split(';'),
                'candidate_clickables': []
            }
            for c, xpath in self._candidate_clickables[iframe_key]:
                candidate_clickable = {}
                candidate_clickable['id'] = c['id'] if c.has_attr('id') else None
                candidate_clickable['name'] = c['name'] if c.has_attr('name') else None
                candidate_clickable['xpath'] = xpath
                candidate_clickable['tag'] = c.name
                iframe['candidate_clickables'].append(candidate_clickable)
            note.append(iframe)
        return note

    def get_dom_list(self):
        return self._dom_list

    def get_all_dom(self):
        dom = [ stateDom.get_dom() for stateDom in self._dom_list ]
        dom = "\n".join(dom)
        return dom

    def get_all_normalize_dom(self):
        dom = [ stateDom.get_normalize_dom() for stateDom in self._dom_list ]
        dom = "\n".join(dom)
        return dom

    def set_url(self, url):
        self._url = url

    def get_url(self):
        return self._url

    def set_depth(self, depth):
        self._depth = depth

    def get_depth(self):
        return self._depth
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

class Edge:
    def __init__(self, state_from, state_to, clickable, inputs, selects, iframe_list, cost = 1):
        self._state_from = state_from
        self._state_to = state_to
        self._clickable = clickable
        self._inputs = inputs
        self._selects = selects
        self._iframe_list = iframe_list

    def get_state_from(self):
        return self._state_from

    def get_state_to(self):
        return self._state_to

    def get_clickable(self):
        return self._clickable

    def get_inputs(self):
        return self._inputs

    def get_selects(self):
        return self._selects

    def get_iframe_list(self):
        return self._iframe_list

    def get_edge_json(self):
        edge_data = {
            'from': self._state_from.get_id(),
            'to': self._state_to.get_id(),
            'clickable': {
                'id': self._clickable.get_id(),
                'name': self._clickable.get_name(),
                'xpath': self._clickable.get_xpath(),
                'tag': self._clickable.get_tag()
            },
            'inputs': [],
            'selects': [],
            'iframe_list': self._iframe_list.split(';')
        }
        for my_input in self._inputs:
            input_data = {
                'id': my_input.get_id(),
                'name': my_input.get_name(),
                'xpath': my_input.get_xpath(),
                'type': my_input.get_type(),
                'value': my_input.get_value()
            }
            edge_data['inputs'].append(input_data)
        for select in self._selects:
            select_data = {
                'id': select.get_id(),
                'name': select.get_name(),
                'xpath': select.get_xpath(),
                'value': select.get_value()
            }
            edge_data['selects'].append(select_data)
        return edge_data