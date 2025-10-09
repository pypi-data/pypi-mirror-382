from .descriptors import RelationshipDescriptor, RelationshipProperty, RelationshipType
from .prefetch import PrefetchHandler
from .proxies import (
    BaseRelatedCollection,
    M2MRelatedCollection,
    NoLoadProxy,
    OneToManyCollection,
    RaiseProxy,
    RelatedObjectProxy,
    RelatedQuerySet,
)
from .utils import M2MTable, RelationshipAnalyzer, RelationshipResolver, relationship


__all__ = [
    # Core relationship types
    "RelationshipType",
    "RelationshipProperty",
    "RelationshipDescriptor",
    "RelationshipResolver",
    # Relationship managers
    "RelatedObjectProxy",
    "BaseRelatedCollection",
    "OneToManyCollection",
    "M2MRelatedCollection",
    "RelatedQuerySet",
    "NoLoadProxy",
    "RaiseProxy",
    # Utilities
    "M2MTable",
    "relationship",
    # New components
    "RelationshipAnalyzer",
    "PrefetchHandler",
]
