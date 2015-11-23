#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Module docstring
"""

import os, sys, json, posixpath, time
from os.path import relpath
from configuration import B2gConfiguration,SeleniumConfiguration
from automata import Automata, State
from clickable import Clickable, InputField, SelectField
from executor import SeleniumExecutor
from crawler import B2gCrawler, SeleniumCrawler
from visualizer import Visualizer
from dom_analyzer import DomAnalyzer
from normalizer import AttributeNormalizer, TagNormalizer, TagWithAttributeNormalizer
#from connecter import mysqlConnect

def B2gmain():
    config = B2gConfiguration('Contacts', 'contacts')
    config.set_max_depth(3)
    executor = B2gExecutor(config.get_app_name(), config.get_app_id())

    crawler = B2gCrawler(config, executor)
    automata = crawler.run()
    save_automata(automata, config)
    Visualizer.generate_html('web', os.path.join(config.get_path('root'), config.get_automata_fname()))
    save_config(config, 'config.json')


#==============================================================================================================================
# Selenium Web Driver
#==============================================================================================================================
def SeleniumMain():
    print "connect to mysql"
    connect  = mysqlConnect("localhost", "jeff", "zj4bj3jo37788", "test")
    _url, _deep, _time = connect.get_submit_by_id(sys.argv[1])
    _web_inputs = connect.get_all_inputs_by_id(sys.argv[1])

    print "setting config..."
    config = SeleniumConfiguration(3, _url, sys.argv[2])
    config.set_max_depth(_deep)
    config.set_simple_clickable_tags()
    config.set_simple_inputs_tags()
    config.set_simple_normalizers()
    
    print "setting executor..."
    executor = SeleniumExecutor(config.get_browserID(), config.get_url())
    
    print "setting crawler..."
    automata = Automata()
    crawler = SeleniumCrawler(config, executor, automata)    
    
    print "crawler start run..."
    automata = crawler.run()
    crawler.close()
    
    print "end! save automata..."
    automata.save_automata(config)
    Visualizer.generate_html('web', os.path.join(config.get_path('root'), config.get_automata_fname()))
    save_config(config, 'config.json')

def debugTestMain():
    #config = SeleniumConfiguration(2, "http://sso.cloud.edu.tw/SSO/SSOLogin.do?returnUrl=https://ups.moe.edu.tw/index.php")
    #config = SeleniumConfiguration(2, "https://www.cloudopenlab.org.tw/index.do")
    #config = SeleniumConfiguration(2, "http://140.112.42.143/nothing/main.html")
    #config.set_max_depth(1)
    print "setting config..."
    config = SeleniumConfiguration(2, "http://sso.cloud.edu.tw/SSO/SSOLogin.do?returnUrl=https://ups.moe.edu.tw/index.php")
    config.set_max_depth(1)
    config.set_domains(["http://sso.cloud.edu.tw/SSO/SSOLogin.do?returnUrl=https://ups.moe.edu.tw/index.php", "https://ups.moe.edu.tw/index.php"])
    config.set_automata_fname('automata.json')

    config.set_simple_clickable_tags()
    config.set_simple_inputs_tags()
    config.set_simple_normalizers()
    config.set_normalizer( TagWithAttributeNormalizer("div", "class", "calendarToday") )
    config.set_normalizer( TagWithAttributeNormalizer("table", None, u"人氣", 'contains') )
    config.set_normalizer( TagWithAttributeNormalizer("table", "class", "clmonth") )
    config.set_normalizer( TagNormalizer(['iframe']) )
    config.set_normalizer( TagWithAttributeNormalizer("a", "href", "http://cloud.edu.tw/?token") )
    print "setting executor..."
    executor = SeleniumExecutor(config.get_browserID(), config.get_url())    
    print "setting crawler..."
    automata = Automata()
    crawler = SeleniumCrawler(config, executor, automata)    
    print "crawler start run..."
    crawler.run()
    crawler.close()    
    print "end! save automata..."
    automata.save_automata(config, config.get_automata_fname())
    Visualizer.generate_html('web', os.path.join(config.get_path('root'), config.get_automata_fname()))
    config.save_config('config.json')
#==============================================================================================================================

def load_automata(fname):
    t_start = time.time()
    assert os.path.isfile(fname) and os.path.exists(fname)
    automata = Automata()
    with open(fname) as f:
        data = json.load(f)
        for state in data['state']:
            with open(os.path.join(os.path.dirname(os.path.realpath(fname)), state['dom_path']), 'r') as df:
                s = State(df.read())
                s.set_id(state['id'])
                for clickable in state['clickable']:
                    c = Clickable(clickable['id'], clickable['xpath'], clickable['tag'])
                    s.add_clickable(c)
                automata.add_state(s)
        for edge in data['edge']:
            from_state = automata.get_state_by_id(edge['from'])
            to_state = automata.get_state_by_id(edge['to'])
            clickable = from_state.get_clickable_by_id(edge['clickable'])
            assert from_state and to_state and clickable
            automata.add_edge(from_state, to_state, clickable)
    print 'automata loaded. loading time: %f sec' % (time.time() - t_start)
    return automata


def load_config(fname):
    t_start = time.time()
    with open(fname) as f:
        data = json.load(f)
        config = B2gConfiguration(data['app_name'], data['app_id'])
        config.set_max_depth(int(data['max_depth']))
        config.set_max_states(int(data['max_states']))
        config.set_sleep_time(int(data['sleep_time']))
        config.set_max_time(int(data['max_time']))
        # ignore the rest ('automata_fname', 'root_path', 'dom_path', 'state_path', 'clickable_path')
        print 'config loaded. loading time: %f sec' % (time.time() - t_start)
    return config

if __name__ == '__main__':
    debugTestMain()
