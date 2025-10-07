[![Test](https://github.com/apmadsen/delegate-pattern/actions/workflows/python-test.yml/badge.svg)](https://github.com/apmadsen/delegate-pattern/actions/workflows/python-test.yml)
[![Coverage](https://github.com/apmadsen/delegate-pattern/actions/workflows/python-test-coverage.yml/badge.svg)](https://github.com/apmadsen/delegate-pattern/actions/workflows/python-test-coverage.yml)
[![Stable Version](https://img.shields.io/pypi/v/delegate-pattern?label=stable&sort=semver&color=blue)](https://github.com/apmadsen/delegate-pattern/releases)
![Pre-release Version](https://img.shields.io/github/v/release/apmadsen/delegate-pattern?label=pre-release&include_prereleases&sort=semver&color=blue)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/delegate-pattern)
[![PyPI Downloads](https://static.pepy.tech/badge/delegate-pattern/week)](https://pepy.tech/projects/delegate-pattern)

# delegate-pattern: Python implementation of the Delegation Pattern.

delegate-pattern provides a basic implementation of the well-known Delegation Pattern.

## What is delegation

Delegation is a pattern in object oriented programming where a class (delegator) delegates responsibilities to one or more delegates.

This allows for greater code reusability and reduced class complexity and may help adhering to the DRY (Do not Repeat Yourself) and SoC (Separation of Concerns) principles.



## Example

Consider a trivial task of delegating the printing of an objects name to the console. Here the delegator `SomeClass` delegates the task to the delegate `PrintNameDelegate` which is not much more than a function wrapped in a class.

The delegate class is always initialized with an argument specifying its delegator, and while this example shows the use of a protocol class called `NamedClassProtocol`, this is merely included for convenience, and will not be enforced at runtime. In fact the type of `delegator` can be anything, but delegate constructors cannot have any other arguments.

Note that it's strongly recommended to use weak references to the delegator in the delegate constructor.

```python
from typing import Protocol
from weakref import ref
from delegate.pattern import delegate

class NamedClassProtocol(Protocol):
    _name: str

class PrintNameDelegate:
    # this is a stateful delegate because its constructor
    # takes a 'delegator' argument

    def __init__(self, delegator: NamedClassProtocol):
        self.__delegator = delegator

    def __call__(self):
        print(self.__delegator._name)

class NamePropertyDelegate:
    # this is a stateless delegate because it has no
    # constructor which takes a 'delegator' argument

    def __get__(self, delegator: NamedClassProtocol) -> str:
        return delegator._name

    def __set__(self, delegator: NamedClassProtocol, value: str):
        delegator._name = value

class SomeClass:
    _name: str
    def __init__(self, name: str) -> None:
        self._name = name

    name_printer = delegate(PrintNameDelegate) # => PrintNameDelegate instance
    name = delegate(NamePropertyDelegate, str) # => string getter

some_instance = SomeClass("Neo")
some_instance.name_printer() # prints Neo

name = some_instance.name # => Neo
some_instance.name = "Trinity"
new_name = some_instance.name # => Trinity
```

## Full documentation

[Go to documentation](https://github.com/apmadsen/delegate-pattern/blob/main/docs/documentation.md)
