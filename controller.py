#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Main entry of the monkey
"""

import os
import time
import sys
import logging
from configuration import B2gConfiguration
from executor import B2gExecutor
from crawler import B2gCrawler
from visualizer import Visualizer


formatter = logging.Formatter("%(asctime)s [%(name)s] [%(levelname)s] %(message)s")
logger = logging.getLogger()
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)


def main():
    t_start = time.time()

    # Init config. For loading config file instead of creating a new one:
    # config = B2gConfiguration(app_name=None, app_id=None, fname='test_data/config.json')
    config = B2gConfiguration('Contacts', 'contacts')  # APP_NAME, APP_ID
    #config = B2gConfiguration('Notes', '5f6c37ff-a957-471c-9fc8-a3b66c3814ca')
    #config = B2gConfiguration('App example', '2a3304ed-29c0-400a-a61a-48a3e835caaf')
    #config = B2gConfiguration('Crashed App', '48d3bd2a-c3b2-42af-a5bc-6ece5da9fa0e')

    # Refer to configuration.py to see supported operations
    config.set_max_depth(2)

    '''
    # example code of adding a invariant:
    from invariant import TagInvariant
    config.add_invariant(
        TagInvariant('a',
            [{'name': 'class', 'value': 'sister'},
             {'name': 'id', 'value': 'link2'},
             {'name': 'string', 'value': 'Bobby'}])
    )
    # example code of adding clickable tags. Refer to dom_analyzer.py
    # DomAnalyzer.add_clickable_tags(Tag('button', {'type': 'reset'}))
    '''

    # (Optional) Write log to file.
    file_handler = logging.FileHandler(os.path.join(config.get_path('root'), 'log.txt'))
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    executor = B2gExecutor(config.get_app_name(), config.get_app_id())
    crawler = B2gCrawler(config, executor)

    logger.info('Start crawling, depth %d', config.get_max_depth())

    # Generate automata and the statistics by crawling. For loading automata from file:
    # automata = Automata(fname='test_data/automata-example.json')
    automata, invariant_violation, num_clickables = crawler.run()

    # save the automata and config to file
    automata.save(config)
    config.save('config.json')

    # generate html report
    Visualizer.generate_html('web', os.path.join(config.get_path('root'), config.get_automata_fname()))

    # text report
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
    logger.info('Total clickables found: %d (True: %d, False: %d, Unexamined: %d)',
                num_clickables['unexamined'] + num_clickables['true'] + num_clickables['false'],
                num_clickables['true'],
                num_clickables['false'],
                num_clickables['unexamined'])
    logger.info('Violated invariants: %d', len(invariant_violation))
    for inv in invariant_violation:
        logger.info('state: %s, violated invariant: %s, execution sequence:', inv['state'], inv['name'])
        for clickable in inv['sequence']:
            logger.info('id: %s (xpath: %s)', clickable.get_id(), clickable.get_xpath())

    t_end = time.time()
    logger.info('time elapsed: %f minutes', ((t_end-t_start)/60.0))


if __name__ == '__main__':
    main()
