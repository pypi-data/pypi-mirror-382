"""
Model subpackage containing core data structures and types.

This subpackage contains the fundamental data structures that form the
dependency injection model, organized to avoid circular dependencies.
"""

from .bindings import Binding
from .graph import DependencyGraph
from .keys import DIKey, Id, InstanceKey, SetElementKey
from .operations import CreateFactory, CreateSet, ExecutableOp, Provide
from .plan import Plan

__all__ = [
    "DIKey",
    "Binding",
    "DependencyGraph",
    "InstanceKey",
    "SetElementKey",
    "Id",
    "Plan",
    "ExecutableOp",
    "Provide",
    "CreateSet",
    "CreateFactory",
]
