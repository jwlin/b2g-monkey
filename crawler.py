#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Module docstring
"""

from abc import ABCMeta, abstractmethod
from automata import Automata, State, StateDom
from dom_analyzer import DomAnalyzer
import time, base64, os
from bs4 import BeautifulSoup
#=============================================================================================
#Diff: check url domain
from urlparse import urlparse
import itertools
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
        self.save_state(initial_state)
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
    def __init__(self, configuration, executor, automata):
        self.configuration = configuration
        self.executor = executor
        self.automata = automata
    
    def run(self):
        self.executor.start()
        self.get_initail_state()
        self.run_script_before_crawl()
        self.crawl(1)        
        return self.automata

    def crawl(self, depth, prev_state=None):
        print "[LOG] now depth: ",depth," - max_depth: ",self.configuration.get_max_depth()
        if depth <= self.configuration.get_max_depth():
            cs = self.automata.get_current_state()
            print "[LOG] current state", cs.get_id()
            for clickables, iframe_list in DomAnalyzer.get_clickables(cs, prev_state if prev_state else None):  
                print "[DEBUG] clickables: ", [ ( c.get_tag(), c.get_xpath() ) for c in clickables ]
                print "[DEBUG] iframe_list: ", iframe_list
                inputs = cs.get_inputs(iframe_list)
                selects = cs.get_selects(iframe_list)

                for clickable in clickables:
                    '''TODO: ADD OTHER EVENTS '''
                    print "[LOG] state %s fire element in %s " % ( cs.get_id(), iframe_list )
                    self.executor.switch_iframe_and_get_source(iframe_list)
                    self.executor.empty_form([inputs, selects])
                    self.executor.fill_form([inputs, selects])
                    self.executor.fire_event(clickable)

                    dom_list, is_same = self.is_same_state_dom(cs)
                    if not is_same:
                        if self.is_same_domain(self.executor.get_url()):
                            print "[LOG] change dom to: ", self.executor.get_url()
                            # check if this is a new state
                            temp_state = State(dom_list)
                            ns, is_newly_added = self.automata.add_state(temp_state)
                            # save this click edge
                            cs.add_clickable(clickable, iframe_list)
                            self.automata.add_edge(cs, ns, clickable, iframe_list)
                            '''TODO: value of inputs should connect with edges '''
                            if is_newly_added:
                                print "[LOG] add new state ",ns.get_id()," of: ", self.executor.get_url()
                                self.save_state(ns)
                                self.automata.change_state(ns)
                                if depth < self.configuration.get_max_depth():
                                    self.crawl(depth+1, cs)
                            self.automata.change_state(cs)
                        else:
                            print "[LOG] out of domain: ", self.executor.get_url()
                        print "[LOG] depth ", depth," -> backtrack to state ", cs.get_id()
                        self.backtrack(cs)
                        print "[LOG] backtrack end"
            print "[LOG] depth ", depth," -> state ", cs.get_id()," crawl end"

    def backtrack(self, state):
        self.executor.back_history()
        #check if executor really turn back. if not, restart and try go again
        dom_list, is_same = self.is_same_state_dom(state)
        if not is_same:
            edges = self.automata.get_shortest_path(state)
            self.executor.restart_app()
            self.run_script_before_crawl()
            print "[LOG] retart"
            for (state_from, state_to, clickable, iframe_list, cost) in edges:
                self.executor.switch_iframe_and_get_source(iframe_list)
                self.executor.empty_form([state_from.get_inputs(iframe_list), state_from.get_selects(iframe_list)])
                self.executor.fill_form([state_from.get_inputs(iframe_list), state_from.get_selects(iframe_list)])
                self.executor.fire_event(clickable)

                #check again if executor really turn back. if not, sth error, stop
                time.sleep(self.configuration.get_sleep_time())
                dom_list, is_same = self.is_same_state_dom(state_to)
                if not is_same:
                    err = State(dom_list)
                    print "[DEBUG] save diff dom as debug_file "
                    with open('debug_origin_'+state_to.get_id()+'.txt', 'w') as f:
                        f.write(state_to.get_all_dom())
                    with open('debug_restart_'+state_to.get_id()+'.txt', 'w') as f:
                        f.write(err.get_all_dom())
                    with open('debug_origin_nor_'+state_to.get_id()+'.txt', 'w') as f:
                        f.write( state_to.get_all_normalize_dom() )
                    with open('debug_restart_nor_'+state_to.get_id()+'.txt', 'w') as f:
                        f.write( err.get_all_normalize_dom() )
                    print "[ERROR] cannot traceback to %s" % ( state_to.get_id() )
                    self.configuration.save_config('debug_config.json')
                    self.automata.save_automata(self.configuration)

    def save_dom(self, state):
        with open(os.path.join(self.configuration.get_abs_path('dom'), state.get_id() + '.txt'), 'w') as f:
            f.write(state.get_all_dom())
        with open(os.path.join(self.configuration.get_abs_path('dom'), state.get_id() + '_nor.txt'), 'w') as f:
            f.write(state.get_all_normalize_dom())
    #=============================================================================================
    def get_initail_state(self):
        print "get initial state"
        initial_state = State( self.get_dom_list() )
        self.automata.add_state(initial_state)
        self.save_state(initial_state)
        time.sleep(self.configuration.get_sleep_time())

    def run_script_before_crawl(self):
        for script_edge in self.configuration.get_before_script():
            self.executor.empty_form([script_edge.get_inputs(), script_edge.get_selects()])
            self.executor.fill_form([script_edge.get_inputs(), script_edge.get_selects()])
            self.executor.fire_event(script_edge.get_clickable())
        pass

    #Diff: check url domain
    def is_same_domain(self, url):
        base_url = urlparse( self.configuration.get_url() )
        new_url = urlparse( url )
        if base_url.netloc == new_url.netloc:
            return True
        else:
            for d in self.configuration.get_domains():
                d_url = urlparse(d)
                if d_url.netloc == new_url.netloc:
                    return True
            return False

    def close(self):
        self.executor.close()

    #Diff: save state's information(inputs, selects, screenshot, [normalize]dom/iframe)
    def save_state(self, state):
        inputs = []
        selects = []
        for stateDom in state.get_dom_list():
            iframe_path_list = stateDom.get_iframe_path_list()
            dom = stateDom.get_dom()
            inputs.append( (DomAnalyzer.get_inputs(dom), iframe_path_list) )
            selects.append( (DomAnalyzer.get_selects(dom), iframe_path_list) )
        print "[DEBUG] inputs: ",inputs
        print "[DEBUG] selects: ",selects
        state.set_inputs(inputs)
        state.set_selects(selects)

        # save this state's screenshot and dom
        path = os.path.join(self.configuration.get_abs_path('state'), state.get_id() + '.png')
        self.executor.get_screenshot(path)
        self.save_dom(state)

    def is_same_state_dom(self, cs):
        dom_list = self.get_dom_list()
        if len( cs.get_dom_list() ) != len( dom_list ):
            return dom_list, False
        else:
            for dom, cs_dom in itertools.izip(dom_list, cs.get_dom_list()):
                if not dom.is_same(cs_dom):
                    return dom_list, False                    
        return dom_list, True

    def get_dom_list(self):
        #save dom of iframe in list of StateDom [iframe_path_list, dom, url/src, normalize dom]
        dom_list = []

        new_dom = self.executor.switch_iframe_and_get_source()
        url = self.executor.get_url()
        soup = BeautifulSoup(new_dom, 'html.parser')
        for iframe_tag in soup.find_all('iframe'):
            iframe_xpath = DomAnalyzer._get_xpath(iframe_tag)
            iframe_src = iframe_tag['src']
            self.get_dom_of_iframe(dom_list, [iframe_xpath], iframe_src)        
            iframe_tag.clear()
        dom_list.append( StateDom(None, str(soup), url) )
        return dom_list

    def get_dom_of_iframe(self, dom_list, iframe_xpath_list, src):
        dom = self.executor.switch_iframe_and_get_source(iframe_xpath_list)
        soup = BeautifulSoup(dom, 'html.parser')
        for iframe_tag in soup.find_all('iframe'):
            iframe_xpath = DomAnalyzer._get_xpath(iframe_tag)
            iframe_xpath_list.append(iframe_xpath)
            iframe_src = iframe_tag['src']
            self.get_dom_of_iframe(dom_list, iframe_xpath_list, iframe_src)      
            iframe_tag.clear()
        dom_list.append( StateDom(iframe_xpath_list, str(soup), src) )
    #=============================================================================================
#==============================================================================================================================