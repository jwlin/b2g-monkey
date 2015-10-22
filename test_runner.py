#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Module docstring
"""

from abc import ABCMeta, abstractmethod
from automata import Automata, State
from executor import B2gExecutor
from configuration import B2gConfiguration
from dom_analyzer import DomAnalyzer
from visualizer import Visualizer
from os.path import relpath
import time, base64, os, json, posixpath


class TestRunner:
    __metaclass__ = ABCMeta

    @abstractmethod
    def run(self):
        pass


class B2gTestRunner(TestRunner):
    def __init__(self, configuration):
        self.automata = Automata()
        self.configuration = configuration
        self.executor = B2gExecutor(self.configuration.get_app_name(), self.configuration.get_app_id())

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
        self.dump_automata()
        Visualizer.generate_html('web', os.path.join(self.configuration.get_path('root'), 'automata.json'))

    def crawl(self, depth):
        if depth <= self.configuration.get_max_depth():
            cs = self.automata.get_current_state()
            #print cs.get_dom()
            #print '==='
            #for clickable in cs.get_candidate_clickables():
            for clickable in DomAnalyzer.get_clickables(cs.get_dom()):
                #print clickable
                #--print len(cs.get_candidate_clickables())
                #--cs.remove_candidate_clickable(clickable)

                # prefetch image of the clickable
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
                        self.automata.change_state(ns)
                        self.save_screenshot(ns.get_id() + '.png', self.executor.get_screenshot(), 'state')
                        self.save_dom(ns)
                        self.crawl(depth+1)
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

    def dump_automata(self):
        data = {
            'state': [],
            'edge': [],
            'id_prefix': DomAnalyzer.serial_prefix  # the prefix used in ids given by our monkey
        }
        for state in self.automata.get_states():
            state_data = {
                'id': state.get_id(),
                # output unix style path for website: first unpack dirs in get_path('dom') and then posixpath.join them with the filename
                'dom_path': posixpath.join(
                    posixpath.join(*(

                        self.configuration.get_path('dom').split(os.sep)
                    )),
                    state.get_id() + '.txt'
                ),
                'img_path': posixpath.join(
                    posixpath.join(
                        *(relpath(
                            self.configuration.get_path('state'),
                            self.configuration.get_path('root')
                            ).split(os.sep))
                    ),
                    state.get_id() + '.png'
                ),
                'clickable': []
            }
            for clickable in state.get_clickables():
                clickable_data = {
                    'id': clickable.get_id(),
                    'xpath': clickable.get_xpath(),
                    'tag': clickable.get_tag(),
                    'img_path': posixpath.join(
                        posixpath.join(
                            *(relpath(
                                self.configuration.get_path('clickable'),
                                self.configuration.get_path('root')
                                ).split(os.sep))
                        ),
                        state.get_id() + '-' + clickable.get_id() + '.png'
                    ),
                    'form': []
                }
                for form in clickable.get_forms():
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
                    clickable_data['form'].append(form_data)
                state_data['clickable'].append(clickable_data)
            data['state'].append(state_data)
        for (state_from, state_to, clickable, cost) in self.automata.get_edges():
            edge_data = {
                'from': state_from.get_id(),
                'to': state_to.get_id(),
                'clickable': clickable.get_id()
            }
            data['edge'].append(edge_data)

        with open(os.path.join(self.configuration.get_abs_path('root'), 'automata.json'), 'w') as f:
            json.dump(data, f, indent=2, sort_keys=True, ensure_ascii=False)

def main():
    '''
        CrawljaxConfigurationBuilder builder = CrawljaxConfiguration.builderFor(URL);
		builder.crawlRules().insertRandomDataInInputForms(false);

		// click these elements
		builder.crawlRules().clickDefaultElements();
		builder.crawlRules().click("div");

		builder.setMaximumStates(10);
		builder.setMaximumDepth(3);
		builder.crawlRules().clickElementsInRandomOrder(true);

		// Set timeouts
		builder.crawlRules().waitAfterReloadUrl(WAIT_TIME_AFTER_RELOAD, TimeUnit.MILLISECONDS);
		builder.crawlRules().waitAfterEvent(WAIT_TIME_AFTER_EVENT, TimeUnit.MILLISECONDS);


		// We want to use two browsers simultaneously.
		builder.setBrowserConfig(new BrowserConfiguration(BrowserType.FIREFOX, 1));

		CrawljaxRunner crawljax = new CrawljaxRunner(builder.build());
		crawljax.call();
	'''
    #config = B2gConfiguration('E-Mail', 'email')
    config = B2gConfiguration('Contacts', 'contacts')
    config.set_max_depth(2)
    runner = B2gTestRunner(config)
    runner.run()


if __name__ == '__main__':
    main()
