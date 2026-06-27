"""Minimal local reference implementation for Ledge operability."""

from .operability import (
    AgentContextResult,
    DriftResult,
    TransitionResult,
    apply_authority_approval,
    generate_agent_context,
    inspect_auth_migration,
    load_auth_migration_evidence,
    load_authority_approval,
    load_latest_accepted_state,
    load_proposed_transition,
    load_relevant_intent,
    validate_agent_context,
    validate_accepted_transition,
    validate_new_accepted_state,
    validate_proposed_transition,
    write_agent_context,
)

__all__ = [
    "AgentContextResult",
    "DriftResult",
    "TransitionResult",
    "apply_authority_approval",
    "generate_agent_context",
    "inspect_auth_migration",
    "load_auth_migration_evidence",
    "load_authority_approval",
    "load_latest_accepted_state",
    "load_proposed_transition",
    "load_relevant_intent",
    "validate_agent_context",
    "validate_accepted_transition",
    "validate_new_accepted_state",
    "validate_proposed_transition",
    "write_agent_context",
]
