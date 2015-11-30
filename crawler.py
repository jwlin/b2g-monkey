#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Module docstring
"""

import os, sys, json, posixpath, time, datetime, base64, codecs
from abc import ABCMeta, abstractmethod
from automata import Automata, State, StateDom
from visualizer import Visualizer
from dom_analyzer import DomAnalyzer
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
        return self.automata

    def crawl(self, depth, prev_state=None):
        if depth <= self.configuration.get_max_depth():
            cs = self.automata.get_current_state()
            #print cs.get_dom()
            #print '==='
            #for clickable in cs.get_candidate_clickables():
            for clickable in DomAnalyzer.get_clickables(cs.get_dom(), prev_state.get_dom() if prev_state else None):
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
        #list of event:(state, clickable, inputs, selects, iframe_list)
        self.event_history = []
    
    def run(self):
        self.executor.start()
        self.executor.goto_url()
        initial_state = self.get_initail_state()
        self.run_script_before_crawl(initial_state)
        self.crawl(1)
        return self.automata

    def crawl(self, depth, prev_state=None):
        print "[LOG] now depth: ",depth," - max_depth: ",self.configuration.get_max_depth()
        if depth <= self.configuration.get_max_depth():
            cs = self.automata.get_current_state()
            print "[LOG] current state", cs.get_id()
            for clickables, iframe_list in DomAnalyzer.get_clickables(cs, prev_state if prev_state else None):
                inputs = cs.get_inputs(iframe_list)
                selects = cs.get_selects(iframe_list)

                for clickable in clickables:
                    '''TODO: ADD OTHER EVENTS '''
                    print "[LOG] state %s fire element in iframe(%s) " % ( cs.get_id(), iframe_list )
                    self.executor.switch_iframe_and_get_source(iframe_list)
                    self.executor.empty_form([inputs, selects])
                    self.executor.fill_form([inputs, selects])
                    self.executor.fire_event(clickable)

                    dom_list, url, is_same = self.is_same_state_dom(cs)
                    if not is_same:
                        if self.is_same_domain(url):
                            print "[LOG] change dom to: ", self.executor.get_url()
                            # check if this is a new state
                            temp_state = State(dom_list, url)
                            ns, is_newly_added = self.automata.add_state(temp_state)
                            # save this click edge
                            cs.add_clickable(clickable, iframe_list)
                            self.automata.add_edge(cs, ns, clickable, inputs, selects, iframe_list)
                            '''TODO: value of inputs should connect with edges '''
                            if is_newly_added:
                                print "[LOG] add new state ",ns.get_id()," of: ", url
                                self.save_state(ns)
                                self.event_history.append( (cs, clickable, inputs, selects, iframe_list) )
                                str_event = [ s.get_id() for s,_c,_i,_s,_l in self.event_history ]
                                print "[DEBUG] event_history: ", str_event
                                if depth < self.configuration.get_max_depth():
                                    self.automata.change_state(ns)
                                    self.crawl(depth+1, cs)
                                self.event_history.pop()
                            self.automata.change_state(cs)
                        else:
                            print "[LOG] out of domain: ", url
                        print "[LOG] <BACKTRACK> : depth ", depth," -> backtrack to state ", cs.get_id()
                        self.backtrack(cs)
                        self.configuration.save_config('config.json')
                        self.automata.save_automata(self.configuration)
                        Visualizer.generate_html('web', os.path.join(self.configuration.get_path('root'), self.configuration.get_automata_fname()))
                        print "[LOG] <BACKTRACK> : end"
            print "[LOG] depth ", depth," -> state ", cs.get_id()," crawl end"

    def backtrack(self, state):
        #if url are same, guess they are just javascipt edges
        if self.executor.get_url() == state.get_url():
            #first, just refresh for javascript button
            print "[log] <BACKTRACK> : try refresh "
            self.executor.refresh()
            dom_list, url, is_same = self.is_same_state_dom(state)
            if is_same:
                return True

        #if can't , try go back form history
        self.executor.back_history()
        print "[log] <BACKTRACK> : try back_history "
        dom_list, url, is_same = self.is_same_state_dom(state)
        if is_same:
            return True

        #if can't , try do last edge of state history
        if len(self.event_history) > 0:
            self.executor.forward_history()
            print "[log] <BACKTRACK> : try last edge of state history "
            parent_state, clickable, inputs, selects, iframe_list = self.event_history[-1]
            self.executor.switch_iframe_and_get_source(iframe_list)
            self.executor.empty_form([inputs, selects])
            self.executor.fill_form([inputs, selects])
            self.executor.fire_event(clickable)
            dom_list, url, is_same = self.is_same_state_dom(state)
            if is_same:
                return True

        #if can't, try go through all edge
        self.executor.goto_url()
        print "[LOG] <BACKTRACK> : start form base url"
        for i in xrange(len(self.event_history)):
            parent_state, clickable, inputs, selects, iframe_list = self.event_history[i]
            self.executor.switch_iframe_and_get_source(iframe_list)
            self.executor.empty_form([inputs, selects])
            self.executor.fill_form([inputs, selects])
            self.executor.fire_event(clickable)
            time.sleep(self.configuration.get_sleep_time())
        dom_list, url, is_same = self.is_same_state_dom(state)
        if is_same:
            return True

        #if can't, restart and try go again
        edges = self.automata.get_shortest_path(state)
        self.executor.restart_app()
        self.executor.goto_url()
        print "[LOG] <BACKTRACK> : retart driver"
        for (state_from, state_to, clickable, inputs, selects, iframe_list, cost) in edges:
            self.executor.switch_iframe_and_get_source(iframe_list)
            self.executor.empty_form([state_from.get_inputs(iframe_list), state_from.get_selects(iframe_list)])
            self.executor.fill_form([state_from.get_inputs(iframe_list), state_from.get_selects(iframe_list)])
            self.executor.fire_event(clickable)

            #check again if executor really turn back. if not, sth error, stop
            time.sleep(self.configuration.get_sleep_time())
            dom_list, url, is_same = self.is_same_state_dom(state_to)
            if not is_same:
                err = State(dom_list, url)
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

        dom_list, url, is_same = self.is_same_state_dom(state)
        return is_same


    def save_dom(self, state):
        with codecs.open(os.path.join(self.configuration.get_abs_path('dom'), state.get_id() + '.txt'), 'w' ) as f:
            f.write(state.get_all_dom())
        with codecs.open(os.path.join(self.configuration.get_abs_path('dom'), state.get_id() + '_nor.txt'), 'w' ) as f:
            f.write(state.get_all_normalize_dom())
        with codecs.open(os.path.join(self.configuration.get_abs_path('dom'), state.get_id() + '_inputs.txt'), 'w', encoding='utf-8' ) as f:
            json.dump(state.get_all_inputs_json(), f, indent=2, sort_keys=True, ensure_ascii=False)
        with codecs.open(os.path.join(self.configuration.get_abs_path('dom'), state.get_id() + '_selects.txt'), 'w', encoding='utf-8' ) as f:
            json.dump(state.get_all_selects_json(), f, indent=2, sort_keys=True, ensure_ascii=False)
        with codecs.open(os.path.join(self.configuration.get_abs_path('dom'), state.get_id() + '_clicks.txt'), 'w', encoding='utf-8') as f:
            json.dump(state.get_all_candidate_clickables_json(), f, indent=2, sort_keys=True, ensure_ascii=False)

    #=============================================================================================
    def get_initail_state(self):
        print "[LOG] get initial state"
        dom_list, url = self.get_dom_list()
        initial_state = State( dom_list, url )
        self.automata.add_state(initial_state)
        self.save_state(initial_state)
        time.sleep(self.configuration.get_sleep_time())
        return initial_state

    def run_script_before_crawl(self, prev_state):
        for inputs, selects, clickable, iframe_list in self.configuration.get_before_script():
            self.executor.switch_iframe_and_get_source(iframe_list)
            self.executor.empty_form([inputs, selects])
            self.executor.fill_form([inputs, selects])
            self.executor.fire_event(clickable)

            dom_list, url, is_same = self.is_same_state_dom(cs)
            if not is_same:
                print "[LOG] change dom to: ", self.executor.get_url()
                # check if this is a new state
                temp_state = State(dom_list, url)
                new_state, is_newly_added = self.automata.add_state(temp_state)
                # save this click edge
                prev_state.add_clickable(clickable, iframe_list)
                self.automata.add_edge(prev_state, new_state, clickable, iframe_list)
                '''TODO: value of inputs should connect with edges '''
                if is_newly_added:
                    print "[LOG] add new state ", new_state.get_id(), " of: ", url
                    self.save_state(new_state)
                    self.automata.change_state(new_state)
                prev_state = new_state

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
        candidate_clickables = []        
        inputs = []
        selects = []
        for stateDom in state.get_dom_list():
            iframe_path_list = stateDom.get_iframe_path_list()
            dom = stateDom.get_dom()
            candidate_clickables.append( (DomAnalyzer.get_candidate_clickables_soup(dom), iframe_path_list) )
            inputs.append( (DomAnalyzer.get_inputs(dom), iframe_path_list) )
            selects.append( (DomAnalyzer.get_selects(dom), iframe_path_list) )
        state.set_candidate_clickables(candidate_clickables)
        state.set_inputs(inputs)
        state.set_selects(selects)

        # save this state's screenshot and dom
        path = os.path.join(self.configuration.get_abs_path('state'), state.get_id() + '.png')
        self.executor.get_screenshot(path)
        self.save_dom(state)

    def is_same_state_dom(self, cs):
        dom_list, url = self.get_dom_list()
        cs_dom_list = cs.get_dom_list()
        if url != cs.get_url():
            return dom_list, url, False
        elif len( cs_dom_list ) != len( dom_list ):
            return dom_list, url, False
        else:
            for dom, cs_dom in itertools.izip(dom_list, cs_dom_list):
                if not dom.is_same(cs_dom):
                    return dom_list, url, False                    
        return dom_list, url, True

    def get_dom_list(self):
        #save dom of iframe in list of StateDom [iframe_path_list, dom, url/src, normalize dom]
        dom_list = []
        new_dom = self.executor.switch_iframe_and_get_source()
        url = self.executor.get_url()
        soup = BeautifulSoup(new_dom, 'html.parser')
        for iframe_tag in soup.find_all('iframe'):
            iframe_xpath = DomAnalyzer._get_xpath(iframe_tag)
            iframe_src = iframe_tag['src'] if iframe_tag.has_attr('src') else None
            try: #not knowing what error in iframe_tag.clear(): no src
                if self.configuration.is_dom_inside_iframe():
                    self.get_dom_of_iframe(dom_list, [iframe_xpath], iframe_src)
                iframe_tag.clear()
            except Exception as e:
                print "[ERROR] ", e
        dom_list.append( StateDom(None, str(soup), url) )
        return dom_list, url

    def get_dom_of_iframe(self, dom_list, iframe_xpath_list, src):
        dom = self.executor.switch_iframe_and_get_source(iframe_xpath_list)
        soup = BeautifulSoup(dom, 'html.parser')
        for iframe_tag in soup.find_all('iframe'):
            iframe_xpath = DomAnalyzer._get_xpath(iframe_tag)
            iframe_xpath_list.append(iframe_xpath)
            iframe_src = iframe_tag['src'] if iframe_tag.has_attr('src') else None
            try:
                self.get_dom_of_iframe(dom_list, iframe_xpath_list, iframe_src)      
                iframe_tag.clear()
            except Exception as e:
                print "[ERROR] ", e
        dom_list.append( StateDom(iframe_xpath_list, str(soup), src) )
    #=============================================================================================
#==============================================================================================================================