"""Base utilities for IR models.

Defines a shared immutable base model with consistent behavior.
"""

from typing import Any

from pydantic import BaseModel
from typing_extensions import Self


class FrozenModel(BaseModel, frozen=True):
    """Immutable Pydantic model raising AttributeError on mutation.

    Provides a clear and predictable immutability contract while retaining
    Pydantic's validation and schema generation. For updates, use ``replace``.
    """

    def __setattr__(self, name: str, value: Any) -> None:  # type: ignore[override]
        if not getattr(self, "_init_complete", False) or name.startswith("_"):
            return super().__setattr__(name, value)
        raise AttributeError("Instances are immutable; cannot assign to fields")

    def model_post_init(self, __context: Any) -> None:
        """Pydantic hook after initialization completes."""
        object.__setattr__(self, "_init_complete", True)

    def replace(self, **updates: Any) -> Self:
        """Return a copy with provided fields updated.

        Args:
            **updates: Field values to update in the new instance.

        Returns:
            A new instance with the given updates applied.
        """
        return self.model_copy(update=updates, deep=True)
