# Getting Started

(Tested on Windows 10, b2g-43.0a1.en-US.win32 and Python 2.7.9)

Install prerequisite
```
cd path/to/b2g-monkey
pip install -r requirement.txt (Admin privilege may be needed)
```

Download [b2g desktop client](https://ftp.mozilla.org/pub/b2g/nightly/latest-maple/b2g-43.0a1.en-US.win32.zip) (b2g-43.0a1.en-US.win32)
Unzip it and run `b2g.exe`. Simulator should be opened. Finish the first-time settings, and then go to

1. Settings -> Display, to turn off Screen Timeout 
2. Settings -> Screen Lock, to disable the screen lock

Install You apps in the simulator. Keep the App Name and App ID and replace the values in `config = B2gConfiguration('APP_NAME', 'APP_ID')` in `controller.py` with yours. (By default the Contact App would be crawled.)

To start crawling, run
```
python controller.py
```

Find logs, captured doms and screenshot in `trace/YYYYMMDDHHMMSS/`