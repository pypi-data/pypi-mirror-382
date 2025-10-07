# pyright: basic
# ruff: noqa
from typing import Any
from pytest import raises as assert_raises, fixture
from weakref import WeakKeyDictionary, ref
import gc


from delegate.pattern.core.compat import is_stateful_delegate

class StatelessDelegate:
    def __init__(self):
        pass

class StatefulDelegate:
    def __init__(self, delegator: object):
        self.delegator = delegator

class StatelessDelegateWithNew:
    def __new__(cls):
        pass
    def __init__(self):
        pass

class StatefulDelegateWithNew:
    def __new__(cls, delegator: object):
        inst = object.__new__(cls)
        inst.__init__(delegator)
        return inst
    def __init__(self, delegator: object):
        self.delegator = delegator


def test_is_stateful_delegate():
    assert not is_stateful_delegate(StatelessDelegate)
    assert is_stateful_delegate(StatefulDelegate)

    assert not is_stateful_delegate(StatelessDelegateWithNew)
    assert is_stateful_delegate(StatefulDelegateWithNew)
