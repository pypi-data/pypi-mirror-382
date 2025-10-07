from typing import Protocol
from typingutils.internal import get_generic_origin
from inspect import Signature, Parameter, signature

from delegate.pattern.core.protocols.stateful_delegate_protocol import StatefulDelegateProtocol
from delegate.pattern.core.protocols.stateless_delegate_protocol import StatelessDelegateProtocol

class DummyProtocol(Protocol):
    pass

def is_stateful_delegate(delegate: type[StatelessDelegateProtocol | StatefulDelegateProtocol]):
    def is_stateful_ctor(sig: Signature) -> bool:
        parameters = list(sig.parameters.values())
        return (
            len(parameters) == 2

            and parameters[0].name.lower() in ("self", "cls")
            and parameters[0].kind in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD)

            and parameters[1].name.lower() == "delegator"
            and parameters[1].kind in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD)
        )

    delegate = get_generic_origin(delegate)

    if delegate.__new__ is not object.__new__:
        sig = signature(delegate.__new__)
        return is_stateful_ctor(sig)
    elif delegate.__init__ not in (object.__init__, DummyProtocol.__init__):
        sig = signature(delegate.__init__)
        return is_stateful_ctor(sig)

    return False