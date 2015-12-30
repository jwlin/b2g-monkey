#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Module docstring
"""

import os, sys, json, posixpath, time, codecs, datetime, logging, traceback
from configuration import SeleniumConfiguration, Browser, MutationMethod
from automata import Automata, State
from clickable import Clickable, InputField, SelectField
from executor import SeleniumExecutor
from crawler import SeleniumCrawler
from visualizer import Visualizer
from dom_analyzer import DomAnalyzer
from data_bank import InlineDataBank, MysqlDataBank
from normalizer import AttributeNormalizer, TagNormalizer, TagWithAttributeNormalizer
from connecter import mysqlConnect

#==============================================================================================================================
# Selenium Web Driver
#==============================================================================================================================
def SeleniumMain(web_submit_id, folderpath=None, dirname=None):
    logging.info(" connect to mysql")
    connect  = mysqlConnect("localhost", "jeff", "zj4bj3jo37788", "test")
    _url, _deep, _time = connect.get_submit_by_id(web_submit_id)
    _web_inputs = connect.get_all_inputs_by_id(web_submit_id)

    logging.info(" setting config...")
    config = SeleniumConfiguration(Browser.PhantomJS, _url, folderpath, dirname)
    config.set_max_depth(_deep)
    config.set_simple_clickable_tags()
    config.set_simple_inputs_tags()
    config.set_simple_normalizers()
    
    logging.info(" setting executor...")
    executor = SeleniumExecutor(config.get_browserID(), config.get_url())
    
    logging.info(" setting crawler...")
    automata = Automata()
    databank = MysqlDataBank()
    crawler = SeleniumCrawler(config, executor, automata, databank)
    
    logging.info(" crawler start run...")
    automata = crawler.run()
    crawler.close()
    
    logging.info(" end! save automata...")
    automata.save_automata(config)
    automata.save_traces(config)
    Visualizer.generate_html('web', os.path.join(config.get_path('root'), config.get_automata_fname()))
    config.save_config('config.json')

def SeleniumMutationTrace(folderpath, dirname, config_fname, traces_fname, trace_id, method_id, max_traces):
    logging.info(" loading config...")
    config = load_config(config_fname)
    config.set_folderpath(folderpath)
    config.set_dirname(dirname)
    config.set_mutant_trace(traces_fname, trace_id)
    config.set_mutation_method(method_id)
    config.set_max_mutation_traces(max_traces)

    logging.info(" setting executor...")
    executor = SeleniumExecutor(config.get_browserID(), config.get_url())

    logging.info(" setting crawler...")
    automata = Automata()
    databank = MysqlDataBank()
    crawler = SeleniumCrawler(config, executor, automata, databank)

    logging.info(" crawler start run...")
    crawler.run_mutant()

    logging.info(" end! save automata...")
    automata.save_traces(config)
    automata.save_automata(config)    
    Visualizer.generate_html('web', os.path.join(config.get_path('root'), config.get_automata_fname()))

def debugTestMain():
    #config = SeleniumConfiguration(2, "http://sso.cloud.edu.tw/SSO/SSOLogin.do?returnUrl=https://ups.moe.edu.tw/index.php")
    #config.set_domains(["http://sso.cloud.edu.tw/SSO/SSOLogin.do?returnUrl=https://ups.moe.edu.tw/index.php", "https://ups.moe.edu.tw/index.php"])
    #config = SeleniumConfiguration(2, "https://www.cloudopenlab.org.tw/index.do")
    #config = SeleniumConfiguration(2, "http://140.112.42.143/nothing/main.html")
    #config.set_max_depth(1)
    logging.info(" setting config...")
    config = SeleniumConfiguration(Browser.FireFox, "http://140.112.42.143/nothing/main.html")
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

    logging.info(" setting executor...")
    executor = SeleniumExecutor(config.get_browserID(), config.get_url())
    logging.info(" setting crawler...")
    automata = Automata()
    databank = InlineDataBank() 
    crawler = SeleniumCrawler(config, executor, automata, databank)
    logging.info(" crawler start run...")
    crawler.run()
    crawler.close()
    logging.info(" end! save automata...")
    automata.save_traces(config)
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
    with codecs.open(fname, encoding='utf-8') as f:
        data = json.load(f)
        browser = Browser.PhantomJS if data['browser_id'] == 3 \
            else Browser.Chrome if data['browser_id'] == 2 else Browser.FireFox
        config = SeleniumConfiguration(browser, data['url'], data['dirname'], data['folderpath'])
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


def make_dir(folderpath=None, dirname=None):
    dirname = datetime.datetime.now().strftime('%Y%m%d%H%M%S') if not dirname else dirname
    root_path = os.path.join('trace', dirname ) if not folderpath else os.path.join( folderpath, dirname )
    file_path = {
        'root': root_path,
        'dom': os.path.join(root_path, 'dom'),
        'state': os.path.join(root_path, 'screenshot', 'state')
    }
    for key, value in file_path.iteritems():
        abs_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), value)
        if not os.path.exists(abs_path):
            os.makedirs(abs_path)
    make_log(folderpath, dirname)

def make_log(folderpath, dirname):
    filename = os.path.join( os.path.dirname(os.path.realpath(__file__)), os.path.join(folderpath, dirname, 'log.txt') )
    level = logging.INFO
    format = '[%(asctime)s]<%(levelname)s>: %(message)s'
    logging.basicConfig(filename=filename, level=level, format=format)

def end_log(filename, complete, note):
    with open(filename, 'w') as end_file:
        end = {
            'complete': complete,
            'note': note
        }
        json.dump(end, end_file, indent=2, sort_keys=True, ensure_ascii=False)

if __name__ == '__main__':
    if len(sys.argv)> 1:
        #default mode
        if  sys.argv[1] == '1':
            try:
                if not os.path.isdir(sys.argv[3]) or not os.path.exists(sys.argv[3]):
                    raise ValueError('not found folder')
                if os.path.exists( os.path.join(sys.argv[3], sys.argv[4]) ):
                    raise ValueError('dirname already exist')
                make_dir(sys.argv[3], sys.argv[4])
                try:
                    SeleniumMain(sys.argv[2], sys.argv[3], sys.argv[4])
                    end_log( os.path.join(sys.argv[3], sys.argv[4], 'end.json'), True, 'done')
                except Exception as e:
                    end_log( os.path.join(sys.argv[3], sys.argv[4], 'end.json'),False, traceback.format_exc())
            except Exception as e:  
                with open("default_log.txt","a") as main_log:
                    main_log.write( '\n[MAIN ERROR-%s]: %s' % (datetime.datetime.now().strftime('%Y%m%d%H%M%S'), traceback.format_exc()) )
        #mutant mode
        elif sys.argv[1] == '2':
            try:
                if os.path.exists( os.path.join(sys.argv[2], sys.argv[3]) ):
                    raise ValueError('dirname already exist')
                if not os.path.isfile(sys.argv[4]) or not os.path.exists(sys.argv[4]):
                    raise ValueError('not found config file')
                if not os.path.isfile(sys.argv[5]) or not os.path.exists(sys.argv[5]):
                    raise ValueError('not found traces file')
                make_dir(sys.argv[2], sys.argv[3])
                try:
                    SeleniumMutationTrace(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8])
                    end_log( os.path.join(sys.argv[2], sys.argv[3], 'end.json'), True, 'done')
                except Exception as e:
                    end_log( os.path.join(sys.argv[2], sys.argv[3], 'end.json'),False, str(e)+traceback.format_exc())
            except Exception as e:
                with open("mutant_log.txt","a") as main_log:
                    main_log.write( '[MAIN ERROR-%s]: %s' % (datetime.datetime.now().strftime('%Y%m%d%H%M%S'), traceback.format_exc()) )
        else:
            make_dir()
            debugTestMain()
    else:
        print "[WARNIING] needed argv: <Mode=1> <WebSubmitID> <FolderPath> <Dirname> default crawling "
        print "                        <Mode=2> <FolderPath> <Dirname> <ConfigFile> <TracesFile> <TraceID> <MutationMethodID> <MaxTraces> mutant crawling "