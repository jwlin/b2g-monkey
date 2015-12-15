#!/usr/bin/python
# -*- coding: utf-8 -*-


import os, sys, json, posixpath, time, datetime, codecs, logging, random
from automata import Automata, State, StateDom, Edge
from dom_analyzer import DomAnalyzer
from configuration import MutationMethod

# mode 1: default crawljax, mutate all inputs at all edge each time
# mode 2: mutate all inputs at one edge each time 
# mode 3: mutate only one input at one edge each time 
# mode 4: mutate each one input at one edge each time
# mode 5: mutate each one input at each one edge each time
'''
DESCRIBE:
ex: [A,A2,A3,A4][B,B2]->[C,C2,C3][D,D2][E,E2,E3]
    (A, B)->(C, D, E)

mode 1: (A2,B2)->(C2,D2,E2); (A3,B)->(C3,D,E3); (A4,B2)->(C,D2,E)

mode 2: (A2,B2)->(C,D,E); (A3,B)->(C,D,E); (A4,B2)->(C,D,E)
        (A,B)->(C2,D2,E2); (A,B)->(C3,D,E3)

mode 3: (A2,B)->(C,D,E); (A3,B)->(C,D,E); (A4,B)->(C,D,E); (A,B2)->(C,D,E);
        (A,B)->(C2,D,E); (A,B)->(C3,D,E); (A,B)->(C,D2,E);
        (A,B)->(C,D,E2); (A,B)->(C,D,E3);

mode 4: (A2,B)->(C,D,E); (A3,B)->(C,D,E); (A4,B)->(C,D,E);
        (A,B2)->(C,D,E); (A2,B2)->(C,D,E); (A3,B2)->(C,D,E); (A4,B2)->(C,D,E);
        (A,B)->(C2,D,E); (A,B)->(C3,D,E); (A,B)->(C,D2,E); (A,B)->(C2,D2,E);
        (A,B)->(C3,D2,E); (A,B)->(C,D,E2); (A,B)->(C2,D,E2); (A,B)->(C3,D,E2);
        (A,B)->(C,D2,E2); (A,B)->(C2,D2,E2); (A,B)->(C3,D2,E2); (A,B)->(C,D,E3);
        (A,B)->(C2,D,E3); (A,B)->(C3,D,E3); (A,B)->(C,D2,E3); (A,B)->(C2,D2,E3);
        (A,B)->(C3,D2,E3);
'''

