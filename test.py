#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Module docstring
"""

import unittest, os
from automata import Automata, State
from clickable import Clickable,  InputField
from crawler import B2gCrawler
from configuration import B2gConfiguration
from dom_analyzer import DomAnalyzer
from bs4 import BeautifulSoup
from normalizer import AttributeNormalizer, TagContentNormalizer, TagNormalizer, TagWithAttributeNormalizer
from visualizer import Visualizer

class NormalizerTestCase(unittest.TestCase):
    def test_normalizer(self):

        dom = '''
        <body><p class="title"><b>The Dormouse story</b></p>
        <div>
        <a class="sister" href="http://example.com/elsie" id="link1">Elsie</a>
        <a class="sister" href="http://example2.com/anna" id="link2">Anna</a>
        <table><tr><td>文字</td><td>Wtf</td></tr></table>
        <table><tr><td>Wtf</td><td>文字</td></tr></table>
        </div>
        </body>
        '''
        normalizer = TagWithAttributeNormalizer('a', 'href', 'http://example.co')
        self.assertEqual(
            normalizer.normalize(dom),
            '<body><p class="title"><b>The Dormouse story</b></p>'\
            '<div>'\
            '<a class="sister" href="http://example2.com/anna" id="link2">Anna</a>'\
            '<table><tr><td>文字</td><td>Wtf</td></tr></table>'\
            '<table><tr><td>Wtf</td><td>文字</td></tr></table></div></body>'
        )
        normalizer = TagWithAttributeNormalizer('table', None, u'文字')
        self.assertEqual(
            normalizer.normalize(dom),
            '<body><p class="title"><b>The Dormouse story</b></p>'\
            '<div>'\
            '<a class="sister" href="http://example.com/elsie" id="link1">Elsie</a>'\
            '<a class="sister" href="http://example2.com/anna" id="link2">Anna</a>'\
            '</div></body>'
        )

        dom = '''
        <div class="calendarToday">
                    2015-11-17 18:28:36
                </div>
        '''
        normalizer = TagWithAttributeNormalizer('div', 'class', 'calendarToday')
        self.assertEqual(
            normalizer.normalize(dom),
            ''
        )




if __name__ == '__main__':
    unittest.main()
