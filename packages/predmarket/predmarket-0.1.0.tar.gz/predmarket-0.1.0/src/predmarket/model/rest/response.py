from pydantic import BaseModel
from typing import TypeVar, Generic, Any

T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    """Generic API response wrapper."""

    data: T
    metadata: dict[str, Any] = {}

    def merge(self, other: "Response[list[Any]]") -> "Response[list[Any]]":
        """Merge two list-based responses."""
        if not isinstance(self.data, list) or not isinstance(other.data, list):
            raise TypeError("Both responses must have list data to merge.")
        return Response(
            data=self.data + other.data,
            metadata={**self.metadata, **other.metadata},
        )
