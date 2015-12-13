#Ver. 0.1.0

b2g-monkey is a python-based crawler for Firefox OS (codename: Boot to Gecko, or b2g) apps.  It automatically explores the app under test by clicking candidate clickables with corresponding text input on encountered screens. You can use it to:

* Explore the interface, clickables and input of the app under test, and see the state transition graph.
* Find and fill all forms with random or pre-saved input (For now, it only deals with the input fields in forms.)
* Detect invariants when crawling the app.

# Getting Started

(Tested on Windows 10, Firefox 42.0 (w/ Simulator 2.2), b2g-43.0a1.en-US.win32 and Python 2.7.9)

Clone the project. Than install the prerequisite:

```
pip install -r path/to/b2g-monkey/requirement.txt (Admin privilege may be needed)
```

There are two ways to activate b2g simulator:

1. Install Firefox and [WebIDE](https://developer.mozilla.org/en-US/docs/Tools/WebIDE). In WebIDE, install b2g Simulator 2.2, and [install your app into the simulator](https://developer.mozilla.org/en-US/docs/Tools/WebIDE/Running_and_debugging_apps). Keep the App Name and App ID.

2. Download [b2g desktop client](https://ftp.mozilla.org/pub/b2g/nightly/latest-maple/b2g-43.0a1.en-US.win32.zip) (b2g-43.0a1.en-US.win32). Unzip it and run `b2g.exe` to activate the simulator. Skip the first time settings, and then go to:
  1. Settings -> Display, to turn off Screen Timeout
  2. Settings -> Screen Lock, to disable the screen lock

  [Install You apps in the b2g desktop client](https://github.com/jwlin/b2g-monkey/tree/master/app_example). Keep the App Name and App ID.

In `controller.py`, replace the values in

```
config = B2gConfiguration('APP_NAME', 'APP_ID')
```

with yours. (By default the Contact App would be crawled.)

To start crawling, run

```
python controller.py
```

Find `report.html`, `state.html`, logs, captured doms and screenshots in

```
path/to/b2g-monkey/trace/YYYYMMDDHHMMSS/
```

# Customization

## Clickable tags

By default four tags are treated as candidate clickables when parsing the dom (refer to `dom_analyzer.py`):

```
Tag('a')
Tag('button')
Tag('input', {'type': 'submit'})
Tag('input', {'type': 'button'})
```

You can get, add or remove tags from this list of `DomAnalyzer`. For example, to add tag:

```
DomAnalyzer.add_clickable_tags(Tag('button', {'type': 'reset'}))
```

Then all buttons like `<button type="reset">Click Me</button>` will be treated as candidate clickables.

## Invariant

Invariants are rules to check every time a new state (screen) is discovered. If any invariant is found violated in a state, the crawler will stop digging and display execution sequences to the invariant in report. By default there is only one invariant: `FileNotFoundInvariant` (refer to `invariant.py`). You can add `StringInvariant` or `TagInvariant`  into `configuration` like this:

```
from invariant import TagInvariant, StringInvariant
config.add_invariant(
    TagInvariant('a',
			[{'name': 'class', 'value': 'sister'},
             {'name': 'id', 'value': 'link2'},
             {'name': 'string', 'value': 'Bobby'}])
)
config.add_invariant(
    StringInvariant("display this page because the file cannot be found.")
)
```

## Normalizer

Normalizers are tag removers or string filters applied to DOM document when comparing DOMs. By default there are three normalizers in `DomAnalyzer` (refer to `dom_analyzer.py`):

```
_normalizers = [
        TagNormalizer(['head']),
        AttributeNormalizer('class'),
        TagWithAttributeNormalizer('section', 'class', 'hide')
    ]
```

You have to manually add or delete normalizers in the list. There are four normalizers (refer to `normalizer.py` and `NormalizerTestCase` in `test.py`)

`AttributeNormalizer(attr_list)`: All attributes not in `attr_list` will be deleted.
`TagContentNormalizer(tag_list)`: Content in tag will be deleted for tag in `tag_list`.
`TagNormalizer(tag_list)`: Content in tag and tag itself will be deleted for tag in `tag_list`.
`TagWithAttributeNormalizer`: Remove tag with: 1. matched name, attr containing value; 2. matched name, tag content containing value