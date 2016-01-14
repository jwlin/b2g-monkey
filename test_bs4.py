
from bs4 import BeautifulSoup   

dom = \
"""
<input id="x">
<div id="a"><input id="y"></div>
<a/>
<input id="z"/>
<div id="b"><a id="z"></div>

"""
soup = BeautifulSoup(dom,"html5lib")
for i in soup.find_all('input'):
    print "=============="
    print i