/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this file,
 * You can obtain one at http://mozilla.org/MPL/2.0/. */

'use strict';
/* global marionetteScriptFinished, pair, mozContact, i */
/* global waitFor, aContacts */
/* exported pair, discovery, GaiaDataLayer */
/* jshint -W083 */

var GaiaDataLayer = {

  getBluetoothDefaultAdapter: function() {
    var bluetooth = window.navigator.mozBluetooth;
    if (bluetooth.defaultAdapter) {
      return bluetooth.defaultAdapter;
    } else {
      return bluetooth.getAdapters()[0];
    }
  },

  setBluetooth: function(aState) {
    var adapter = this.getBluetoothDefaultAdapter();

    if (adapter.state == aState) {
      console.log('bluetooth already ' + aState);
      marionetteScriptFinished(true);
      return;
    }

    waitFor(
      function() {
        console.log('bluetooth ' + aState);
        marionetteScriptFinished(true);
      },
      function() {
        console.log('bluetooth enable status: ' + adapter.state);

        // Wait for the adapter state to become 'disabled' or 'enabled'
        if (adapter.state === 'disabling' || adapter.state === 'enabling') {
          return false;
        }

        if (adapter.state != aState) {
          console.log('trying to make bluetooth ' + aState);
          if (aState === 'enabled') {
            adapter.enable();
          } else {
            adapter.disable();
          }
          return false;
        }

        return adapter.state === aState;
      }
    );
  },

  disableBluetooth: function() {
    this.setBluetooth('disabled');
  },

  enableBluetooth: function() {
    this.setBluetooth('enabled');
  },

  insertContact: function(aContact) {
    // requires the 'contacts-create' permission
    if (aContact.photo) {
      var blob = GaiaDataLayer.base64ToBlob(aContact.photo, 'image/jpg');
      aContact.photo = [blob];
    }

    var contact = new mozContact(aContact);
    var req = window.navigator.mozContacts.save(contact);
    req.onsuccess = function() {
      console.log('success saving contact');
      marionetteScriptFinished(true);
    };
    req.onerror = function() {
      console.error('error saving contact', req.error.name);
      marionetteScriptFinished(false);
    };
  },

  insertSIMContact: function(aType, aContact) {

    // Get 1st SIM
    var iccId = window.navigator.mozIccManager.iccIds[0];
    var icc = window.navigator.mozIccManager.getIccById(iccId);

    var simContact = new window.mozContact(aContact);
    if ('id' in aContact) {
      simContact.id = aContact.id;
    }

    var req = icc.updateContact(aType, simContact);
    req.onsuccess = function() {
      console.log('success saving contact to SIM');
      marionetteScriptFinished(req.result);
    };
    req.onerror = function() {
      console.error('error saving contact to SIM', req.error.name);
      marionetteScriptFinished(false);
    };
  },


  deleteSIMContact: function(aType, aId) {

    // Get 1st SIM
    var iccId = window.navigator.mozIccManager.iccIds[0];
    var icc = window.navigator.mozIccManager.getIccById(iccId);

    var aContact = new mozContact();
    aContact.id = aId;

    var req = icc.updateContact(aType, aContact);
    req.onsuccess = function() {
      console.log('success removing contact from SIM');
      marionetteScriptFinished(true);
    };
    req.onerror = function() {
      console.error('error removing contact from SIM', req.error.name);
      marionetteScriptFinished(false);
    };
  },


  getAllContacts: function(aCallback) {
    // requires 'contacts-read' permission
    var callback = aCallback || marionetteScriptFinished;
    var req = window.navigator.mozContacts.find({});
    req.onsuccess = function() {
      console.log('success finding contacts');
      callback(req.result);
    };
    req.onerror = function() {
      console.error('error finding contacts ' + req.error.name);
      callback([]);
    };
  },

  getSIMContacts: function(aType, aCallback) {
    var type = aType || 'adn';
    var callback = aCallback || marionetteScriptFinished;
    var icc = navigator.mozIccManager;

    // See bug 932134
    // To keep all tests passed while introducing multi-sim APIs, in bug 928325
    // we do the following check. Remove it after the APIs land.
    if (icc && icc.iccIds && icc.iccIds[0]) {
      icc = icc.getIccById(icc.iccIds[0]);
    }
    var req = icc.readContacts(type);
    req.onsuccess = function() {
      console.log('success finding ' + type + ' contacts');
      callback(req.result);
    };
    req.onerror = function() {
      console.error('error finding ' + type + ' contacts ' + req.error.name);
      callback([]);
    };
  },

  removeAllContacts: function() {
    var self = this;
    this.getAllContacts(function(aContacts) {
      if (aContacts.length > 0) {
        var contactsLength = aContacts.length;
        var done = 0;
        for (var i = 0; i < contactsLength; i++) {
          self.removeContact(aContacts[i], function() {
            if (++done === contactsLength) {
              marionetteScriptFinished(true);
            }
          });
        }
      }
      else {
        console.log('no contacts to remove');
          marionetteScriptFinished(true);
      }
    });
  },

  removeContact: function(aContact, aCallback) {
    // requires the 'contacts-write' persmission
    var callback = aCallback || marionetteScriptFinished;
    console.log('removing contact with id \'' + aContact.id + '\'');
    var req = window.navigator.mozContacts.remove(aContact);
    req.onsuccess = function() {
      console.log('success removing contact with id \'' + aContact.id + '\'');
      callback(true);
    };
    req.onerror = function() {
      console.error('error removing contact with id \'' +
                      aContacts[i].id + '\'');
      callback(false);
    };
  },

  getSetting: function(aName, aCallback) {
    // requires the 'settings-read' and 'settings-api-read' permissions
    var callback = aCallback || marionetteScriptFinished;
    var req = window.navigator.mozSettings.createLock().get(aName);
    req.onsuccess = function() {
      console.log('setting retrieved');
      let result = aName === '*' ? req.result : req.result[aName];
      callback(result);
    };
    req.onerror = function() {
      console.log('error getting setting ' + req.error.name);
    };
  },

  setSetting: function(aName, aValue, aReturnOnSuccess) {
    // requires the 'settings-write' and 'settings-api-write' permissions
    var returnOnSuccess = aReturnOnSuccess || aReturnOnSuccess === undefined;
    var setting = {};
    setting[aName] = aValue;
    console.log('setting ' + aName + ' to ' + aValue);
    var lock = window.navigator.mozSettings.createLock();
    var req = lock.set(setting);
    lock.onsettingstransactionsuccess = function() {
      console.log('setting changed');
      if (returnOnSuccess) {
        marionetteScriptFinished(true);
      }
    };
    lock.onsettingstransactionfailure = function() {
      console.log('error changing setting ' + req.error.name);
      marionetteScriptFinished(false);
    };
  },

  connectToWiFi: function(aNetwork, aCallback) {
    var callback = aCallback || marionetteScriptFinished;
    var manager = window.navigator.mozWifiManager;

    if (this.isWiFiConnected(aNetwork)) {
      console.log('already connected to network with ssid \'' +
                  aNetwork.ssid + '\'');
      callback(true);
    }
    else {
      var req;
      if (window.MozWifiNetwork === undefined) {
        req = manager.associate(aNetwork);
      } else {
        req = manager.associate(new window.MozWifiNetwork(aNetwork));
      }

      req.onsuccess = function() {
        console.log('waiting for connection status \'connected\'');
        waitFor(
          function() {
            console.log('success connecting to network with ssid \'' +
                        aNetwork.ssid + '\'');
            callback(true);
          },
          function() {
            console.log('connection status: ' + manager.connection.status);
            return manager.connection.status === 'connected';
          }
        );
      };

      req.onerror = function() {
        console.log('error connecting to network ' + req.error.name);
        callback(false);
      };
    }
  },

  disableWiFi: function() {
    var manager = window.navigator.mozWifiManager;
    if (manager.enabled) {
      waitFor(
        function() { marionetteScriptFinished(true); },
        function() {
          console.log('wifi enabled status: ' + manager.enabled);
          return manager.enabled === false;
      });
      this.setSetting('wifi.enabled', false, false);
    }
    else {
      console.log('wifi already disabled');
      marionetteScriptFinished(true);
    }
  },

  enableWiFi: function() {
    var manager = window.navigator.mozWifiManager;
    if (!manager.enabled) {
      waitFor(
        function() { marionetteScriptFinished(true); },
        function() {
          console.log('wifi enabled status: ' + manager.enabled);
          return manager.enabled === true;
      });
      this.setSetting('wifi.enabled', true, false);
    }
    else {
      console.log('wifi already enabled');
      marionetteScriptFinished(true);
    }
  },

  forgetAllNetworks: function(aCallback) {
    var callback = aCallback || marionetteScriptFinished;
    var self = this;
    this.getKnownNetworks(function(aNetworks) {
      if (aNetworks.length > 0) {
        var networksLength = aNetworks.length;
        var done = 0;
        for (var i = 0; i < networksLength; i++) {
          self.forgetWiFi(aNetworks[i], function() {
            if (++done === networksLength) {
              callback(true);
            }
          }, false);
        }
      }
      else {
        console.log('no known networks to forget');
        callback(true);
      }
    });
  },

  getKnownNetworks: function(aCallback) {
    var callback = aCallback || marionetteScriptFinished;
    var manager = window.navigator.mozWifiManager;
    var req = manager.getKnownNetworks();

    req.onsuccess = function() {
      console.log('success getting known networks');
      callback(req.result);
    };

    req.onerror = function() {
      console.log('error getting known networks ' + req.error.name);
      callback([]);
    };
  },

  forgetWiFi: function(aNetwork, aCallback, aWaitForStatus) {
    var callback = aCallback || marionetteScriptFinished;
    var waitForStatus = aWaitForStatus || 'disconnected';
    var manager = window.navigator.mozWifiManager;
    var req = manager.forget(aNetwork);

    req.onsuccess = function() {
      console.log('success forgetting network with ssid \'' +
                  aNetwork.ssid + '\'');
      if (waitForStatus !== false) {
        console.log('waiting for connection status \'' +
                    waitForStatus + '\'');
        waitFor(
          function() { callback(true); },
          function() {
            console.log('connection status: ' + manager.connection.status);
            return manager.connection.status === waitForStatus;
          }
        );
      }
      else {
        callback(true);
      }
    };

    req.onerror = function() {
      console.log('error forgetting network with ssid \'' +
                    aNetwork.ssid + '\' ' + req.error.name);
      callback(false);
    };
  },

  isWiFiConnected: function(aNetwork) {
    let manager = window.navigator.mozWifiManager;
    let connected = manager.connection.status === 'connected';
    if (connected && aNetwork) {
      return manager.connection.network.ssid === aNetwork.ssid;
    } else {
      return connected;
    }
  },

  getMozTelephonyState: function() {
    return window.navigator.mozTelephony.active.state;
  },

  connectToCellData: function() {
    var manager = window.navigator.mozMobileConnections &&
                  window.navigator.mozMobileConnections[0];

    if (!manager.data.connected) {
      waitFor(
        function() {
          console.log('cell data enabled');
          marionetteScriptFinished(true);
        },
        function() { return manager.data.connected; }
      );
      this.setSetting('ril.data.enabled', true, false);
    }
    else {
      console.log('cell data already connected');
      marionetteScriptFinished(true);
    }
  },

  disableCellData: function() {
    var self = this;
    this.getSetting('ril.data.enabled', function(aCellDataEnabled) {
      var manager = window.navigator.mozMobileConnections &&
                    window.navigator.mozMobileConnections[0];

      if (aCellDataEnabled) {
        waitFor(
          function() {
            console.log('cell data disabled');
            marionetteScriptFinished(true);
          },
          function() { return !manager.data.connected; }
        );
        self.setSetting('ril.data.enabled', false, false);
      }
      else {
        console.log('cell data already disabled');
        marionetteScriptFinished(true);
      }
    });
  },

  getAllPictures: function() {
    this.getFiles('pictures');
  },

  getAllVideos: function() {
    this.getFiles('videos');
  },

  getAllMusic: function() {
    this.getFiles('music');
  },

  getAllSDCardFiles: function() {
    this.getFiles('sdcard');
  },

  getFiles: function(aType, aCallback) {
    var callback = aCallback || marionetteScriptFinished;
    var files = [];
    console.log('getting ' + aType);
    var storage = navigator.getDeviceStorage(aType);
    var req = storage.enumerate();
    req.onsuccess = function() {
      var file = req.result;
      if (file) {
        if (aType === 'music' && file.name.slice(-4) === '.3gp') {
          // 3gp is both music and video; we skip the music definition
          req.continue();
        }
        else {
          // File.name returns a fully qualified path
          files.push({'name': file.name, 'size': file.size});
          req.continue();
        }
      }
      else {
        callback(files);
      }
    };
    req.onerror = function() {
      console.error('failed to enumerate ' + aType + ' ' + req.error.name);
      callback(false);
    };
  },

  sendSMS: function(recipient, content, skipVerification, aCallback) {
    // requires the 'sms' permission and the 'dom.sms.enabled' pref
    var callback = aCallback || marionetteScriptFinished;
    console.log('sending sms message to number: ' + recipient);

    let messageManager = window.navigator.mozMobileMessage;
    let request = messageManager.send(recipient, content);
    if (skipVerification) {
      marionetteScriptFinished(true);
      return;
    }

    request.onsuccess = function(event) {
      var sms = event.target.result;

      waitFor(
        function() { callback(true); },
        function() {
          console.log('sms delivery state: ' + sms.delivery);
          return sms.delivery === 'sent';
        }
      );
    };

    request.onerror = function() {
      console.log('sms message not sent');
      callback(false);
    };
  },

  getAllSms: function(aCallback) {
    // requires the 'sms' permission and the 'dom.sms.enabled' pref
    var callback = aCallback || marionetteScriptFinished;
    console.log('searching for sms messages');

    let sms = window.navigator.mozMobileMessage;

    let msgList = [];
    let cursor = sms.getMessages(null, false);

    cursor.onsuccess = function(event) {
      if(cursor.result) {
        // Add the sms to the list
        msgList.push(cursor.result);
        // Now get the next in the list
        cursor.continue();
      }else{
        // Send back the list
        callback(msgList);
      }
    };

    cursor.onerror = function(event) {
      console.log('sms.getMessages error: ' + event.target.error.name);
      callback(false);
    };
  },

  deleteAllSms: function(aCallback) {
    // requires the 'sms' permission and the 'dom.sms.enabled' pref
    var callback = aCallback || marionetteScriptFinished;
    console.log('searching for sms messages');

    let sms = window.navigator.mozMobileMessage;

    let msgList = [];
    let cursor = sms.getMessages(null, false);

    cursor.onsuccess = function(event) {
      // Check if message was found
      if (cursor.result) {
        msgList.push(cursor.result.id);
        // Now get next message in the list
        cursor.continue();
      } else {
        // No (more) messages found
        if (msgList.length) {
          console.log('found ' + msgList.length + ' sms messages to delete');
          deleteSmsMsgs(msgList);
        } else {
          console.log('zero sms messages found');
          callback(true);
        }
      }
    };

    cursor.onerror = function(event) {
      console.log('sms.getMessages error: ' + event.target.error.name);
      callback(false);
    };

    function deleteSmsMsgs(msgList) {
      let smsId = msgList.shift();
      console.log('deleting sms id: ' + smsId);
      let request = sms.delete(smsId);

      request.onsuccess = function(event) {
        if (event.target.result) {
          // Message deleted, continue until none are left
          if (msgList.length) {
            deleteSmsMsgs(msgList);
          } else {
            // All messages deleted
            console.log('finished deleting all sms messages');
            callback(true);
          }
        } else {
          console.log('sms delete failed');
          callback(false);
        }
      };

      request.onerror = function(event) {
        console.log('sms.delete request returned unexpected error: ' +
                    event.target.error.name);
        callback(false);
      };
    }
  },

  deleteAllAlarms: function() {
    window.wrappedJSObject.AlarmManager.getAlarmList(function(aList) {
      aList.forEach(function(aAlarm) {
         console.log('Deleting alarm with id  \'' + aAlarm.id + '\'');
         window.wrappedJSObject.AlarmManager.delete(aAlarm);
      });
    });
  },

  base64ToBlob: function(base64, mimeType) {
      var binary = atob(base64);
      var len = binary.length;
      var buffer = new ArrayBuffer(len);
      var view = new Uint8Array(buffer);
      for (var i = 0; i < len; i++) {
        view[i] = binary.charCodeAt(i);
      }
      return new Blob([view], {type: mimeType});
  }
};