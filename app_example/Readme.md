# Install the example apps in /test-apps

## Install the apps in b2g desktop client

Tested on b2g-43.0a1.en-US.win32, Windows 10

Refer to <https://developer.mozilla.org/en-US/Marketplace/Options/Self_publishing>

Modify the following paths:
* `manifestUrl` in `install.html`
* `package_path` in `manifest.webapp` (Unzip `app-example.zip`, do modification and then zip it again.)
* `package_path` in `app-example.manifest` 

Note: `manifest.webapp` (in `app-example.zip`) and `app-example.manifest` must be **identical**.

put `app-example.manifest`, `app-example.zip` and `install.html` on accessible web host (localhost works), and then link to <http://yourhost/path/to/install.html> with the browser in b2g simulator to install. **Keep the displayed app-id**.

## Install the apps in WebIDE simulator
<https://developer.mozilla.org/en-US/docs/Tools/WebIDE/Running_and_debugging_apps>