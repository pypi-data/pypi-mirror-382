from typing import Generic, TypeVar, Any, cast, overload
from typingutils import get_generic_arguments, is_type
from weakref import WeakValueDictionary, WeakKeyDictionary

from delegate.pattern.core.protocols.stateful_delegate_protocol import StatefulDelegateProtocol
from delegate.pattern.core.protocols.stateful_readable_delegate_protocol import StatefulReadableDelegateProtocol
from delegate.pattern.core.protocols.stateful_writable_delegate_protocol import StatefulWritableDelegateProtocol
from delegate.pattern.core.protocols.stateful_deleteable_delegate_protocol import StatefulDeleteableDelegateProtocol
from delegate.pattern.core.protocols.stateless_delegate_protocol import StatelessDelegateProtocol
from delegate.pattern.core.protocols.stateless_readable_delegate_protocol import StatelessReadableDelegateProtocol
from delegate.pattern.core.protocols.stateless_writable_delegate_protocol import StatelessWritableDelegateProtocol
from delegate.pattern.core.protocols.stateless_deleteable_delegate_protocol import StatelessDeleteableDelegateProtocol
from delegate.pattern.core.protocols.protocol_error import ProtocolError
from delegate.pattern.core.delegator_error import DelegatorError
from delegate.pattern.core.compat import is_stateful_delegate

T = TypeVar("T", bound = StatefulDelegateProtocol | StatelessDelegateProtocol)
Tp = TypeVar("Tp", bound = StatefulWritableDelegateProtocol | StatelessWritableDelegateProtocol)
Tout = TypeVar("Tout")

ATTR = "__delegates__"

DELEGATES: WeakValueDictionary[tuple[type[Any], bool], 'Delegate[Any]'] = WeakValueDictionary()

class Delegate(Generic[T]):
    __slots__ = [ "__weakref__", "__delegate_proto", "__is_stateful", "__passthrough" ]
    __delegate_proto: type[T]
    __passthrough: bool

    def __new__(cls, passthrough: bool = False):
        delegate_proto = cast(type[T], get_generic_arguments(cls)[0])

        if dlg := DELEGATES.get((delegate_proto, passthrough)):
            return dlg

        instance = object().__new__(cls)
        instance.__delegate_proto = delegate_proto
        instance.__is_stateful = is_stateful_delegate(delegate_proto)
        instance.__passthrough = passthrough

        DELEGATES[(delegate_proto, passthrough)] = instance
        return instance


    def __get__(self, delegator: object, cls: type[Any]) -> T:
        if delegator is None:
            # __get__ is called on a class instance, and should therefore return it self rather than a delegate
            return self # pyright: ignore[reportReturnType]

        delegate = self.__get_delegate(delegator)

        if self.__passthrough and self.__is_stateful and isinstance(delegate, StatefulReadableDelegateProtocol):
            return delegate.__get__()
        elif self.__passthrough and not self.__is_stateful and isinstance(delegate, StatelessReadableDelegateProtocol):
            return delegate.__get__(delegator)
        elif self.__passthrough:
            raise ProtocolError("Delegate protocol is not a valid ReadableDelegateProtocol")
        else:
            return delegate

    def __get_delegate(self, delegator: object) -> T:
        def get_delegates(obj: Any | type[Any]) -> WeakKeyDictionary[Delegate[T], T]:
            delegates: WeakKeyDictionary[Delegate[T], T] | None = None

            if hasattr(obj, ATTR):
                return cast(WeakKeyDictionary[Delegate[T], T], getattr(obj, ATTR))
            else:
                try:
                    delegates = WeakKeyDictionary()
                    setattr(obj, ATTR, delegates)
                    return delegates
                except AttributeError:
                    if not is_type(obj):
                        check_slots(type(obj)) # pyright: ignore[reportUnknownArgumentType]
                    else:
                        pass # impossible # pragma: no cover
                    raise # pragma: no cover

        if self.__is_stateful:
            delegates = get_delegates(delegator)
            if not ( delegate := delegates.get(self) ):
                delegate = cast(T, cast(type[StatefulDelegateProtocol], self.__delegate_proto)(delegator))
                delegates[self] = delegate

        else:
            delegates = get_delegates(type(delegator))
            if not ( delegate := delegates.get(self) ):
                delegate = cast(T, cast(type[StatelessDelegateProtocol], self.__delegate_proto)())
                delegates[self] = delegate

        return delegate

    def __set__(self, delegator: object, value: Any) -> None:
        delegate = self.__get_delegate(delegator)

        if self.__passthrough and self.__is_stateful and isinstance(delegate, StatefulWritableDelegateProtocol):
            delegate.__set__(value)
            return
        elif self.__passthrough and not self.__is_stateful and isinstance(delegate, StatelessWritableDelegateProtocol):
            delegate.__set__(delegator, value)
            return
        elif self.__passthrough:
            raise ProtocolError("Delegate protocol is not a valid WritableDelegateProtocol")

        if value is delegate:
            pass # pragma: no cover
        else:
            raise AttributeError("Delegate attribute cannot be changed" + str(self.__passthrough) + str(delegate))

    def __delete__(self, delegator: object):
        delegate = self.__get_delegate(delegator)
        if self.__passthrough and self.__is_stateful and isinstance(delegate, StatefulDeleteableDelegateProtocol):
            delegate.__delete__()
        elif self.__passthrough and not self.__is_stateful and isinstance(delegate, StatelessDeleteableDelegateProtocol):
            delegate.__delete__(delegator)
        elif self.__passthrough:
            raise ProtocolError("Delegate protocol is not a valid DeleteableDelegateProtocol")
        pass # pragma: no cover


@overload
def delegate(delegate: type[T]) -> Delegate[T]:
    """
    Creates a delegate of type T.

    Args:
        delegate (type[T]): The delegate protocol type

    Returns:
        Delegate[T]: Returns a Delegate[T] object.
    """
    ...
@overload
def delegate(delegate: type[T], type_out: type[Tout]) -> Tout:
    """
    Creates a passthrough delegate of type Tp with an out type of Tout. This implementation
    makes type checkers believe that a value of Tout is the actual returned object, which
    is the case when retrieved afterwards.

    Args:
        delegate (type[Tp]): The delegate protocol type

    Returns:
        Delegate[Tp]: Returns a Delegate[Tp] object.
    """
    ...
def delegate(delegate: type[T], type_out: type[Tout] | None = None) -> Delegate[T] | Tout:
    return Delegate[delegate](type_out is not None)

def check_slots(cls: type[Any]) -> None: # pragma: no cover
    if hasattr(cls, "__slots__"):
        slots = getattr(cls, "__slots__")
        if ATTR not in slots:
            raise DelegatorError(f"Delegator class {cls.__name__} uses slots, and attribute '{ATTR}' is not defined. Please make sure that attributes '__weakref__' and '{ATTR}' are both defined in class slots.")
        if "__weakref__" not in slots:
            raise DelegatorError(f"Delegator class {cls.__name__} uses slots, and attribute '__weakref__' is not defined. Please make sure that attributes '__weakref__' and '{ATTR}' are both defined in class slots.")

