#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Module docstring
"""

import time
from marionette import Marionette
from marionette_driver import Wait
import unittest


class TestContacts(unittest.TestCase):

    def unlock_screen(self):
        self.marionette.execute_script('window.wrappedJSObject.lockScreen.unlock();')

    def kill_all(self):
        self.marionette.switch_to_frame()
        self.marionette.execute_async_script("""
             // Kills all running apps, except the homescreen.
             function killAll() {
               let manager = window.wrappedJSObject.appWindowManager;

               let apps = manager.getApps();
               for (let id in apps) {
                 let origin = apps[id].origin;
                 if (origin.indexOf('verticalhome') == -1) {
                   manager.kill(origin);
                 }
               }
             };
             killAll();
             // return true so execute_async_script knows the script is complete
             marionetteScriptFinished(true);
            """)

    def setUp(self):

         # Create the client for this session. Assuming you're using the default port on a Marionette instance running locally
        self.marionette = Marionette()
        self.marionette.start_session()

        # Unlock the screen
        #self.unlock_screen()

        # kill all open apps
        self.kill_all()

        # Switch context to the homescreen iframe and tap on the contacts icon
        time.sleep(2)
        home_frame = self.marionette.find_element('css selector', 'div.homescreen iframe')
        self.marionette.switch_to_frame(home_frame)


    def test_add_contacts(self):
        contacts_icon = self.marionette.find_element('xpath', "//div[@class='icon']//span[contains(text(),'Contacts')]")
        contacts_icon.tap()

        # Switch context back to the base frame

        #print self.marionette.page_source
        import base64
        #imgdata = base64.b64decode(self.marionette.screenshot())
        #filename = 'image1.png'  # I assume you have a way of picking unique filenames
        #with open(filename, 'wb') as f:
        #    f.write(imgdata)
        self.marionette.switch_to_frame()
        #print '-----'
        #imgdata = base64.b64decode(self.marionette.screenshot())
        #filename = 'image2.png'  # I assume you have a way of picking unique filenames
        #with open(filename, 'wb') as f:
        #    f.write(imgdata)
        import sys
        #print sys.stdout.encoding
        #print self.marionette.page_source.encode(sys.stdout.encoding, errors='replace')
        #print u'\u232b'.encode('utf-8', 'ignore')#.decode('utf-8')
        #print u'\u232b'.encode('utf-8', 'replace')#.decode('utf-8')
        #print u'\u232b'.encode('utf-8')
        #print self.marionette.page_source.encode(sys.stdout.encoding, 'ignore')
        Wait(self.marionette).until(lambda m: m.find_element('css selector', "iframe[data-url*='contacts']").is_displayed())


        # Switch context to the contacts app
        contacts_frame = self.marionette.find_element('css selector', "iframe[data-url*='contacts']")
        self.marionette.switch_to_frame(contacts_frame)

        # Tap [+] to add a new Contact
        self.marionette.find_element('id', 'add-contact-button').tap()
        Wait(self.marionette).until(lambda m: m.find_element('id', 'save-button').location['y']== 0)

        # Type name into the fields
        self.marionette.find_element('id', 'givenName').send_keys('John')
        self.marionette.find_element('id', 'familyName').send_keys('Doe')

        # Tap done
        self.marionette.find_element('id', 'save-button').tap()
        Wait(self.marionette).until(lambda m: not m.find_element('id', 'save-button').is_displayed())


    def tearDown(self):
        # Close the Marionette session now that the test is finished
        self.marionette.delete_session()

if __name__ == '__main__':
    unittest.main()