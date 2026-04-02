from __future__ import annotations

from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class JobAgentState(TypedDict, total=False):
    query: str
    discovered_jobs: list[dict]
    shortlisted_jobs: list[dict]
    tailored_documents: list[dict]
    submitted: list[dict]


def discovery_node(state: JobAgentState) -> JobAgentState:
    return {**state, "discovered_jobs": state.get("discovered_jobs", [])}


def scoring_node(state: JobAgentState) -> JobAgentState:
    return {**state, "shortlisted_jobs": state.get("shortlisted_jobs", [])}


def tailoring_node(state: JobAgentState) -> JobAgentState:
    return {**state, "tailored_documents": state.get("tailored_documents", [])}


def submission_node(state: JobAgentState) -> JobAgentState:
    return {**state, "submitted": state.get("submitted", [])}


def build_job_agent_graph():
    graph = StateGraph(JobAgentState)
    graph.add_node("discovery", discovery_node)
    graph.add_node("scoring", scoring_node)
    graph.add_node("tailoring", tailoring_node)
    graph.add_node("submission", submission_node)

    graph.add_edge(START, "discovery")
    graph.add_edge("discovery", "scoring")
    graph.add_edge("scoring", "tailoring")
    graph.add_edge("tailoring", "submission")
    graph.add_edge("submission", END)

    return graph.compile()
