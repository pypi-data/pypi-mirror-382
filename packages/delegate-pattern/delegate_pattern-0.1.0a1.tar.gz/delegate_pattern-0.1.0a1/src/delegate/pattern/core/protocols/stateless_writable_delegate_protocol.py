from typing import Protocol, Any, runtime_checkable

@runtime_checkable
class StatelessWritableDelegateProtocol(Protocol):
    """
    A basic delegate protocol. Since the delegator argument type is Any,
    there's no restriction when implementing, as long as it's the only argument.
    """
    def __init__(self):
        ... # pragma: no cover

    def __set__(self, delegator: Any, value: Any) -> None:
        ... # pragma: no cover