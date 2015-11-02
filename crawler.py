#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Module docstring
"""

from abc import ABCMeta, abstractmethod
from automata import Automata, State
from dom_analyzer import DomAnalyzer
import time, base64, os
#=============================================================================================
#Diff: check url domain
from urlparse import urlparse
#=============================================================================================


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

    def run(self):
        self.executor.restart_app()
        initial_state = State(self.executor.get_source())
        self.automata.add_state(initial_state)
        self.save_screenshot(initial_state.get_id() + '.png', self.executor.get_screenshot(), 'state')
        self.save_dom(initial_state)
        self.crawl(1)
        '''
        print 'automata'
        for s in self.automata.get_states():
            print s
            for c in s.get_clickables():
                print c
                for f in c.get_forms():
                    print f
                    for _i in f.get_inputs():
                        print _i
        print 'edges'
        for (state_from, state_to, clickable, cost) in self.automata.get_edges():
            print state_from, state_to, clickable, cost
        '''
        return self.automata

    def crawl(self, depth, prev_state=None):
        if depth <= self.configuration.get_max_depth():
            cs = self.automata.get_current_state()
            #print cs.get_dom()
            #print '==='
            #for clickable in cs.get_candidate_clickables():
            for clickable in DomAnalyzer.get_clickables(cs.get_dom(), prev_state.get_dom() if prev_state else None):
                #print clickable
                #--print len(cs.get_candidate_clickables())
                #--cs.remove_candidate_clickable(clickable)

                # prefetch image of the clickable
                time.sleep(0.2)  # time for correctly fetching image
                img_name = cs.get_id() + '-' + clickable.get_id() + '.png'
                img_data = self.executor.get_screenshot(clickable)

                # fire the clickable
                self.executor.empty_form(clickable)
                self.executor.fill_form(clickable)
                self.executor.fire_event(clickable)
                time.sleep(self.configuration.get_sleep_time())

                new_dom = self.executor.get_source()
                if not DomAnalyzer.is_equal(cs.get_dom(), new_dom):
                    cs.add_clickable(clickable)
                    self.save_screenshot(img_name, img_data, 'clickable')
                    ns, is_newly_added = self.automata.add_state(State(new_dom))
                    self.automata.add_edge(cs, ns, clickable)
                    if is_newly_added:
                        self.save_screenshot(ns.get_id() + '.png', self.executor.get_screenshot(), 'state')
                        self.save_dom(ns)
                        self.automata.change_state(ns)
                        self.crawl(depth+1, cs)
                    self.automata.change_state(cs)
                    self.backtrack(cs)

    def backtrack(self, state):
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


#==============================================================================================================================
# Selenium Web Driver
#==============================================================================================================================
class SeleniumCrawler(Crawler):
    def __init__(self, configuration, executor):
        self.automata = Automata()
        self.configuration = configuration
        self.executor = executor

    def run(self):
        #self.executor.restart_app()
        print "get initial state"
        initial_state = State(self.executor.get_source())
        self.automata.add_state(initial_state)
        #=============================================================================================
        #Diff: selenium save screenshot as file, need mkdir first!
        path = os.path.join(self.configuration.get_abs_path('state'), initial_state.get_id() + '.png')
        self.executor.get_screenshot(path)
        #=============================================================================================
        self.save_dom(initial_state)
        self.crawl(1)
        return self.automata

    def crawl(self, depth, prev_state=None):
        print "now depth: ",depth," - max_depth: ",self.configuration.get_max_depth()
        if depth <= self.configuration.get_max_depth():
            cs = self.automata.get_current_state()
            print "current state", cs.get_id()

            for clickable in DomAnalyzer.get_clickables(cs.get_dom(), prev_state.get_dom() if prev_state else None):
                #=============================================================================================
                #Diff: selenium dosen't screenshot edge clickable
                #=============================================================================================
                # EVENT1-SIMPLE CLICK : fire the clickable
                '''TODO: ADD OTHER EVENTS '''
                print "state ",cs.get_id(), " fire element"
                self.executor.empty_form(clickable)
                self.executor.fill_form(clickable)
                self.executor.fire_event(clickable)
                time.sleep(self.configuration.get_sleep_time())

                new_dom = self.executor.get_source()
                if not DomAnalyzer.is_equal(cs.get_dom(), new_dom) and self.is_same_domain(self.executor.get_url()):
                    print "change dom to: ", self.executor.get_url()
                    cs.add_clickable(clickable)
                    ns, is_newly_added = self.automata.add_state(State(new_dom))
                    self.automata.add_edge(cs, ns, clickable)
                    if is_newly_added:
                        print "add new state ",ns.get_id()," of: ", self.executor.get_url()
                        path = os.path.join(self.configuration.get_abs_path('state'), ns.get_id() + '.png')
                        self.executor.get_screenshot(path)
                        self.save_dom(ns)
                        self.automata.change_state(ns)
                        self.crawl(depth+1, cs)
                    self.automata.change_state(cs)
                    print "depth ", depth," -> backtrack to state ", cs.get_id()
                    self.backtrack(cs)
                    print "backtrack end"
            print "depth ", depth," -> state ", cs.get_id()," crawl end"

    def backtrack(self, state):
        self.executor.back_history()
        time.sleep(self.configuration.get_sleep_time())
        dom = self.executor.get_source()
        #check if executor really turn back. if not, restart and try go again
        if not DomAnalyzer.is_equal(state.get_dom(), dom):
            edges = self.automata.get_shortest_path(state)
            self.executor.restart_app()
            print "retart"
            for (state_from, state_to, clickable, cost) in edges:
                time.sleep(self.configuration.get_sleep_time())
                self.executor.empty_form(clickable)
                self.executor.fill_form(clickable)
                self.executor.fire_event(clickable)
            time.sleep(self.configuration.get_sleep_time())
            dom = self.executor.get_source()
            #check again if executor really turn back. if not, sth error, stop
            if not DomAnalyzer.is_equal(state.get_dom(), dom):
                '''TODO: stop and throw exception'''


    def save_dom(self, state):
        with open(os.path.join(self.configuration.get_abs_path('dom'), state.get_id() + '.txt'), 'w') as f:
            f.write(state.get_dom())

    #=============================================================================================
    #Diff: check url domain
    def is_same_domain(self, url):
        base_url = urlparse( self.configuration.get_url() )
        new_url = urlparse( url )
        return base_url.netloc == new_url.netloc 
    #=============================================================================================
#==============================================================================================================================