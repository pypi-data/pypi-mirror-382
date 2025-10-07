# Testionary

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A library providing tools to inspect dicionaries during testing. 

## Installation

Using pip:
```
pip install testionary
```
or using uv for project management:

```
uv add testionary
```

## Usage

### Read and Modified attributes
Accessing a value using e.g. the `[]`-operator or `dict.get()` method will cause the key to be added to `TrackingDict.accessed_keys`. Setting a value e.g. using assignment together with the `[]`-operator will get tracked using `TrackingDict.modified_keys`. Here is a small example:
```python
# My library code:
>>> def set_danger(enemy):
...     if enemy["type"] == "Rabbit":
...         enemy["danger"] = 9000


# My test:
>>> from testionary.tracking_dict import TrackingDict
>>> tracked_dict = TrackingDict({"type": "Rabbit", "danger": 42})
>>> set_danger(tracked_dict)
>>> "type" in tracked_dict.accessed_keys
True
>>> "danger" in tracked_dict.modified_keys
True

```

#### Tracked Access methods
- `[]`
- `.get`


#### Tracked Modification methods
- `[] =`
- `.update()`
- `|=`

### Iteration
When iterating over dictionary, e.g. when using dictionary comprehension, you might be accessing a few or all of the items. However, in these scenarios it is common to actually interate over all the key-value pairs while filtering on some condition. Instead of attemting to track each access with `TrackingDict.accessed_keys`, a boolean attribute, `TrackingDict.has_been_iterated`, is used instead. Here is an example of this being used:
```python
# Libray code
>>> def vals_as_str(_dict):
...    return {k: str(v) for k,v in _dict.items()}

# My test:
>>> from testionary.tracking_dict import TrackingDict

>>> tracked_dict = TrackingDict({"type": "Rabbit", "danger": 42, "hp": 100, "armor": 100})
>>> vals_as_str(tracked_dict)
{'type': 'Rabbit', 'danger': '42', 'hp': '100', 'armor': '100'}
>>> tracked_dict.has_been_iterated
True

```

#### Tracked Iteration Methods
- `__iter__()` called by `iter()` and `for`
- `__contains__()`, called by `in` operator in e.g. `if "key" in my_dict`
- `.keys()`
- `.values()`
- `.items()`

For `.keys()`, `.values()`, and `.items()`, iteration is assumed following calls to these methods. The returned dict-views are not inspected.
