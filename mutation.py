#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, json, posixpath, time, datetime, codecs, logging, random, logging
from automata import Automata, State, StateDom, Edge
from dom_analyzer import DomAnalyzer
from configuration import MutationMethod, MutationMode

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
        self.basic_edge_trace = trace
        self.method = MutationMethod.Simple
        self.modes = []
        self.databank = databank

    def make_data_set(self):
        for edge in self.basic_edge_trace:
            mutation_edge = MutationDataSetEdge(edge, self.databank, self.modes)
            self.data_set_trace.append( mutation_edge )

    def set_method(self, method):
        self.method = method

    def set_modes(self, modes):
        logging.info(modes)
        self.modes = modes

    def make_mutation_traces(self):
        if self.method == MutationMethod.Simple:
            self.make_simple_method()
        elif self.method == MutationMethod.AllInputsOneState:
            pass
        elif self.method == MutationMethod.OneInputsAllState:
            self.make_OneInputsAllState_method()
        elif self.method == MutationMethod.OneInputsOneState:
            pass
        elif self.method == MutationMethod.EachInputsOneState:
            pass

    def get_mutation_traces(self):
        self.log_mutation()
        return self.mutation_traces

    def make_simple_method(self):
        max_len = max( *[ edge.find_max_len() for edge in self.data_set_trace ] ) \
            if len(self.data_set_trace) > 1 else self.data_set_trace[0].find_max_len()
        # bigO=max_len
        if max_len == 0:
            trace = []
            for edge in self.data_set_trace:
                e= ValueEdge()
                e.set_edge_default_value(edge)
                trace.append(e)
            self.mutation_traces.append(trace)

        for i in xrange(max_len):
            trace = []
            for edge in self.data_set_trace:
                e = ValueEdge()
                e.set_edge_default_value(edge)
                for k,v in edge.get_inputs().items():
                    if not v[1] or len(v[1]) == 0:
                        e.get_inputs()[k] = ''
                    else:
                        i_in_list = i if i < len(v[1]) else i%(len(v[1]))
                        e.get_inputs()[k] = v[1][i_in_list]
                trace.append(e)
            self.mutation_traces.append(trace)

    def make_OneInputsAllState_method(self):
        edge_table_list = []
        for edge in self.data_set_trace:
            #make edge's mutation list
            edge_table = []
            for k, v in edge.get_inputs().items():
                for data in v[1]:
                    if data == v[0] or \
                        type(data) == type([]) and len(data) == 2 and data[1] == v[0]:
                        continue
                    e = ValueEdge()
                    e.set_edge_default_value(edge)
                    e.get_inputs()[k] = data
                    edge_table.append(e)

            if not edge_table:
                e = ValueEdge()
                e.set_edge_default_value(edge)
                edge_table.append(e)
            edge_table_list.append(edge_table)

        #find max_len of edge_table
        lens = [1]
        for edge_table in edge_table_list :
            if edge_table:
                lens.append(len(edge_table))
        max_len = max( *lens )
        
        #bigO=max_len(edge)=len(inputs)
        for i in xrange(max_len):
            trace = []
            for edge_table in edge_table_list:
                if not edge_table:
                    continue
                i_in_list = i if i < len(edge_table) else i % len(edge_table)
                trace.append( edge_table[i_in_list] )
            self.mutation_traces.append(trace)

    def log_mutation(self):
        logging.info(' data_set_trace: ------------------------------------------------')
        logging.info( self.get_data_set_trace_json() )
        logging.info(' all mutation_traces: %d ----------------------------------------' % ( len(self.mutation_traces) ) )
        for trace in self.get_mutation_traces_json() :
            logging.info(trace)
            logging.info(' -------------------------- ')

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

class MutationDataSetEdge:
    def __init__(self, edge, databank, modes):
        self.databank = databank
        self._inputs = {}
        for i in edge.get_inputs():
            #================================================================================================
            # IMPORTANT ! change the inputs value with mutation table, not value table
            # data_set => a list of [(info, mutant_value),...]
            #================================================================================================
            dataset = i.get_mutation_data_set(databank, modes)
            self._inputs[i.get_id()] = [ i.get_value(), dataset  ]
            logging.info(dataset )
        self._selects = {}
        for s in edge.get_selects():
            self._selects[s.get_id()] = s.get_selected()
        self._checkboxes = {}
        for c in edge.get_checkboxes():
            self._checkboxes[c.get_checkbox_name()] = c.get_selected_list()
        self._radios = {}
        for r in edge.get_radios():
            self._radios[r.get_radio_name()] = r.get_selected()

    def find_max_len(self):
        i_len = [ len(data_set) for v,data_set in self._inputs.values() ]
        if len(i_len) > 1:
            return max( *(i_len) )
        elif i_len:
            1
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

    def set_edge_default_value(self, mutation_edge):
        for k,v in mutation_edge.get_inputs().items():
            self._inputs[k] = v[0]
        for k,v in mutation_edge.get_selects().items():
            self._selects[k] = v
        for k,v in mutation_edge.get_checkboxes().items():
            self._checkboxes[k] = v
        for k,v in mutation_edge.get_radios().items():
            self._radios[k] = v
