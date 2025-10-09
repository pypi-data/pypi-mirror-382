
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from onescience.models.UMA.components.reducer import Reducer
    from onescience.models.UMA.components.runner import Runner


class ManagedAttribute:
    """A descriptor helper to manage setting/access to an attribute of a class"""

    def __init__(self, enforced_type: type | None = None):
        self._enforced_type = enforced_type

    def __set_name__(self, owner: Runner | Reducer, name: str):
        self.public_name: str = name
        self.private_name: str = "_" + name

    def __get__(
        self, obj: Runner | Reducer, objtype: type[Runner | Reducer] | None = None
    ):
        return getattr(obj, self.private_name)

    def __set__(self, obj: Runner | Reducer, value: Any):
        if self._enforced_type is not None and not isinstance(
            value, self._enforced_type
        ):
            raise ValueError(
                f"{self.public_name} can only be set to an instance of {self._enforced_type} type!"
            )
        setattr(obj, self.private_name, value)
