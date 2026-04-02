from __future__ import annotations

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from job_agent.discovery.engine import DiscoveryEngine
from job_agent.experience.loader import ExperienceLakeLoader
from job_agent.matching.agent import MatcherAgent
from job_agent.rag.index import ExperienceRAGIndex
from job_agent.schemas.jobs import ApplicationPackage, JobPosting, MatchAssessment
from job_agent.tailoring.agent import TailoringAgent


class JobAgentState(TypedDict, total=False):
    query: str
    discovered_jobs: list[JobPosting]
    shortlisted_jobs: list[JobPosting]
    assessments: list[MatchAssessment]
    tailored_packages: list[ApplicationPackage]


def build_job_agent_graph(
    discovery_engine: DiscoveryEngine,
    experience_lake_path: str,
    min_match_score: int = 3,
):
    lake = ExperienceLakeLoader(experience_lake_path).load()
    matcher = MatcherAgent(lake)
    rag_index = ExperienceRAGIndex(ExperienceLakeLoader(experience_lake_path).to_documents(lake))
    tailor = TailoringAgent(lake, rag_index)

    def discovery_node(state: JobAgentState) -> JobAgentState:
        query = state.get("query", "software engineer")
        discovered_jobs = discovery_engine.poll(query=query)
        return {**state, "discovered_jobs": discovered_jobs}

    def scoring_node(state: JobAgentState) -> JobAgentState:
        discovered = state.get("discovered_jobs", [])
        assessments: list[MatchAssessment] = []
        shortlisted: list[JobPosting] = []
        for job in discovered:
            result = matcher.score_job(job.description)
            assessment = MatchAssessment(
                job_id=job.id,
                score=result.score,
                strengths_alignment=result.strengths_alignment,
                critical_gaps=result.critical_gaps,
                rationale=result.rationale,
            )
            assessments.append(assessment)
            if result.score >= min_match_score:
                shortlisted.append(job)
        return {**state, "assessments": assessments, "shortlisted_jobs": shortlisted}

    def tailoring_node(state: JobAgentState) -> JobAgentState:
        shortlisted = state.get("shortlisted_jobs", [])
        assessments_by_job = {a.job_id: a for a in state.get("assessments", [])}

        packages: list[ApplicationPackage] = []
        for job in shortlisted:
            assessment = assessments_by_job[job.id]
            packages.append(tailor.build_application_package(job, assessment))
        return {**state, "tailored_packages": packages}

    def submission_node(state: JobAgentState) -> JobAgentState:
        return state

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
