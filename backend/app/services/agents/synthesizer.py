"""Synthesizer node — merges, deduplicates, detects conflicts, filters by role.

Story 7.4: Full synthesis with conflict detection, compound insights,
cascading support, role-aware confidence thresholds, and epistemic honesty.
"""

from itertools import combinations

import structlog

from app.config import settings
from app.schemas.agent import AgentInsight, PipelineState

logger = structlog.get_logger()

# Default confidence thresholds per role
ROLE_THRESHOLDS: dict[str, str] = {
    "tech_lead": "confidence_tech_lead",
    "developer": "confidence_developer",
    "pm": "confidence_pm",
    "commercial": "confidence_commercial",
    "admin": "confidence_admin",
}

# Insight types that may conflict between agents
CONFLICT_PAIRS = [
    ("effort_estimation", "budget_impact"),
    ("effort_estimation", "scope_classification"),
    ("alternative_suggestion", "pattern_suggestion"),
    ("dependency_alert", "scope_classification"),
]


def _get_threshold(role: str) -> float:
    """Get the confidence threshold for a role from settings."""
    attr = ROLE_THRESHOLDS.get(role, "confidence_admin")
    return getattr(settings, attr, 0.5)


def _is_duplicate(
    insight: AgentInsight,
    previous: list[str],
) -> bool:
    """Check if insight summary is too similar to a previous one."""
    summary_lower = insight.summary.lower().strip()
    return any(
        summary_lower and prev.lower().strip() == summary_lower
        for prev in previous
    )


def _detect_conflicts(
    insights: list[AgentInsight],
) -> list[tuple[AgentInsight, AgentInsight]]:
    """Detect contradictions between insights from different agents.

    A conflict occurs when two agents from different sources generate
    insights of types known to potentially contradict each other.
    """
    conflicts: list[tuple[AgentInsight, AgentInsight]] = []
    for a, b in combinations(insights, 2):
        if a.agent_source == b.agent_source:
            continue
        type_pair = (a.subtype or a.type, b.subtype or b.type)
        type_pair_rev = (type_pair[1], type_pair[0])
        if type_pair in CONFLICT_PAIRS or type_pair_rev in CONFLICT_PAIRS:
            conflicts.append((a, b))
    return conflicts


def _generate_compound_insight(
    a: AgentInsight,
    b: AgentInsight,
) -> AgentInsight:
    """Generate a compound synthesis insight from two conflicting insights."""
    return AgentInsight(
        agent_source="supervisor",
        type="alert",
        subtype="synthesis_conflict",
        summary=(
            f"{a.agent_source} vs {b.agent_source}: perspectivas distintas"
        ),
        content=(
            f"**{a.agent_source}**: {a.summary}. "
            f"**{b.agent_source}**: {b.summary}. "
            "Revisar ambas perspectivas antes de decidir."
        ),
        confidence=max(a.confidence, b.confidence),
        sources=list(set(a.sources + b.sources)),
        target_roles=list(set(a.target_roles + b.target_roles)),
        metadata={
            "conflict_agents": [a.agent_source, b.agent_source],
            "conflict_types": [a.type, b.type],
        },
    )


def _apply_confidence_filter(
    insights: list[AgentInsight],
) -> list[AgentInsight]:
    """Filter insights by confidence threshold per target role.

    An insight passes if it meets the threshold for ANY of its target roles.
    """
    filtered: list[AgentInsight] = []
    for insight in insights:
        for role in insight.target_roles:
            threshold = _get_threshold(role)
            if insight.confidence >= threshold:
                filtered.append(insight)
                break
    return filtered


async def synthesizer_node(state: PipelineState) -> dict:
    """Full synthesis: dedup → conflict detection → compound generation
    → confidence filter → epistemic honesty."""
    raw_insights = state.get("agent_insights", [])
    previous = state.get("previous_insights", [])

    if not raw_insights:
        if not state.get("context_chunks"):
            hint = AgentInsight(
                agent_source="supervisor",
                type="suggestion",
                subtype="insufficient_context",
                summary="Sin contexto del proyecto indexado",
                content=(
                    "No hay documentos de contexto. "
                    "Subir archivos del proyecto mejorará "
                    "las sugerencias."
                ),
                confidence=1.0,
                sources=[],
                target_roles=["admin", "tech_lead"],
            )
            logger.info("synthesizer_insufficient_context")
            return {"final_insights": [hint]}
        logger.info("synthesizer_no_insights")
        return {"final_insights": []}

    # Step 1: Deduplicate against previous insights
    deduped: list[AgentInsight] = [
        i for i in raw_insights if not _is_duplicate(i, previous)
    ]

    # Step 2: Detect conflicts between agents
    conflicts = _detect_conflicts(deduped)
    compound_insights: list[AgentInsight] = []
    for a, b in conflicts:
        compound = _generate_compound_insight(a, b)
        compound_insights.append(compound)
        logger.info(
            "conflict_detected",
            agent_a=a.agent_source,
            agent_b=b.agent_source,
            type_a=a.type,
            type_b=b.type,
        )

    # Step 3: Merge originals + compounds
    all_insights = deduped + compound_insights

    # Step 4: Apply confidence threshold per role
    filtered = _apply_confidence_filter(all_insights)

    # Step 5: Epistemic honesty — no context + no good insights
    if not state.get("context_chunks") and not filtered:
        filtered.append(AgentInsight(
            agent_source="supervisor",
            type="suggestion",
            subtype="insufficient_context",
            summary="Sin contexto del proyecto indexado",
            content=(
                "No hay documentos de contexto. "
                "Subir archivos del proyecto mejorará "
                "las sugerencias."
            ),
            confidence=1.0,
            sources=[],
            target_roles=["admin", "tech_lead"],
        ))

    logger.info(
        "synthesizer_done",
        raw=len(raw_insights),
        deduped=len(deduped),
        conflicts=len(conflicts),
        compounds=len(compound_insights),
        filtered=len(filtered),
    )

    return {"final_insights": filtered}
