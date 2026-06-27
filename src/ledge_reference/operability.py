from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from textwrap import dedent
from typing import Any


LF = chr(10)
BLANK_LINE = LF + LF


@dataclass(frozen=True)
class DriftResult:
    claim_id: str
    drift: bool
    reason: str
    clerk_references: tuple[str, ...]


@dataclass(frozen=True)
class TransitionResult:
    transition_id: str
    status: str
    approval_id: str
    accepted_state_path: str
    authentication_migration_complete: bool


@dataclass(frozen=True)
class AgentContextResult:
    state_id: str
    authentication_migration_complete: bool
    evidence_paths: tuple[str, ...]
    corrected_assumptions: tuple[str, ...]
    markdown: str


@dataclass(frozen=True)
class AgentTask:
    path: str
    text: str
    summary: str


@dataclass(frozen=True)
class AgentDecisionResult:
    task: str
    context_path: str
    accepted_knowledge: str
    stale_assumptions_avoided: tuple[str, ...]
    evidence_paths: tuple[str, ...]
    reality_check: str
    decision: str
    markdown: str


def inspect_auth_migration(example_root: Path) -> DriftResult:
    """Inspect the auth migration example without defining a protocol format."""
    claim_path = example_root / ".ledge" / "claims" / "auth-uses-betterauth.json"
    source_paths = sorted((example_root / "src").rglob("*.ts"))

    claim = json.loads(claim_path.read_text(encoding="utf-8"))
    claimed_complete = claim["migration"]["claimedComplete"]
    clerk_references = tuple(
        str(path.relative_to(example_root))
        for path in source_paths
        if "clerk" in path.read_text(encoding="utf-8").lower()
    )

    drift = claimed_complete and bool(clerk_references)
    reason = (
        "Claim says the Clerk to BetterAuth migration is complete, "
        "but local source files still reference Clerk."
        if drift
        else "Claim and local source evidence do not show this drift."
    )

    return DriftResult(
        claim_id="claim.auth.uses-betterauth",
        drift=drift,
        reason=reason,
        clerk_references=clerk_references,
    )


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_latest_accepted_state(example_root: Path) -> dict[str, Any]:
    state_path = example_root / ".ledge" / "states" / "current.json"
    state = load_json(state_path)

    if state.get("status") != "accepted":
        raise ValueError("Latest state must be accepted.")

    if state.get("authenticationMigrationComplete") is not False:
        raise ValueError(
            "Latest accepted state must mark authentication migration complete as false."
        )

    return state


def load_relevant_intent(example_root: Path) -> str:
    intent_path = (
        example_root / ".ledge" / "intent" / "replace-clerk-with-betterauth.md"
    )
    intent_text = intent_path.read_text(encoding="utf-8")

    if "Replace Clerk with BetterAuth" not in intent_text:
        raise ValueError("Expected auth migration intent was not found.")

    return "Replace Clerk with BetterAuth."


def load_proposed_transition(example_root: Path, transition_name: str) -> dict[str, Any]:
    transition_path = example_root / ".ledge" / "transitions" / transition_name
    transition = load_json(transition_path)
    validate_proposed_transition(example_root, transition)
    return transition


def validate_proposed_transition(
    example_root: Path, transition: dict[str, Any]
) -> None:
    if transition.get("status") != "proposed":
        raise ValueError("Transition must have status proposed before approval.")

    patch_path = transition.get("patchPath")
    if not isinstance(patch_path, str):
        raise ValueError("Transition must reference a patch path.")

    if not (example_root / ".ledge" / patch_path).is_file():
        raise ValueError("Transition must reference an existing patch.")


def load_authority_approval(example_root: Path, approval_name: str) -> dict[str, Any]:
    approval_path = example_root / ".ledge" / "authority" / approval_name
    return load_json(approval_path)


def apply_authority_approval(
    example_root: Path, transition: dict[str, Any], approval: dict[str, Any]
) -> dict[str, Any]:
    validate_proposed_transition(example_root, transition)

    if approval.get("decision") != "approved":
        raise ValueError("Authority approval must explicitly approve the transition.")

    if approval.get("transition") != transition.get("id"):
        raise ValueError("Authority approval must reference the transition.")

    accepted_transition = dict(transition)
    accepted_transition["status"] = "accepted"
    accepted_transition["approval"] = approval["id"]
    return accepted_transition


def validate_accepted_transition(transition: dict[str, Any]) -> None:
    if transition.get("status") != "accepted":
        raise ValueError("Transition is not accepted.")

    if not transition.get("approval"):
        raise ValueError("Accepted transition must record approval.")


