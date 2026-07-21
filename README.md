[![Test](https://img.shields.io/github/actions/workflow/status/FrederikP/ahocorapy/pythontest.yml?branch=master)](https://github.com/FrederikP/ahocorapy/actions)
[![Test Coverage](https://img.shields.io/codecov/c/gh/FrederikP/ahocorapy/master)](https://codecov.io/gh/FrederikP/ahocorapy)
[![Downloads](https://pepy.tech/badge/ahocorapy)](https://pepy.tech/project/ahocorapy)
[![PyPi Version](https://img.shields.io/pypi/v/ahocorapy.svg)](https://pypi.python.org/pypi/ahocorapy)
[![PyPi License](https://img.shields.io/pypi/l/ahocorapy.svg)](https://pypi.python.org/pypi/ahocorapy)
[![PyPi Versions](https://img.shields.io/pypi/pyversions/ahocorapy.svg)](https://pypi.python.org/pypi/ahocorapy)
[![PyPi Wheel](https://img.shields.io/pypi/wheel/ahocorapy.svg)](https://pypi.python.org/pypi/ahocorapy)

# ahocorapy - Fast Many-Keyword Search in Pure Python

ahocorapy is a pure python implementation of the Aho-Corasick Algorithm.
Given a list of keywords one can check if at least one of the keywords exist in a given text in linear time.

## Comparison:

### Why another Aho-Corasick implementation?

We started working on this in the beginning of 2016. Our requirements included unicode support combined with python2.7. That
was impossible with C-extension based libraries (like [pyahocorasick](https://github.com/WojciechMula/pyahocorasick/)). Pure
python libraries were very slow or unusable due to memory explosion. Since then another pure python library was released
[py-aho-corasick](https://github.com/JanFan/py-aho-corasick). The repository also contains some discussion about different
implementations.
There is also [acora](https://github.com/scoder/acora), but it includes the note ('current construction algorithm is not
suitable for really large sets of keywords') which really was the case the last time I tested, because RAM ran out quickly.

### Differences

- Compared to [pyahocorasick](https://github.com/WojciechMula/pyahocorasick/) our library supports unicode in python 2.7 just like [py-aho-corasick](https://github.com/JanFan/py-aho-corasick).
  We don't use any C-Extension so the library is not platform dependant.

- On top of the standard Aho-Corasick longest suffix search, we also perform a shortcutting routine in the end, so
  that our lookup is fast while, the setup takes longer. During set up we go through the states and directly add transitions that are
  "offered" by the longest suffix or their longest suffixes. This leads to faster lookup times, because in the end we only have to
  follow simple transitions and don't have to perform any additional suffix lookup. It also leads to a bigger memory footprint,
  because the number of transitions is higher, because they are all included explicitely and not implicitely hidden by suffix pointers.

- We added a small tool that helps you visualize the resulting graph. This may help understanding the algorithm, if you'd like. See below.

- Fully pickleable (pythons built-in de-/serialization). ahocorapy uses a non-recursive custom implementation for de-/serialization so that even huge keyword trees can be pickled.

### Performance

I compared the two libraries mentioned above with ahocorapy, using a 50,000 keywords long list and two input texts:

- **sparse**: 34,198 characters of text that contain exactly one keyword. This resembles searching ordinary text for a set of names.
- **dense**: 85,578 characters built by concatenating keywords, containing 6,207 matches. This measures the other extreme, where almost every position is part of a match.

The setup process was run once per library and each search was run 100 times. The following results are in seconds (not averaged for the lookup).

You can perform this test yourself using `python tests/ahocorapy_performance_test.py`. (Except for the pure python variant of
pyahocorasick. It's not published on pypi, so those numbers were taken by importing the pure python code from the
[pyahocorasick](https://github.com/WojciechMula/pyahocorasick/) repo at `etc/py/pyahocorasick.py`.)

The pure python libraries were additionally run with pypy.

These are the results:

| Library (Variant)                                    | Setup (1x) | Search sparse (100x) | Search dense (100x) |
| ---------------------------------------------------- | ---------- | -------------------- | ------------------- |
| ahocorapy\*                                          | 0.19s      | 0.02s                | 0.42s               |
| ahocorapy (run with pypy)\*                          | 0.23s      | 0.01s                | 0.28s               |
| pyahocorasick\*                                      | 0.02s      | 0.02s                | 0.08s               |
| pyahocorasick (run with pypy)\*                      | 0.03s      | 0.03s                | 0.15s               |
| pyahocorasick (pure python variant in github repo)\* | 0.10s      | 0.21s                | 0.69s               |
| pyahocorasick (pure python variant, run with pypy)\* | 0.18s      | 0.07s                | 0.30s               |
| py_aho_corasick\*                                    | 0.34s      | 2.05s                | 2.48s               |
| py_aho_corasick (run with pypy)\*                    | 0.45s      | 1.00s                | 1.19s               |

On sparse text ahocorapy is on par with the pyahocorasick C-Extension on CPython, and faster than it on pypy. This is possible
because during setup ahocorapy precomputes the matches to report per state and a regex character class of all symbols that
keywords can start with, which the search loop then uses to skip over stretches of text that cannot contain a keyword start at
C speed. On match-dense text the C-Extension is still clearly faster. Setup takes longer than with pyahocorasick due to the
suffix shortcutting and match precomputation described above. Compared to the other pure python libraries ahocorapy is the
fastest in every discipline.

\* Specs

CPU: Apple M4 Pro

OS: macOS 26.5.2 (Darwin 25.5.0)

CPython: 3.14.5

pypy: PyPy 7.3.23 (Python 3.11.15) with GCC Apple LLVM 21.0.0 (clang-2100.0.123.102)

Library versions: ahocorapy 1.8.0, pyahocorasick 2.3.1, py_aho_corasick 1.1.0

Date tested: 2026-07-21

## Basic Usage:

### Installation

```
pip install ahocorapy
```

### Creation of the Search Tree

```python
from ahocorapy.keywordtree import KeywordTree
kwtree = KeywordTree(case_insensitive=True)
kwtree.add('malaga')
kwtree.add('lacrosse')
kwtree.add('mallorca')
kwtree.add('mallorca bella')
kwtree.add('orca')
kwtree.finalize()
```

### Searching

```python
result = kwtree.search('My favorite islands are malaga and sylt.')
print(result)
```

Prints :

```python
('malaga', 24)
```

The search_all method returns a generator for all keywords found, or None if there is none.

```python
results = kwtree.search_all('malheur on mallorca bellacrosse')
for result in results:
    print(result)
```

Prints :

```python
('mallorca', 11)
('orca', 15)
('mallorca bella', 11)
('lacrosse', 23)
```

### Arbitrary Sequences of Arbitrary Symbols

ahocorapy is not limited to strings. Keywords and search input can be **any
sequence of hashable symbols**. Internally the tree never assumes anything about
the symbols beyond that they can be used as dictionary keys, so it works with
tuples of integers, byte values, lists of tokens and more.

The only requirements are:

- Each **symbol** (an element of the sequence) must be hashable.
- Each **keyword** and the **search input** must be an iterable that also
  supports `len()` (needed to compute match start indices). Strings, tuples,
  lists and bytes all qualify.

For example, using tuples of integers as keywords:

```python
from ahocorapy.keywordtree import KeywordTree
kwtree = KeywordTree()
kwtree.add((1, 2, 3))
kwtree.add((2, 3, 4))
kwtree.finalize()

result = kwtree.search((9, 1, 2, 3, 4, 8))
print(result)
```

Prints:

```python
((1, 2, 3), 1)
```

Using lists of string tokens enables word-level (instead of character-level)
matching:

```python
kwtree = KeywordTree()
kwtree.add(['hello', 'world'])
kwtree.finalize()

result = kwtree.search(['say', 'hello', 'world', 'now'])
print(result)
```

Prints:

```python
(['hello', 'world'], 1)
```

A note on `bytes`: in Python 3 iterating over a `bytes` object yields integers,
whereas in Python 2 `bytes` is an alias for `str` and yields 1-character
strings. Matching works in both cases, but the symbol type differs between the
two Python versions.

The `case_insensitive=True` option is string-specific (it calls `.lower()` on
keywords and input) and therefore only applies when your symbols are strings.

### Thread Safety

The construction of the tree is currently NOT thread safe. That means `add`ing shouldn't be called multiple times concurrently. Behavior is undefined.

After `finalize` is called you can use the `search` functionality on the same tree from multiple threads at the same time. So that part is thread safe.

## Drawing Graph

You can print the underlying graph with the Visualizer class.
This feature requires a working pygraphviz library installed.

```python
from ahocorapy_visualizer.visualizer import Visualizer
visualizer = Visualizer()
visualizer.draw('readme_example.png', kwtree)
```

The resulting .png of the graph looks like this:

![graph for kwtree](https://raw.githubusercontent.com/FrederikP/ahocorapy/master/img/readme_example.png "Keyword Tree")
