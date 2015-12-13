#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Generate html for crawling summary, automata, etc.
"""

import shutil
import os
import json
import logging
import time
import HTMLParser
from bs4 import BeautifulSoup
from dom_analyzer import DomAnalyzer

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class Visualizer:
    @classmethod
    # generate state.html and report.html
    def generate_automata(cls, template_dir, dst_dir, automata_file):
        assert os.path.isdir(template_dir) and os.path.exists(template_dir)
        assert os.path.isfile(os.path.join(dst_dir, automata_file)) and os.path.exists(os.path.join(dst_dir, automata_file))
        # copy files from template_dir to the location of the automata file
        src = template_dir
        dst = dst_dir
        cls.copy_files(src, dst, exception_files=['report.html'])
        '''
        for name in os.listdir(src):
            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)
            try:
                if os.path.isdir(srcname):
                    try:
                        shutil.rmtree(dstname)
                    except OSError:
                        pass
                    shutil.copytree(srcname, dstname)
                else:
                    try:
                        os.remove(dstname)
                    except OSError:
                        pass
                    shutil.copy2(srcname, dstname)
            except Exception as e:
                logger.error('Exception: %s in generate_html() of Visualizer', str(e))
        '''

        # parse automata.json, fill the info into state.html
        with open(os.path.join(dst_dir, automata_file)) as f:
            img_div_str = ''
            input_graph_str = '''
            digraph {
            node [rx=5 ry=5 labelStyle="font: 300 14px 'Helvetica Neue', Helvetica"];
            edge [labelStyle="font: 300 14px 'Helvetica Neue', Helvetica"];
            '''
            automata = json.load(f)
            clickable_path = {}
            for state in automata['state']:
                img_div_str += '<img src="' + state['img_path'] + '">\n'
                input_graph_str += state['id'] \
                    + ' [labelType=\"html\" label=\"' + state['id'] \
                    + '<img src=\'' + state['img_path'] + '\'>"];\n'
                for clickable in state['clickable']:
                    clickable_path[state['id'] + '-' + clickable['id']] = clickable['img_path']
                    img_div_str += '<img src="' + clickable['img_path'] + '" alt="' + clickable['id'] + '">\n'
            #print automata['id_prefix']
            for edge in automata['edge']:
                input_graph_str += edge['from'] + '->' + edge['to'] \
                    + '[labelType=\"html\" label=\"<img src=\'' + clickable_path[edge['from'] + '-' + edge['clickable']] \
                    + '\' alt=\'' + edge['clickable'] + '\'>"];\n'
            #print img_div_str
            #print input_graph_str
            input_graph_str += '}'
            with open(os.path.join(dst, 'state.html'), 'r+') as sf:
                soup = BeautifulSoup(sf.read(), 'html.parser')
                img_div = soup.find(id='images')
                img_div.clear()
                img_div.string = img_div_str
                input_graph = soup.find(id='inputGraph')
                input_graph.clear()
                input_graph.string = input_graph_str
                sf.seek(0)
                sf.truncate()
                sf.write(HTMLParser.HTMLParser().unescape(str(soup)))

    @classmethod
    def generate_report(cls, template_dir, dst_dir, automata_file, depth, num_clickables, form_list, invariant_violation, elapsed_min):
        assert os.path.isdir(template_dir) and os.path.exists(template_dir)
        assert os.path.isdir(dst_dir) and os.path.exists(dst_dir)
        assert os.path.isfile(os.path.join(dst_dir, automata_file)) and os.path.exists(os.path.join(dst_dir, automata_file))
        cls.copy_files(template_dir, dst_dir, exception_files=['state.html'])

        state_path = {}  # dict of state_id to file_path for generating report
        with open(os.path.join(dst_dir, automata_file)) as f:
            automata = json.load(f)
            for state in automata['state']:
                state_path[state['id']] = state['img_path']

        with open(os.path.join(dst_dir, 'report.html'), 'r+') as rf:
            soup = BeautifulSoup(rf.read(), 'html.parser')

            # update summary section
            soup.find(id='depth').string = str(depth)
            soup.find(id='time').string = str(elapsed_min)
            soup.find(id='total').string = str(num_clickables['unexamined'] + num_clickables['true'] + num_clickables['false'])
            soup.find(id='true').string = str(num_clickables['true'])
            soup.find(id='false').string = str(num_clickables['false'])
            soup.find(id='unexamined').string = str(num_clickables['unexamined'])
            soup.find(id='form-summary').string = str(len(form_list))
            soup.find(id='invariant-summary').string = str(len(invariant_violation))

            # generate forms section
            '''
            example content: (refer to web/report.html)
            <div class="row">
              <div class="col-md-4"><img src="http://placekitten.com/160/255"></div>
              <div class="col-md-8">
                state: 3, form-id: b2g-monkey-5 (xpath: //html/body/form[1]) <br />
                input_value: <br />
                type: text, id: id_username (xpath: //html/body/form[1]/p[1]/input[1]), value: pjshzzza <br />
                type: password, id: id_password (xpath: //html/body/form[1]/p[2]/input[1]), value: !qaz2wsX <br />
                path-to-form: <br />
                id: b2g-monkey-3 (xpath: //html/body/p[3]/a[1]) <br />
                clickables in the form: <br />
                id: b2g-monkey-6 (xpath: //html/body/form[1]/p[3]/a[1]) <br />
                id: b2g-monkey-7 (xpath: //html/body/form[1]/p[3]/button[1]) <br />
              </div>
            </div>
            '''
            soup.find(id='form').find('div').decompose()
            form_list = sorted(form_list, key=lambda k: int(k['state']), reverse=True)
            for f in form_list:
                state_url = state_path[str(f['state'])]
                fid = 'None' if f['form'].get_id().startswith(DomAnalyzer.serial_prefix) else f['form'].get_id()
                log_str = 'State: %s, form-id: %s (xpath: %s) <br />' % (f['state'], fid, f['form'].get_xpath())
                log_str += 'Input values: <br />'
                for the_input in f['form'].get_inputs():
                    log_str += 'Type: %s, id: %s (xpath: %s), value: %s <br />' % (
                        the_input.get_type(), the_input.get_id(), the_input.get_xpath(), the_input.get_value())
                log_str += 'Path to the form: <br />'
                for clickable in f['execution_seq']:
                    cid = 'None' if clickable.get_id().startswith(DomAnalyzer.serial_prefix) else clickable.get_id()
                    log_str += 'id: %s (xpath: %s) <br />' % (cid, clickable.get_xpath())
                log_str += 'Clickables in the form: <br />'
                for clickable in f['clickable']:
                    cid = 'None' if clickable.get_id().startswith(DomAnalyzer.serial_prefix) else clickable.get_id()
                    log_str += 'id: %s (xpath: %s) <br />' % (cid, clickable.get_xpath())
                form_section = '<div class="row"><div class="col-md-4"><img src="' + state_url + '"></div>'
                form_section += '<div class="col-md-8">' + log_str + '</div></div><hr />'
                soup.find(id='form').find('h3').insert_after(form_section)

            # generate invariant section
            '''
            example content: (refer to web/report.html)
            <div class="row">
              <div class="col-md-4"><img src="http://placekitten.com/160/255"></div>
              <div class="col-md-8">
                state: 2, violated invariant: {"name": "file-not-found"} <br />
                execution sequence: <br />
                id: b2g-monkey-2 (xpath: //html/body/p[2]/a[1]) <br />
              </div>
            </div>
            '''
            soup.find(id='invariant').find('div').decompose()
            invariant_violation = sorted(invariant_violation, key=lambda k: int(k['state']), reverse=True)
            for inv in invariant_violation:
                state_url = state_path[str(inv['state'])]
                log_str = 'State: %s, violated invariant: %s <br />' % (inv['state'], inv['name'])
                log_str += 'Execution sequence: <br />'
                for clickable in inv['sequence']:
                    cid = 'None' if clickable.get_id().startswith(DomAnalyzer.serial_prefix) else clickable.get_id()
                    log_str += 'id: %s (xpath: %s) <br />' % (cid, clickable.get_xpath())
                inv_section = '<div class="row"><div class="col-md-4"><img src="' + state_url + '"></div>'
                inv_section += '<div class="col-md-8">' + log_str + '</div></div><hr />'
                soup.find(id='invariant').find('h3').insert_after(inv_section)

            rf.seek(0)
            rf.truncate()
            rf.write(HTMLParser.HTMLParser().unescape(str(soup)))

    @classmethod
    def copy_files(cls, dir_from, dir_to, exception_files=None):
        assert os.path.isdir(dir_from) and os.path.exists(dir_from)
        assert os.path.isdir(dir_to) and os.path.exists(dir_to)
        for name in os.listdir(dir_from):
            if name in exception_files:
                continue
            srcname = os.path.join(dir_from, name)
            dstname = os.path.join(dir_to, name)

            try:
                if os.path.isdir(srcname):
                    try:
                        shutil.rmtree(dstname)
                    except OSError:
                        pass
                    time.sleep(0.5)  # wait for unfinished file operation
                    shutil.copytree(srcname, dstname)
                else:
                    try:
                        os.remove(dstname)
                    except OSError:
                        pass
                    time.sleep(0.5)  # wait for unfinished file operation
                    shutil.copy2(srcname, dstname)
            except Exception as e:
                logger.error('Exception: %s in copy_files() of Visualizer', e)
