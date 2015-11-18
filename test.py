#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Module docstring
"""

import unittest, os
from automata import Automata, State
from clickable import Clickable, FormField, InputField
from crawler import B2gCrawler
from executor import B2gExecutor
from configuration import B2gConfiguration
from dom_analyzer import DomAnalyzer
from bs4 import BeautifulSoup
from normalizer import AttributeNormalizer, TagContentNormalizer, TagNormalizer, TagWithAttributeNormalizer
from visualizer import Visualizer


class AutomataTestCase(unittest.TestCase):
    def setUp(self):
        dom1 = '''
            <!DOCTYPE html>
            <html lang="en">
            <head> <meta charset="UTF-8"> <title></title> </head>
            <body>dom1</body>
            </html>
        '''
        state = State(dom1)
        self.automata = Automata()
        self.automata.add_state(state)
        self.assertEqual(len(self.automata.get_states()), 1)
        self.assertEqual(self.automata.get_initial_state().get_id(), self.automata.get_current_state().get_id())
        self.assertEqual(self.automata.get_current_state().get_id(), '0')

        # test adding and removing inputs and forms
        form1 = FormField('form1')
        form1.add_input(InputField('username', '//*[@id="username"]', 'castman'))
        form1.add_input(InputField('password', '', 'p@ssw0rd'))
        form1.add_input(InputField('password', '', 'p@ssw0rd'))
        self.assertEqual(len(form1.get_inputs()), 2)
        form1.remove_input(InputField('username', '//*[@id="username"]', 'castman'))
        self.assertEqual(len(form1.get_inputs()), 1)

        form2 = FormField('', '//*[@id="lst-ib"]')
        clickable = Clickable('', '//*[@id="btn1"]')
        clickable.add_form(form1)
        clickable.add_form(FormField('form1'))
        clickable.add_form(form2)
        self.assertEqual(len(clickable.get_forms()), 2)
        clickable.remove_form(FormField('', '//*[@id="lst-ib"]'))
        self.assertEqual(len(clickable.get_forms()), 1)

        # add the clickable into state 0
        self.automata.get_current_state().add_clickable(clickable)

    def test_automata(self):
        dom1 = self.automata.get_current_state().get_dom()
        dom1 += '<custom></custom>'
        dom2 = dom1
        state1 = State(dom1)
        state2 = State(dom2)
        self.automata.add_state(state1)
        state3, is_newly_added = self.automata.add_state(state2)
        self.assertTrue(state3 == state1)
        self.assertFalse(is_newly_added)
        self.assertEqual(len(self.automata.get_states()), 2)

        clickable = self.automata.get_current_state().get_clickables()[0]
        clickable2 = Clickable('', '//html/body/button[3]')
        self.assertEqual(len(self.automata.get_current_state().get_clickables()), 1)
        self.automata.get_current_state().add_clickable(clickable)
        self.automata.get_current_state().add_clickable(clickable2)
        self.automata.get_current_state().add_clickable(clickable2)
        self.assertEqual(len(self.automata.get_current_state().get_clickables()), 2)

        self.automata.add_edge(self.automata.get_current_state(), state1, self.automata.get_current_state().get_clickables()[0])
        self.assertEqual(len(self.automata.get_edges()), 1)

        state1.add_prev_state(self.automata.get_current_state())

        self.assertEqual(self.automata.get_current_state().get_id(), '0')
        self.automata.change_state(state1)
        self.assertEqual(self.automata.get_initial_state().get_id(), '0')
        self.assertEqual(self.automata.get_current_state().get_id(), '1')
        self.assertEqual(self.automata.get_current_state().get_prev_states()[0].get_id(), '0')

        '''
        for s in self.automata.get_states():
            print s
            for c in s.get_clickables():
                print c
                for f in c.get_forms():
                    print f
                    for _i in f.get_inputs():
                        print _i
        for (state_from, state_to, clickable, cost) in self.automata.get_edges():
            print state_from, state_to, clickable, cost
        '''

    def test_get_shortest_path(self):
        automata = Automata()
        state0 = State('state0')
        state1 = State('state1')
        state2 = State('state2')
        state3 = State('state3')
        state4 = State('state4')
        state5 = State('state5')
        state6 = State('state6')
        automata.add_state(state0)
        automata.add_state(state1)
        automata.add_state(state2)
        automata.add_state(state3)
        automata.add_state(state4)
        automata.add_state(state5)
        automata.add_state(state6)
        automata.add_edge(state0, state1, Clickable('0-1'))
        automata.add_edge(state0, state2, Clickable('0-2'))
        automata.add_edge(state0, state3, Clickable('0-3'))
        automata.add_edge(state2, state4, Clickable('2-4'))
        automata.add_edge(state4, state5, Clickable('4-5'))
        automata.add_edge(state3, state5, Clickable('3-5'))
        automata.add_edge(state3, state5, Clickable('5-0'))
        automata.add_edge(state5, state6, Clickable('5-6'))
        self.assertEqual(automata.get_shortest_path(state0), [])
        edges = automata.get_shortest_path(state6)
        # 0-3, 3-5, 5-6
        self.assertEqual([int(e[0].get_id()) for e in edges], [0, 3, 5])
        #for e in edges:
        #    print e[0].get_id(), e[1].get_id(), e[2].get_id()

'''
class ExecutorTestCase(unittest.TestCase):
    def test_executor(self):
        app_name = 'E-Mail'  # "name": "Ba-ttery"
        app_id = 'email'  # '6a961774-d6fd-469a-9e53-78f31114a076'
        executor = B2gExecutor(app_name, app_id)
        executor.restart_app()
        #analyzer = DomAnalyzer()
        #analyzer.get_clickables(executor.get_source())
'''


class DomAnalyzerTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_xpath(self):
        html_doc = '''
        <html><body>
          <div></div>
          <div>
            <form>
              <input><button></button>
            </form>
          </div>
        </body></html>
        '''
        soup = BeautifulSoup(html_doc, 'html.parser')
        form = soup.find('form')
        self.assertEqual(DomAnalyzer._get_xpath(form), '//html/body/div[2]/form[1]')

    def test_add_clickable(self):
        dom = '''
        <html><body>
        <form data-prop="formNode" class="sup-form sup-account-form">
        <p>
        <input placeholder="Your name" data-prop="nameNode" data-event="input:onInfoInput" class="sup-info-name" data-l10n-id="setup-info-name" x-inputmode="verbatim" inputmode="verbatim" dir="auto" required="" type="text">
        <button type="reset"></button>
        </p>
        <p>
        <input placeholder="someone@example.com" data-prop="emailNode" data-event="input:onInfoInput" class="sup-info-email" data-l10n-id="setup-info-email" dir="auto" required="" type="email">
        <button type="reset"></button>
        </p>
        <p>
        <button data-prop="nextButton" data-event="click:onNext" class="sup-info-next-btn recommend" disabled="">
          <span data-l10n-id="setup-info-next">Next</span>
        </button>
        <button data-prop="manualConfig" data-event="click:onClickManualConfig" class="sup-manual-config-btn" disabled="" data-l10n-id="setup-manual-config2">Manual setup</button>
        </p>
        </form>
        </body></html>
        '''
        clickables = DomAnalyzer.get_clickables(dom)
        self.assertEqual(len(clickables), 4)
        self.assertEqual(len(clickables[3].get_forms()), 1)
        self.assertEqual(len(clickables[3].get_forms()[0].get_inputs()), 2)
        self.assertEqual(clickables[3].get_forms()[0].get_inputs()[1].get_xpath(), '//html/body/form[1]/p[2]/input[1]')
        self.assertEqual(clickables[3].get_forms()[0].get_inputs()[1].get_type(), 'email')
        
        '''
            for click in clickables:
                print click
                for form in click.get_forms():
                    print form
                    for inp in form.get_inputs():
                        print inp
                print '==='
        '''


class ConfigurationTestCase(unittest.TestCase):
    def test_b2g_configuration(self):
        app_name = 'app-name'
        app_id = 'app-id'
        init_max_depth = 2
        init_max_states = 0
        init_max_time = 0
        config = B2gConfiguration(app_name, app_id)
        self.assertEqual(config.get_app_name(), app_name)
        self.assertEqual(config.get_app_id(), app_id)
        self.assertEqual(config.get_max_depth(), init_max_depth)
        self.assertEqual(config.get_max_states(), init_max_states)
        self.assertEqual(config.get_max_time(), init_max_time)


class ControllerTestCase(unittest.TestCase):
    def test_controller(self):
        import controller
        controller.main()


class DataBankTestCase(unittest.TestCase):
    def test_inline_databank(self):
        from data_bank import InlineDataBank
        InlineDataBank.add_item('email', 'user3@email.com')
        InlineDataBank.add_item('email', 'user3@email.com')  # duplicated adding
        InlineDataBank.remove_item('email', 'abc@mail.com')  # invalid removal
        InlineDataBank.remove_item('email', 'user1@example.com')  # valid removal
        self.assertEqual(len(InlineDataBank.get_data('email')), 2)
        InlineDataBank.add_item('phone-number', '0912345678')   # add data into a new type
        InlineDataBank.add_item('phone-number', '0987654321')
        self.assertEqual(len(InlineDataBank.get_types()), 4)
        self.assertEqual(len(InlineDataBank.get_data('phone-number')), 2)
        self.assertIsNone(InlineDataBank.get_data('text'))


class NormalizerTestCase(unittest.TestCase):
    def test_normalizer(self):
        dom = '''
        <button data-event="click:onNext" class="sup-info-next-btn recommend">
        <span data-l10n-id="setup-info-next">Next</span>
        </button>
        <button data-prop="manualConfig"  disabled="" data-l10n-id="setup-manual-config2">Manual setup</button>
        '''
        normalizer = AttributeNormalizer(['disabled'])
        dom = normalizer.normalize(dom)
        self.assertEqual(dom, '<button><span>Next</span></button><button disabled="">Manual setup</button>')

        normalizer = TagContentNormalizer(['button'])
        dom = normalizer.normalize(dom)
        self.assertEqual(dom, '<button></button><button disabled=""></button>')

        normalizer = TagNormalizer(['button'])
        dom = normalizer.normalize(dom)
        self.assertEqual(dom, '')

        dom = '''
        <body>
        <p class="title"><b>The Dormouse story</b></p>
        <a class="sister" href="http://example.com/elsie" id="link1">Elsie</a>
        <table><tr><td>文字</td><td>Wtf</td></tr></table>
        </body>
        '''
        normalizer = TagWithAttributeNormalizer('a', 'href', 'http://example.co')
        self.assertEqual(
            normalizer.normalize(dom),
            '<body><p class="title"><b>The Dormouse story</b></p><table><tr><td>文字</td><td>Wtf</td></tr></table></body>'
        )
        normalizer = TagWithAttributeNormalizer('table', None, u'文字')
        self.assertEqual(
            normalizer.normalize(dom),
            '<body><p class="title"><b>The Dormouse story</b></p><a class="sister" href="http://example.com/elsie" id="link1">Elsie</a></body>'
        )


    def demo(self):
        with open('C:\\Users\\Jun-Wei\\Desktop\\20151102214729\\dom\\2.txt') as f:
            dom1 = f.read()

        with open('C:\\Users\\Jun-Wei\\Desktop\\20151102214729\\dom\\3.txt') as f:
            dom2 = f.read()
        normalizer = TagNormalizer(['head', 'canvas'])
        dom1 = normalizer.normalize(dom1)
        dom2 = normalizer.normalize(dom2)
        normalizer = AttributeNormalizer('class')
        dom1 = normalizer.normalize(dom1)
        dom2 = normalizer.normalize(dom2)
        #normalizer = TagContentNormalizer()
        #dom1 = normalizer.normalize(dom1)
        #dom2 = normalizer.normalize(dom2)
        print dom1==dom2


class VisualizerTestCase(unittest.TestCase):
    def test_testvisualizer(self):
        from visualizer import Visualizer
        Visualizer.generate_html(
            'web',
            'trace/example-contact-depth-2/automata.json'
        )


if __name__ == '__main__':
    unittest.main()