def validate_new_accepted_state(
    example_root: Path, accepted_transition: dict[str, Any]
) -> TransitionResult:
    validate_accepted_transition(accepted_transition)

    state_path = accepted_transition.get("acceptedStatePath")
    if not isinstance(state_path, str):
        raise ValueError("Accepted transition must reference a new accepted state.")

    state = load_json(example_root / ".ledge" / state_path)

    if state.get("acceptedTransition") != accepted_transition.get("id"):
        raise ValueError("New accepted state must reference the accepted transition.")

    complete = state.get("authenticationMigrationComplete")
    if complete is not False:
        raise ValueError(
            "New accepted state must mark authentication migration complete as false."
        )

    return TransitionResult(
        transition_id=accepted_transition["id"],
        status=accepted_transition["status"],
        approval_id=accepted_transition["approval"],
        accepted_state_path=state_path,
        authentication_migration_complete=complete,
    )


def load_auth_migration_evidence(example_root: Path) -> dict[str, Any]:
    evidence_path = example_root / ".ledge" / "evidence" / "source-scan.json"
    evidence = load_json(evidence_path)

    observations = evidence.get("observations")
    if not isinstance(observations, list) or not observations:
        raise ValueError("Evidence must include source observations.")

    return evidence


def generate_agent_context(example_root: Path) -> AgentContextResult:
    state = load_latest_accepted_state(example_root)
    human_intent = load_relevant_intent(example_root)
    evidence = load_auth_migration_evidence(example_root)

    transition = load_proposed_transition(
        example_root, "mark-auth-migration-incomplete.proposed.json"
    )
    approval = load_authority_approval(example_root, "founder-approval.json")
    accepted_transition = apply_authority_approval(example_root, transition, approval)
    validate_accepted_transition(accepted_transition)

    if state.get("acceptedTransition") != accepted_transition.get("id"):
        raise ValueError("Latest accepted state must reference the accepted transition.")

    evidence_paths = tuple(
        observation["path"]
        for observation in evidence["observations"]
        if isinstance(observation, dict) and isinstance(observation.get("path"), str)
    )
    if not evidence_paths:
        raise ValueError("Evidence must include source paths.")

    corrected_assumptions = (
        "Do not assume authentication migration is complete.",
        "Do not assume all Clerk references have been removed.",
    )

    markdown = render_agent_context_markdown(
        human_intent=human_intent,
        evidence_paths=evidence_paths,
        corrected_assumptions=corrected_assumptions,
    )

    return AgentContextResult(
        state_id=state["id"],
        authentication_migration_complete=state["authenticationMigrationComplete"],
        evidence_paths=evidence_paths,
        corrected_assumptions=corrected_assumptions,
        markdown=markdown,
    )


def render_agent_context_markdown(
    human_intent: str,
    evidence_paths: tuple[str, ...],
    corrected_assumptions: tuple[str, ...],
) -> str:
    evidence_lines = LF.join(f"- {path}" for path in evidence_paths)
    assumption_lines = LF.join(corrected_assumptions)
    guidance_lines = LF.join(
        (
            "1. Search for remaining Clerk references.",
            "2. Prefer BetterAuth-compatible changes.",
            "3. Do not mark the migration complete without evidence.",
            "4. Produce evidence for any claim about migration completion.",
        )
    )

    sections = (
        "# Agent Context",
        dedent(
            """
            ## Human Intent
            {human_intent}
            """
        ).strip().format(human_intent=human_intent),
        dedent(
            """
            ## Accepted Knowledge
            Authentication migration is not complete.
            """
        ).strip(),
        dedent(
            """
            ## Evidence
            Remaining Clerk references were found in:

            {evidence_lines}
            """
        ).strip().format(evidence_lines=evidence_lines),
        dedent(
            """
            ## Corrected Assumptions
            {assumption_lines}
            """
        ).strip().format(assumption_lines=assumption_lines),
        dedent(
            """
            ## Current Drift Risk
            The codebase may still contain Clerk-specific imports, middleware, or auth provider usage.
            """
        ).strip(),
        dedent(
            """
            ## Agent Guidance
            Before implementing new authentication changes:

            {guidance_lines}
            """
        ).strip().format(guidance_lines=guidance_lines),
    )
    return BLANK_LINE.join(sections) + LF


def write_agent_context(example_root: Path) -> AgentContextResult:
    result = generate_agent_context(example_root)
    context_path = example_root / ".ledge" / "context" / "agent-context.md"
    context_path.parent.mkdir(parents=True, exist_ok=True)
    context_path.write_text(result.markdown, encoding="utf-8")
    return result


def validate_agent_context(example_root: Path) -> AgentContextResult:
    result = generate_agent_context(example_root)
    context_path = example_root / ".ledge" / "context" / "agent-context.md"

    if context_path.read_text(encoding="utf-8") != result.markdown:
        raise ValueError("Generated agent context does not match the context artifact.")

    return result


def load_agent_context_artifact(example_root: Path) -> str:
    context_path = example_root / ".ledge" / "context" / "agent-context.md"
    if not context_path.is_file():
        raise ValueError("Generated agent context artifact is missing.")

    context = context_path.read_text(encoding="utf-8")
    if "Authentication migration is not complete." not in context:
        raise ValueError("Agent context must state accepted incomplete migration knowledge.")

    return context


