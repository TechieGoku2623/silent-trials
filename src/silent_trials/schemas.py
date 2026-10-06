"""Data contracts for Phase 0 trials, publications, and matcher decisions."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

StudyType = Literal["interventional", "observational", "expanded_access"]
Phase = Literal["Phase 1", "Phase 2", "Phase 3", "Phase 4", "Not Applicable", "Early Phase 1"]
ProductType = Literal["drug", "biologic", "device", "behavioral", "other"]
CompletionDateType = Literal["primary", "study"]
MatchDecision = Literal["MATCH", "NO_MATCH", "AMBIGUOUS"]
FdaaaStatus = Literal[
    "NOT_APPLICABLE",
    "NOT_YET_DUE",
    "REPORTED_REGISTRY",
    "REPORTED_PUBLICATION",
    "REPORTED_BOTH",
    "SILENT",
]
AdjudicationLabel = Literal["genuinely_unreported", "reported_but_unmatched"]


class TrialRecord(BaseModel):
    """One registered trial, modeled on a ClinicalTrials.gov study record."""

    nct_id: str
    title: str
    official_title: str = ""
    condition: str
    sponsor: str
    pi_last: str
    pi_first: str = ""
    phase: Phase
    study_type: StudyType = "interventional"
    product_type: ProductType = "drug"
    us_site: bool = True
    fda_regulated: bool = True
    device_feasibility: bool = False
    applicable_clinical_trial: bool
    primary_completion_date: date
    study_completion_date: date | None = None
    completion_date_type: CompletionDateType = "primary"
    has_registry_results: bool = False
    registry_results_first_posted: date | None = None
    overall_status: str = "Completed"
    notes: str = ""


class PublicationRecord(BaseModel):
    """One candidate publication, modeled on a PubMed citation."""

    pub_id: str
    title: str
    abstract: str
    authors: list[str] = Field(default_factory=list)
    journal: str = ""
    published: date
    pmid: str = ""
    mesh_terms: list[str] = Field(default_factory=list)
    body: str = ""


class SampleCase(BaseModel):
    """One of the designed demo cases."""

    sample_id: str
    nct_id: str
    path_exercised: str
    why_present: str
    expected_behavior: str
    trial: TrialRecord
    publications: list[PublicationRecord] = Field(default_factory=list)


class CandidateScore(BaseModel):
    """Explainable score for one trial–publication pair."""

    pub_id: str
    score: float
    reasons: list[str]
    nct_in_text: bool
    title_similarity: float
    pi_match: bool
    condition_overlap: float
    date_in_window: bool


class MatchResult(BaseModel):
    """Matcher output for one trial against a publication list."""

    nct_id: str
    decision: MatchDecision
    chosen_pub_id: str | None = None
    candidates: list[CandidateScore] = Field(default_factory=list)
    rationale: str


class FdaaaClock(BaseModel):
    """Time-aware FDAAA 801 results-reporting clock for one trial."""

    nct_id: str
    reference_date: date
    completion_date: date
    completion_date_type: CompletionDateType
    applicable: bool
    due_date: date | None
    days_elapsed: int
    days_remaining: int | None
    has_registry_results: bool
    status: FdaaaStatus
    rationale: str


class ReportingOutcome(BaseModel):
    """Combined FDAAA clock + matcher view used for sponsor tallies."""

    nct_id: str
    sponsor: str
    clock: FdaaaClock
    match: MatchResult
    outcome: FdaaaStatus
