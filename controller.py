#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Module docstring
"""

import os, sys, json, posixpath, time, codecs
from os.path import relpath
from configuration import SeleniumConfiguration
from automata import Automata, State
from clickable import Clickable, InputField, SelectField
from executor import SeleniumExecutor
from crawler import SeleniumCrawler
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
def SeleniumMain(web_submit_id, dirname=None, folderpath=None):
    print "connect to mysql"
    connect  = mysqlConnect("localhost", "jeff", "zj4bj3jo37788", "test")
    _url, _deep, _time = connect.get_submit_by_id(web_submit_id)
    _web_inputs = connect.get_all_inputs_by_id(web_submit_id)

    print "setting config..."
    config = SeleniumConfiguration(3, _url, dirname, folderpath)
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
    #config.set_domains(["http://sso.cloud.edu.tw/SSO/SSOLogin.do?returnUrl=https://ups.moe.edu.tw/index.php", "https://ups.moe.edu.tw/index.php"])
    #config = SeleniumConfiguration(2, "https://www.cloudopenlab.org.tw/index.do")
    #config = SeleniumConfiguration(2, "http://140.112.42.143/nothing/main.html")
    #config.set_max_depth(1)
    print "setting config..."
    config = SeleniumConfiguration(2, "http://140.112.42.143/nothing/main.html")
    config.set_max_depth(3)
    config.set_max_states(100)
    config.set_automata_fname('automata.json')
    config.set_traces_fname('traces.json')
    config.set_frame_tags(['iframe'])
    config.set_dom_inside_iframe(True)
    config.set_simple_clickable_tags()
    config.set_simple_inputs_tags()
    config.set_simple_normalizers()
    #ups.moe.edu.tw
    config.set_tags_normalizer( ['iframe'] )
    config.set_tag_with_attribute_normalizer( "div", "class", "calendarToday" )
    config.set_tag_with_attribute_normalizer( "table", None, u"人氣", 'contains')
    config.set_tag_with_attribute_normalizer( "table", "class", "clmonth")
    config.set_tag_with_attribute_normalizer( "td", "class", "viewNum" )
    #jibako
    config.set_tags_normalizer( ["script","style"] )
    config.set_tag_with_attribute_normalizer( "div", 'class', 'fotorama', 'contains' )
    config.set_tag_with_attribute_normalizer( "div", 'class', 'player', 'contains' )
    config.set_path_ignore_tags( ['img', 'hr', 'br'] )
    #member.cht.com.tw/
    config.set_tag_with_attribute_normalizer( "div", 'style', 'visibility: hidden', 'contains' )
    config.set_tag_with_attribute_normalizer( "div", 'style', 'none', 'contains' )
    config.set_tag_with_attribute_normalizer( "div", 'class', 'ui-widget', 'contains' )

    print "setting executor..."
    executor = SeleniumExecutor(config.get_browserID(), config.get_url())    
    print "setting crawler..."
    automata = Automata()
    crawler = SeleniumCrawler(config, executor, automata)    
    print "crawler start run..."
    crawler.run()
    crawler.close()    
    print "end! save automata..."
    automata.save_traces(config)
    automata.save_automata(config, config.get_automata_fname())
    Visualizer.generate_html('web', os.path.join(config.get_path('root'), config.get_automata_fname()))
    config.save_config('config.json')

def SeleniumMutationTrace(folderpath, config_fname, traces_fname, trace_id):
    print "loading config..."
    config = load_config(config_fname)
    config.set_mutant_trace(traces_fname, trace_id)
    print "setting executor..."
    executor = SeleniumExecutor(config.get_browserID(), config.get_url())    
    print "setting crawler..."
    automata = Automata()
    crawler = SeleniumCrawler(config, executor, automata)    
    print "crawler start run..."
    crawler.run_mutant()
    crawler.close()    
    print "end! save automata..."
    automata.save_traces(config)
    automata.save_automata(config)
    Visualizer.generate_html('web', os.path.join(config.get_path('root'), config.get_automata_fname()))
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
    with codecs.open(fname, encoding='utf-8') as f:
        data = json.load(f)
        config = SeleniumConfiguration(data['browser_id'], data['url'], data['dirname'], data['folderpath'])
        config.set_max_depth(int(data['max_depth']))
        config.set_max_states(int(data['max_states']))
        config.set_sleep_time(int(data['sleep_time']))
        config.set_max_time(int(data['max_time']))
        # ignore the rest ('automata_fname', 'root_path', 'dom_path', 'state_path', 'clickable_path')
        config.set_automata_fname(data['automata_fname'])
        config.set_domains(data['domains'])
        config.set_dom_inside_iframe(data['dom_inside_iframe'])
        config.set_traces_fname(data['traces_fname'])

        if data['analyzer']['simple_clickable_tags']:
            config.set_simple_clickable_tags()
        if data['analyzer']['simple_normalizers']:
            config.set_simple_normalizers()
        if data['analyzer']['simple_inputs_tags']:
            config.set_simple_inputs_tags()
        for tag in data['analyzer']['clickable_tags']:
            config.set_clickable_tags(tag['tag'], tag['attr'], tag['value'])
        for tag in data['analyzer']['inputs_tags']:
            config.set_inputs_tags(tag)
        config.set_path_ignore_tags(data['analyzer']['path_ignore_tags'])
        config.set_tags_normalizer(data['analyzer']['tag_normalizers'])
        config.set_attributes_normalizer(data['analyzer']['attributes_normalizer'])
        for tag in data['analyzer']['tag_with_attribute_normalizers']:
            config.set_tag_with_attribute_normalizer(tag['tag'], tag['attr'], tag['value'], tag['mode'])

        if data['before_trace_fname']:
            config.set_before_trace(data['before_trace_fname'])
        print 'config loaded. loading time: %f sec' % (time.time() - t_start)
    return config

if __name__ == '__main__':
    if len(sys.argv)> 1:
        #default mode
        if  sys.argv[1] == '1':
            try:
                assert not os.path.exists( os.path.join(sys.argv[4], sys.argv[3]) )
                SeleniumMain(sys.argv[2], sys.argv[3], sys.argv[4])
            except Exception as e:                
                print '[MAIN ERROR]: %s' % (str(e))
        #mutant mode
        elif sys.argv[1] == '2':
            #try:
                #assert os.path.isdir(sys.argv[2]) and os.path.exists(sys.argv[2])
                #assert os.path.isfile(sys.argv[3]) and os.path.exists(sys.argv[3])
                #assert os.path.isfile(sys.argv[4]) and os.path.exists(sys.argv[3])
                SeleniumMutationTrace(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
            #except Exception as e:
            #    print '[MAIN ERROR]: %s' % (str(e))
        else:
            debugTestMain()
    else:
        print "[WARNIING] needed argv: <Mode=1> <WebSubmitID> <Dirname> <FolderPath> default crawling "
        print "                        <Mode=2> <FolderPath> <ConfigFile> <TracesFile> <TraceID> mutant crawling "