#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Crawler
"""

import time
import base64
import os
import threading
import sys
import logging
from abc import ABCMeta, abstractmethod
from automata import Automata, State
from dom_analyzer import DomAnalyzer

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class Crawler:
    __metaclass__ = ABCMeta

    @abstractmethod
    def run(self):
        pass


class B2gCrawler(Crawler):
    def __init__(self, configuration, executor):
        self.automata = Automata()
        self.configuration = configuration
        self.executor = executor
        self.exe_stack = []  # stack of executed clickables (events)
        self.invariant_violation = []
        self.num_clickables = {
            'unexamined': 0,  # num of candidate clickables found with rules in DomAnalyzer
            'true':  0,  # num of clickables triggered new state (different screen dom)
            'false': 0,  # num of clickables not triggering new state
        }

    def run(self):
        self.executor.restart_app()
        initial_state = State(self.executor.get_source())
        self.automata.add_state(initial_state)
        self.save_screenshot(initial_state.get_id() + '.png', self.executor.get_screenshot(), 'state')
        self.save_dom(initial_state)
        self.crawl(1)
        self.invariant_violation = sorted(self.invariant_violation, key=lambda k: int(k['state']))
        return self.automata, self.invariant_violation, self.num_clickables

    def crawl(self, depth, prev_state=None):
        if depth <= self.configuration.get_max_depth():
            cs = self.automata.get_current_state()
            if not self.violate_invariant(cs.get_dom(), cs.get_id()):
                candidate_clickables = DomAnalyzer.get_clickables(cs.get_dom(), prev_state.get_dom() if prev_state else None)
                self.num_clickables['unexamined'] += len(candidate_clickables)
                for clickable in candidate_clickables:
                    # prefetch image of the clickable
                    time.sleep(0.2)  # time for correctly fetching image
                    img_name = cs.get_id() + '-' + clickable.get_id() + '.png'
                    img_data = self.executor.get_screenshot(clickable)

                    # fire the clickable
                    logger.debug('Fire event in state %s', cs.get_id())
                    self.executor.empty_form(clickable)
                    self.executor.fill_form(clickable)
                    ft = FireEventThread(self.executor, clickable)
                    ft.start()
                    ft.join(self.configuration.get_sleep_time()*2)  # time out after sleep_time*2 seconds
                    if ft.is_alive():  # timed out
                        logger.error('No response while firing an event. Execution sequences:')
                        self.exe_stack.append(clickable)  # add the clickable triggering No Response
                        for c in self.exe_stack:
                            logger.error(c)
                        logger.error('Total clickables found: %d (true: %d, false: %d, unexamined: %d)',
                                     self.num_clickables['unexamined'] + self.num_clickables['true'] + self.num_clickables['false'],
                                     self.num_clickables['true'],
                                     self.num_clickables['false'],
                                     self.num_clickables['unexamined']
                                     )
                        logger.error('Program terminated.')
                        sys.exit()
                    time.sleep(self.configuration.get_sleep_time())
                    self.num_clickables['unexamined'] -= 1

                    new_dom = self.executor.get_source()
                    if DomAnalyzer.is_equal(cs.get_dom(), new_dom):
                        self.num_clickables['false'] += 1
                    else:
                        self.num_clickables['true'] += 1
                        cs.add_clickable(clickable)
                        self.exe_stack.append(clickable)
                        self.save_screenshot(img_name, img_data, 'clickable')
                        ns, is_newly_added = self.automata.add_state(State(new_dom))
                        self.automata.add_edge(cs, ns, clickable)
                        if is_newly_added:
                            self.save_screenshot(ns.get_id() + '.png', self.executor.get_screenshot(), 'state')
                            self.save_dom(ns)
                            self.automata.change_state(ns)
                            self.crawl(depth+1, cs)
                        self.exe_stack.pop(-1)
                        self.automata.change_state(cs)
                        self.backtrack(cs)

    def backtrack(self, state):
        logger.debug('Backtrack to state %s', state.get_id())
        edges = self.automata.get_shortest_path(state)
        self.executor.restart_app()
        for (state_from, state_to, clickable, cost) in edges:
            time.sleep(self.configuration.get_sleep_time())
            self.executor.empty_form(clickable)
            self.executor.fill_form(clickable)
            self.executor.fire_event(clickable)

    def save_screenshot(self, fname, b64data, my_type):
        path = os.path.join(self.configuration.get_abs_path(my_type), fname)
        imgdata = base64.b64decode(b64data)
        with open(path, 'wb') as f:
            f.write(imgdata)

    def save_dom(self, state):
        with open(os.path.join(self.configuration.get_abs_path('dom'), state.get_id() + '.txt'), 'w') as f:
            f.write(state.get_dom())

    def violate_invariant(self, dom, statd_id):
        is_violated = False
        for inv in self.configuration.get_invariants():
            if inv.check(dom):
                is_violated = True
                violation = {
                    'state': statd_id,
                    'name': str(inv),
                    'sequence': list(self.exe_stack)  # shallow copy of clickables
                }
                self.invariant_violation.append(violation)
        return is_violated


class FireEventThread(threading.Thread):
    def __init__(self, executor, clickable):
        threading.Thread.__init__(self)
        self._executor = executor
        self._clickable = clickable

    def run(self):
        self._executor.fire_event(self._clickable)
