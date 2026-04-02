from __future__ import annotations

import logging
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from job_agent.core.config import AgentConfig
from job_agent.discovery.engine import DiscoveryEngine
from job_agent.experience.loader import ExperienceLakeLoader
from job_agent.llm.client import LLMClient
from job_agent.matching.agent import MatcherAgent
from job_agent.persistence.store import SQLiteStore
from job_agent.rag.index import ExperienceRAGIndex
from job_agent.schemas.fill_plan import FillPlan
from job_agent.schemas.jobs import ApplicationPackage, JobPosting, MatchAssessment
from job_agent.submission.stealth import StealthExecutor
from job_agent.tailoring.agent import TailoringAgent

logger = logging.getLogger(__name__)


class JobAgentState(TypedDict, total=False):
    query: str
    discovered_jobs: list[JobPosting]
    shortlisted_jobs: list[JobPosting]
    assessments: list[MatchAssessment]
    tailored_packages: list[ApplicationPackage]
    submitted_job_ids: list[str]


def build_job_agent_graph(
    discovery_engine: DiscoveryEngine,
    config: AgentConfig,
):
    loader = ExperienceLakeLoader(config.experience_lake_path)
    lake = loader.load()
    rag_index = ExperienceRAGIndex(loader.to_documents(lake))
    llm_client = LLMClient(model=config.openai_model, api_key=config.openai_api_key) if config.openai_api_key else None
    matcher = MatcherAgent(lake=lake, llm_client=llm_client)
    tailor = TailoringAgent(lake=lake, rag_index=rag_index, llm_client=llm_client, output_dir=config.output_dir)
    store = SQLiteStore(path=config.sqlite_path)
    executor = StealthExecutor(cdp_url=config.cdp_url, headless=config.headless)

    def discovery_node(state: JobAgentState) -> JobAgentState:
        query = state.get("query", "software engineer")
        discovered_jobs = discovery_engine.poll(query=query)
        for job in discovered_jobs:
            store.save_job(job)
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
            store.save_assessment(assessment)
            assessments.append(assessment)
            if result.score >= config.min_match_score:
                shortlisted.append(job)
        return {**state, "assessments": assessments, "shortlisted_jobs": shortlisted}

    def tailoring_node(state: JobAgentState) -> JobAgentState:
        shortlisted = state.get("shortlisted_jobs", [])
        assessments_by_job = {a.job_id: a for a in state.get("assessments", [])}

        packages: list[ApplicationPackage] = []
        for job in shortlisted:
            assessment = assessments_by_job[job.id]
            package = tailor.build_application_package(job, assessment)
            store.save_package(package)
            packages.append(package)
        return {**state, "tailored_packages": packages}

    def submission_node(state: JobAgentState) -> JobAgentState:
        submitted_job_ids: list[str] = []
        for package in state.get("tailored_packages", []):
            fill_plan = FillPlan.model_validate(package.fill_plan)
            if not config.dry_run_submission:
                executor.submit(fill_plan)
            store.mark_submitted(package.job_id)
            submitted_job_ids.append(package.job_id)
            logger.info("Submitted (or marked dry-run) job_id=%s", package.job_id)
        return {**state, "submitted_job_ids": submitted_job_ids}

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
