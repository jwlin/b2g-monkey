#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Provide a web page for the automata
"""

import shutil
import os
import json
import logging
import HTMLParser
from bs4 import BeautifulSoup

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class Visualizer:
    @classmethod
    def generate_html(cls, template_dir, automata_file):
        assert os.path.isdir(template_dir) and os.path.exists(template_dir)
        assert os.path.isfile(automata_file) and os.path.exists(automata_file)
        # copy files from template_dir to the location of the automata file
        src = template_dir
        dst = os.path.dirname(os.path.realpath(automata_file))
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

        # parse automata.json, fill the info into state.html
        with open(automata_file) as f:
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
                sf.write(HTMLParser.HTMLParser().unescape(soup.prettify()))