from typing import Protocol, runtime_checkable

@runtime_checkable
class StatelessDelegateProtocol(Protocol):
    """
    A basic delegate protocol. Since the delegator argument type is Any,
    there's no restriction when implementing, as long as it's the only argument.
    """
    def __init__(self):
        ... # pragma: no cover
