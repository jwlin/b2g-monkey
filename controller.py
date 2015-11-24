#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Main entry of the monkey
"""

import os
import json
import posixpath
import time
import sys
import logging
from os.path import relpath
from configuration import B2gConfiguration
from automata import Automata, State
from clickable import Clickable, FormField, InputField
from executor import B2gExecutor
from crawler import B2gCrawler
from visualizer import Visualizer
from dom_analyzer import DomAnalyzer
from test_generator import TestGenerator


formatter = logging.Formatter("%(asctime)s [%(name)s] [%(levelname)s] %(message)s")
logger = logging.getLogger()
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)


def main():
    t_start = time.time()

    # for crawling
    config = B2gConfiguration('Contacts', 'contacts')
    #config = B2gConfiguration('Firetext', 'firetext')
    #config = B2gConfiguration('App example', '2a3304ed-29c0-400a-a61a-48a3e835caaf')
    #config = B2gConfiguration('Crashed App', '48d3bd2a-c3b2-42af-a5bc-6ece5da9fa0e')
    config.set_max_depth(5)

    file_handler = logging.FileHandler(os.path.join(config.get_path('root'), 'log.txt'))
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    executor = B2gExecutor(config.get_app_name(), config.get_app_id())
    crawler = B2gCrawler(config, executor)

    logger.info('Start crawling, depth %d', config.get_max_depth())

    automata, invariant_violation = crawler.run()
    save_automata(automata, config)
    Visualizer.generate_html('web', os.path.join(config.get_path('root'), config.get_automata_fname()))
    save_config(config, 'config.json')
    logger.info('Crawling finished.')
    form_list = automata.get_forms_with_clickables()
    logger.info('Forms: %d', len(form_list))
    for f in form_list:
        logger.info('state: %s, form-id: %s (xpath: %s), input_value:', f['state'], f['form'].get_id(), f['form'].get_xpath())
        for the_input in f['form'].get_inputs():
            logger.info('type: %s, id: %s (xpath: %s), value: %s',
                  the_input.get_type(), the_input.get_id(), the_input.get_xpath(), the_input.get_value())
        logger.info('path-to-form:')
        for clickable in f['execution_seq']:
            logger.info('id: %s (xpath: %s)', clickable.get_id(), clickable.get_xpath())
        logger.info('clickables in the form:')
        for clickable in f['clickable']:
            logger.info('id: %s (xpath: %s)', clickable.get_id(), clickable.get_xpath())
    logger.info('Violated invariants: %d', len(invariant_violation))
    for inv in invariant_violation:
        logger.info('state: %s, violated invariant: %s, execution sequence:', inv['state'], inv['name'])
        for clickable in inv['sequence']:
            logger.info('id: %s (xpath: %s)', clickable.get_id(), clickable.get_xpath())

    '''
    # for test case generation
    config = load_config(os.path.join('trace/20151112234521-depth-2/config.json'))
    automata = load_automata(os.path.join('trace/20151112234521-depth-2/automata.json'))
    executor = B2gExecutor(config.get_app_name(), config.get_app_id())
    tg = TestGenerator(automata, config, executor)
    #clickable_seqs = tg.clickables_to_forms()
    for state, seq in clickable_seqs.iteritems():
        print 'executing events:', state,
        for c in seq:
            print c
        executor.restart_app()
        for clickable in seq:
            time.sleep(config.get_sleep_time())
            #executor.empty_form(clickable)
            executor.fill_form(clickable)
            #raw_input()
            executor.fire_event(clickable)
    '''
    t_end = time.time()
    logger.info('time elapsed: %f minutes', ((t_end-t_start)/60.0))

def save_automata(automata, configuration):
        data = {
            'state': [],
            'edge': [],
            'id_prefix': DomAnalyzer.serial_prefix  # the prefix used in ids given by our monkey
        }
        for state in automata.get_states():
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
                                configuration.get_path('clickable'),
                                configuration.get_path('root')
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
        for (state_from, state_to, clickable, cost) in automata.get_edges():
            edge_data = {
                'from': state_from.get_id(),
                'to': state_to.get_id(),
                'clickable': clickable.get_id()
            }
            data['edge'].append(edge_data)

        with open(os.path.join(configuration.get_abs_path('root'), configuration.get_automata_fname()), 'w') as f:
            json.dump(data, f, indent=2, sort_keys=True, ensure_ascii=False)


def save_config(config, fname):
    config_data = {}
    config_data['max_depth'] = config.get_max_depth()
    config_data['max_states'] = config.get_max_states()
    config_data['max_time'] = config.get_max_time()
    config_data['sleep_time'] = config.get_sleep_time()
    config_data['app_name'] = config.get_app_name()
    config_data['app_id'] = config.get_app_id()
    config_data['automata_fname'] = config.get_automata_fname()
    config_data['root_path'] = posixpath.join(*(config.get_path('root').split(os.sep)))
    config_data['dom_path'] = posixpath.join(*(config.get_path('dom').split(os.sep)))
    config_data['state_path'] = posixpath.join(*(config.get_path('state').split(os.sep)))
    config_data['clickable_path'] = posixpath.join(*(config.get_path('clickable').split(os.sep)))
    invariants = []
    for inv in config.get_invariants():
        invariants.append(str(inv))
    config_data['invariants'] = invariants
    with open(os.path.join(config.get_abs_path('root'), fname), 'w') as f:
        json.dump(config_data, f, indent=2, sort_keys=True, ensure_ascii=False)


def load_automata(fname, load_dom=False):
    t_start = time.time()
    assert os.path.isfile(fname) and os.path.exists(fname)
    automata = Automata()
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
            automata.add_state(s)
        for edge in data['edge']:
            from_state = automata.get_state_by_id(edge['from'])
            to_state = automata.get_state_by_id(edge['to'])
            clickable = from_state.get_clickable_by_id(edge['clickable'])
            assert from_state and to_state and clickable
            automata.add_edge(from_state, to_state, clickable)
    logger.info('automata loaded. loading time: %f sec', time.time() - t_start)
    return automata


def load_config(fname):
    t_start = time.time()
    with open(fname) as f:
        data = json.load(f)
        config = B2gConfiguration(data['app_name'], data['app_id'], mkdir=False)
        config.set_max_depth(int(data['max_depth']))
        config.set_max_states(int(data['max_states']))
        config.set_sleep_time(int(data['sleep_time']))
        config.set_max_time(int(data['max_time']))
        config.set_automata_fname(data['automata_fname'])
        config.set_path('root', data['root_path'])
        config.set_path('dom', data['dom_path'])
        config.set_path('state', data['state_path'])
        config.set_path('clickable', data['clickable_path'])
        # todo: load invariants
        logger.info('config loaded. loading time: %f sec', time.time() - t_start)
    return config


if __name__ == '__main__':
    main()
