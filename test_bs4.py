#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Module docstring
"""

html_doc = """
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
"""

html_doc2 = """
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
        <button data-prop="nextButton" data-event="click:onNext" class="sup-info-next-btn recommend" disabled="">
          <span data-l10n-id="setup-info-next">New Btn</span>
        </button>
        </form>
        </body></html>
"""

from bs4 import BeautifulSoup
soup = BeautifulSoup(html_doc, 'html.parser')
soup2 = BeautifulSoup(html_doc2, 'html.parser')
btn1 =  soup.find_all('button')
btn2 = soup2.find_all('button')
for btn in btn2:
    if btn not in btn1:
        print btn
print '------'
for tag in soup.find_all():
    print tag.attrs
    white_listed_attrs = {}
    for attr in tag.attrs:
        if attr in ['disabled']:
            white_listed_attrs[attr] = tag[attr]
    tag.attrs = white_listed_attrs
print str(soup).replace('\n', '')