def load_agent_task(example_root: Path, task_name: str) -> AgentTask:
    task_path = example_root / ".ledge" / "tasks" / task_name
    if not task_path.is_file():
        raise ValueError("Agent task is missing.")

    task_text = task_path.read_text(encoding="utf-8")
    summary = "Continue the authentication migration."
    if summary not in task_text:
        raise ValueError("Agent task must ask to continue the authentication migration.")

    return AgentTask(
        path=str(task_path.relative_to(example_root)),
        text=task_text,
        summary=summary,
    )


def generate_agent_decision_from_context(example_root: Path) -> AgentDecisionResult:
    load_agent_context_artifact(example_root)
    task = load_agent_task(example_root, "continue-auth-migration.md")
    evidence = load_auth_migration_evidence(example_root)

    evidence_paths = tuple(
        observation["path"]
        for observation in evidence["observations"]
        if isinstance(observation, dict) and isinstance(observation.get("path"), str)
    )
    if not evidence_paths:
        raise ValueError("Agent decision requires source evidence paths.")

    source_paths = tuple(
        str((example_root / path).relative_to(example_root))
        for path in evidence_paths
        if (example_root / path).is_file()
    )
    if source_paths != evidence_paths:
        raise ValueError("Agent decision evidence must reference existing source files.")

    stale_assumptions = (
        "Did not assume migration was complete.",
        "Did not assume all Clerk references were removed.",
    )
    evidence_consulted = (
        "examples/auth-migration/.ledge/evidence/source-scan.json",
        *evidence_paths,
    )
    accepted_knowledge = "Authentication migration is not complete."
    reality_check = "Remaining Clerk references are present."
    decision = LF.join(
        (
            "Do not mark migration complete.",
            "Continue migration by removing or replacing remaining Clerk-specific code.",
        )
    )

    markdown = render_agent_decision_markdown(
        task=task.summary,
        context_path="examples/auth-migration/.ledge/context/agent-context.md",
        accepted_knowledge=accepted_knowledge,
        stale_assumptions=stale_assumptions,
        evidence_consulted=evidence_consulted,
        reality_check=reality_check,
        decision=decision,
    )

    return AgentDecisionResult(
        task=task.summary,
        context_path="examples/auth-migration/.ledge/context/agent-context.md",
        accepted_knowledge=accepted_knowledge,
        stale_assumptions_avoided=stale_assumptions,
        evidence_paths=evidence_consulted,
        reality_check=reality_check,
        decision=decision,
        markdown=markdown,
    )


def render_agent_decision_markdown(
    task: str,
    context_path: str,
    accepted_knowledge: str,
    stale_assumptions: tuple[str, ...],
    evidence_consulted: tuple[str, ...],
    reality_check: str,
    decision: str,
) -> str:
    stale_assumption_lines = LF.join(
        f"- {assumption}" for assumption in stale_assumptions
    )
    evidence_lines = LF.join(f"- {path}" for path in evidence_consulted)

    sections = (
        "# Agent Decision",
        dedent(
            """
            ## Task
            {task}
            """
        ).strip().format(task=task),
        dedent(
            """
            ## Context Consumed
            {context_path}
            """
        ).strip().format(context_path=context_path),
        dedent(
            """
            ## Accepted Knowledge Used
            {accepted_knowledge}
            """
        ).strip().format(accepted_knowledge=accepted_knowledge),
        dedent(
            """
            ## Stale Assumptions Avoided
            {stale_assumption_lines}
            """
        ).strip().format(stale_assumption_lines=stale_assumption_lines),
        dedent(
            """
            ## Evidence Consulted
            {evidence_lines}
            """
        ).strip().format(evidence_lines=evidence_lines),
        dedent(
            """
            ## Reality Check
            {reality_check}
            """
        ).strip().format(reality_check=reality_check),
        dedent(
            """
            ## Decision
            {decision}
            """
        ).strip().format(decision=decision),
        dedent(
            """
            ## Proposed Next Actions
            1. Replace remaining Clerk middleware usage.
            2. Replace remaining Clerk provider usage.
            3. Re-run source scan.
            4. Only propose completion after evidence shows no remaining Clerk references.
            """
        ).strip(),
        dedent(
            """
            ## Artifact Boundary
            This is a local non-normative decision fixture.
            """
        ).strip(),
    )
    return BLANK_LINE.join(sections) + LF


def write_agent_decision(example_root: Path) -> AgentDecisionResult:
    result = generate_agent_decision_from_context(example_root)
    decision_path = (
        example_root
        / ".ledge"
        / "agent-decisions"
        / "continue-auth-migration.decision.md"
    )
    decision_path.parent.mkdir(parents=True, exist_ok=True)
    decision_path.write_text(result.markdown, encoding="utf-8")
    return result


def validate_agent_decision(example_root: Path) -> AgentDecisionResult:
    result = generate_agent_decision_from_context(example_root)
    decision_path = (
        example_root
        / ".ledge"
        / "agent-decisions"
        / "continue-auth-migration.decision.md"
    )

    if decision_path.read_text(encoding="utf-8") != result.markdown:
        raise ValueError("Generated agent decision does not match the decision artifact.")

    return result