class Mutation:
    def __init__(self, trace, databank):
        self.data_set_trace = []
        self.mutation_traces = []
        self.trace = trace
        self.method = MutationMethod.Simple
        self.databank = databank

    def make_data_set(self):
        for edge in self.trace:
            mutation_edge = MutationEdge(edge, self.databank)
            self.data_set_trace.append( mutation_edge )
            print edge.get_state_from(),'->',edge.get_state_to()

    def set_method(self, method):
        self.method = method

    def make_mutation_traces(self):
        if self.method == MutationMethod.Simple:
            print "start make simple"
            self.make_simple_method()
        elif self.method == MutationMethod.AllInputsOneState:
            self.make_AllInputsOneState_method()
        elif self.method == MutationMethod.OneInputsOneState:
            pass
        elif self.method == MutationMethod.EachInputsOneState:
            pass

    def get_mutation_traces(self):
        #print '\n\n\n',self.get_data_set_trace_json()
        #print '\n\n\n\n',self.get_mutation_traces_json()
        return self.mutation_traces

    def make_simple_method(self):
        max_len = 0
        for edge in self.data_set_trace:
            max_len = max( edge.find_max_len(), max_len )
        # bigO=max_len
        print 'max_len', max_len
        for i in xrange(max_len):
            trace = []
            for edge in self.data_set_trace:
                e = ValueEdge()
                for k,v in edge.get_inputs().items():
                    if not v[1] or len(v[1]) == 0:
                        e.get_inputs()[k] = ''
                    else:
                        i_in_list = i if i < len(v[1]) else i%len(v[1])
                        e.get_inputs()[k] = v[1][i_in_list]
                for k,v in edge.get_selects().items():
                    if not v[1] or len(v[1]) == 0:
                        e.get_selects()[k] = ''
                    else:
                        i_in_list = i if i < len(v[1]) else i%len(v[1])
                        e.get_selects()[k] = v[1][i_in_list]
                for k,v in edge.get_checkboxes().items():
                    if not v[1] or len(v[1]) == 0:
                        e.get_checkboxes()[k] = ''
                    else:
                        i_in_list = i if i < len(v[1]) else i%len(v[1])
                        e.get_checkboxes()[k] = v[1][i_in_list]
                for k,v in edge.get_radios().items():
                    if not v[1] or len(v[1]) == 0:
                        e.get_radios()[k] = ''
                    else:
                        i_in_list = i if i < len(v[1]) else i%len(v[1])
                        e.get_radios()[k] = v[1][i_in_list]
                trace.append(e)
            self.mutation_traces.append(trace)

    def make_AllInputsOneState_method(self):
        #bigO=len(trace)*max_len(edge)
        for edge in self.data_set_trace:
            for i in xrange(edge.find_max_len()):
                trace=[]
                for _edge in self.data_set_trace:
                    if edge != _edge:
                        e = ValueEdge()
                        for k,v in edge.get_inputs().items():
                            e.get_inputs()[k] = v[0]
                        trace.append(e)
                    else:
                        e = ValueEdge()
                        for k,v in edge.get_inputs().items():
                            if not v or len(v) == 0:
                                e.get_inputs()[k] = ''
                            else:
                                i_in_list = i if i < len(v) else i%len(v)
                                e.get_inputs()[k] = v[i_in_list]
                                trace.appenf(e)
                self.mutation_traces.append(trace)

    def get_data_set_trace_json(self):
        note = []
        for edge in self.data_set_trace:
            edge_data = {
                'inputs':{},
                'selects':{},
                'checkboxes':{},
                'radios':{}
            }
            for k,v in edge.get_inputs().items():
                edge_data['inputs'][k] = v
            for k,v in edge.get_selects().items():
                edge_data['selects'][k] = v
            for k,v in edge.get_checkboxes().items():
                edge_data['checkboxes'][k] = v
            for k,v in edge.get_radios().items():
                edge_data['radios'][k] = v
            note.append(edge_data)
        return note

    def get_mutation_traces_json(self):
        note = []
        for trace in self.mutation_traces:
            trace_data = []
            for edge in trace:
                edge_data = {
                    'inputs':{},
                    'selects':{},
                    'checkboxes':{},
                    'radios':{}
                }
                for k,v in edge.get_inputs().items():
                    edge_data['inputs'][k] = v
                for k,v in edge.get_selects().items():
                    edge_data['selects'][k] = v
                for k,v in edge.get_checkboxes().items():
                    edge_data['checkboxes'][k] = v
                for k,v in edge.get_radios().items():
                    edge_data['radios'][k] = v
                trace_data.append(edge_data)
            note.append(trace_data)
        return note

class MutationEdge:
    def __init__(self, edge, databank):
        self.databank = databank
        self._inputs = {}
        for i in edge.get_inputs():
            self._inputs[i.get_id()] = [ i.get_value(), i.get_data_set(databank) ]
        self._selects = {}
        for s in edge.get_selects():
            self._selects[s.get_id()] = [ s.get_selected(), s.get_data_set(databank) ]
        self._checkboxes = {}
        for c in edge.get_checkboxes():
            self._checkboxes[c.get_checkbox_name()] = [ c.get_selected_list(), c.get_data_set(databank) ]
        self._radios = {}
        for r in edge.get_radios():
            self._radios[r.get_radio_name()] = [ r.get_selected(), r.get_data_set(databank) ]

    def find_max_len(self):
        i_len = [ len(data_set) for v,data_set in self._inputs.values() ]
        s_len = [ len(data_set) for v,data_set in self._selects.values() ]
        c_len = [ len(data_set) for v,data_set in self._checkboxes.values() ]
        r_len = [ len(data_set) for v,data_set in self._radios.values() ]

        if i_len or s_len or c_len or r_len:
            return max( *(i_len+s_len+c_len+r_len) )
        else:
            return 0

    def get_inputs(self):
        return self._inputs

    def get_selects(self):
        return self._selects

    def get_checkboxes(self):
        return self._checkboxes

    def get_radios(self):
        return self._radios

class ValueEdge:
    def __init__(self):
        self._inputs = {}
        self._selects = {}
        self._checkboxes = {}
        self._radios = {}

    def get_inputs(self):
        return self._inputs

    def get_selects(self):
        return self._selects

    def get_checkboxes(self):
        return self._checkboxes

    def get_radios(self):
        return self._radios


