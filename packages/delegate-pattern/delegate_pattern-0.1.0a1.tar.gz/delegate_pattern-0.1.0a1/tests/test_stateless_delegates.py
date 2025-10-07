# pyright: basic
# ruff: noqa
from typing import Any
from pytest import raises as assert_raises, fixture
from weakref import WeakKeyDictionary, ref
import gc

from delegate.pattern.core.delegate import ATTR
from delegate.pattern.core.compat import is_stateful_delegate
from delegate.pattern.protocols import ProtocolError
from delegate.pattern import Delegate, DelegatorError, delegate
from delegate.pattern.core.protocols.stateless_delegate_protocol import StatelessDelegateProtocol
from delegate.pattern.core.protocols.stateful_delegate_protocol import StatefulDelegateProtocol

class SomeDelegate:
    def __init__(self):
        pass

class SomeOtherDelegate:
    def __init__(self):
        pass

def test_checks():

    assert not is_stateful_delegate(SomeDelegate)
    assert not is_stateful_delegate(SomeOtherDelegate)

def test_single_instance():
    assert delegate(SomeDelegate) is Delegate[SomeDelegate]()

    dlg1 = delegate(SomeDelegate)
    dlg2 = delegate(SomeDelegate)
    dlg3 = delegate(SomeOtherDelegate)
    dlg4 = delegate(SomeOtherDelegate)

    # Delegate is a singleinstance generic class, so there
    # should be 2 distinct instances
    assert dlg1 is dlg2
    assert dlg3 is dlg4
    assert dlg1 is not dlg3

    class Class:
        Something = delegate(SomeDelegate)
        Something2 = delegate(SomeDelegate)

    # since Delegate is a singleton generic class
    # both attributes should point to the same instance
    assert Class.Something is Class.Something2

    inst = Class()

    # same goes for the instances
    assert inst.Something is inst.Something2
    assert inst.Something is not Class.Something
    assert inst.Something is not Class.Something2

    inst2 = Class()
    assert inst.Something is inst2.Something



def test_delegate():

    class Class:
        Something = Delegate[SomeDelegate]()

    inst = Class()

    assert isinstance(inst.Something, SomeDelegate)

    with assert_raises(AttributeError):
        inst.Something = Delegate[SomeOtherDelegate]() # pyright: ignore[reportAttributeAccessIssue]


def test_multiple_instances():
    class Class1:
        Something = delegate(SomeDelegate)

    inst1 = Class1()
    inst2 = Class1()

    assert isinstance(Class1.Something, Delegate)
    assert isinstance(inst1.Something, SomeDelegate)
    assert isinstance(inst2.Something, SomeDelegate)

    delegates = getattr(Class1, ATTR)

    assert isinstance(delegates, WeakKeyDictionary)

    # since both delegates share the same protocol, they should be the same instance
    assert Class1.Something == tuple(delegates.keys())[0]


def test_same_event_multiple_classes():
    class Class1:
        Something = delegate(SomeDelegate)

    class Class2:
        Something = delegate(SomeDelegate)

    inst1 = Class1()
    inst2 = Class2()

    assert Class1.Something is Class2.Something # should still be singleinstance
    assert Class1.Something is not inst1.Something is not inst2.Something

    delegates1 = getattr(inst1, ATTR)
    delegates2 = getattr(inst2, ATTR)

    # since both both delegates share the same protocol, they should be the same instance
    assert Class1.Something == tuple(delegates1.keys())[0] == tuple(delegates2.keys())[0]

    # since instances are of different classes, the protocol instances should not be the same
    assert tuple(delegates1.values())[0] is not tuple(delegates2.values())[0]

    x=0


def test_passthrough_delegates():
    from typing import Protocol

    class NamedClassProtocol(Protocol):
        _name: str

    class NamePropertyDelegate:
        def __init__(self, delegator: NamedClassProtocol):
            self.delegator = delegator

        def __get__(self) -> str:
            return self.delegator._name

        def __set__(self, value: str):
            self.delegator._name = value


    class SomeClass:
        _name: str
        def __init__(self, name: str) -> None:
            self._name = name

        name = delegate(NamePropertyDelegate, str)

    some_instance = SomeClass("Neo")

    assert some_instance.name == "Neo"
    some_instance.name = "Trinity"
    assert some_instance.name == "Trinity"

    class SomeClass1:
        _name: str
        def __init__(self, name: str) -> None:
            self._name = name

        name = delegate(SomeDelegate, str) # pyright: ignore[reportArgumentType]

    some_instance1 = SomeClass1("Morpheus")

    with assert_raises(ProtocolError):
        name = some_instance1.name

    with assert_raises(ProtocolError):
        some_instance1.name = "Tank"

    with assert_raises(ProtocolError):
        del some_instance1.name

def test_garbage_collection():
    class OtherDelegate:
        def __init__(self, delegator: object):
            self.delegator = delegator

    class Class1:
        Delegate = delegate(OtherDelegate)


    dlg = ref(Class1.Delegate)
    refs_before_gc = len(gc.get_referrers(dlg()))

    inst1 = Class1()
    inst1 = None
    del Class1

    gc.collect()
    gc.collect()

    assert refs_before_gc > 0
    assert dlg() is None


def test_readme_example1():
    from delegate.pattern import delegate

    class SayHelloDelegate:
        def __call__(self) -> str:
            return "Hello world"

    class Class1:
        dlg = delegate(SayHelloDelegate)

    inst = Class1()
    assert "Hello world" == inst.dlg() # => 'Hello world'


def test_readme_example2():
    from delegate.pattern import delegate

    class PropertyDelegate:
        def __init__(self):
            self.prop = ""

        def __get__(self, delegator: object) -> str:
            return self.prop

        def __set__(self, delegator: object, value: str):
            self.prop = value

        def __delete__(self, delegator: object):
            self.prop = ""

    class Class1:
        dlg = delegate(PropertyDelegate, str)

    inst = Class1()
    assert "" == inst.dlg # => ''
    inst.dlg = "Some value"
    assert "Some value" == inst.dlg # => 'Some value'
    del inst.dlg
    assert "" == inst.dlg


def test_readme_example3():
    from typing import Protocol
    from weakref import ref
    from delegate.pattern import delegate

    class NamedClassProtocol(Protocol):
        _name: str

    class PrintNameDelegate:
        def __init__(self, delegator: NamedClassProtocol):
            self.__delegator = delegator

        def __call__(self):
            print(self.__delegator._name)

    class NamePropertyDelegate:
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