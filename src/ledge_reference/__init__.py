"""Minimal local reference implementation for Ledge operability."""

from .operability import (
    DriftResult,
    TransitionResult,
    apply_authority_approval,
    inspect_auth_migration,
    load_authority_approval,
    load_proposed_transition,
    validate_accepted_transition,
    validate_new_accepted_state,
    validate_proposed_transition,
)

__all__ = [
    "DriftResult",
    "TransitionResult",
    "apply_authority_approval",
    "inspect_auth_migration",
    "load_authority_approval",
    "load_proposed_transition",
    "validate_accepted_transition",
    "validate_new_accepted_state",
    "validate_proposed_transition",
]
