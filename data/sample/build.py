"""Build the 20 designed sample cases. Not a ClinicalTrials.gov dump."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
REF = date(2026, 10, 6)


def _trial(
    nct: str,
    title: str,
    condition: str,
    sponsor: str,
    pi: str,
    phase: str,
    completion: date,
    *,
    applicable: bool = True,
    results: bool = False,
    results_posted: date | None = None,
    study_type: str = "interventional",
    product: str = "drug",
    us_site: bool = True,
    fda: bool = True,
    device_feasibility: bool = False,
    completion_date_type: str = "primary",
    study_completion: date | None = None,
    notes: str = "",
) -> dict[str, object]:
    return {
        "nct_id": nct,
        "title": title,
        "official_title": title,
        "condition": condition,
        "sponsor": sponsor,
        "pi_last": pi,
        "pi_first": "Alex",
        "phase": phase,
        "study_type": study_type,
        "product_type": product,
        "us_site": us_site,
        "fda_regulated": fda,
        "device_feasibility": device_feasibility,
        "applicable_clinical_trial": applicable,
        "primary_completion_date": completion.isoformat(),
        "study_completion_date": study_completion.isoformat() if study_completion else None,
        "completion_date_type": completion_date_type,
        "has_registry_results": results,
        "registry_results_first_posted": results_posted.isoformat() if results_posted else None,
        "overall_status": "Completed",
        "notes": notes,
    }


def _pub(
    pub_id: str,
    title: str,
    abstract: str,
    authors: list[str],
    published: date,
    mesh: list[str],
    body: str = "",
) -> dict[str, object]:
    return {
        "pub_id": pub_id,
        "title": title,
        "abstract": abstract,
        "authors": authors,
        "journal": "Designed Neuropsychiatric Journal",
        "published": published.isoformat(),
        "pmid": pub_id.replace("pub-", "9"),
        "mesh_terms": mesh,
        "body": body,
    }


def samples() -> list[dict[str, object]]:
    return [
        {
            "sample_id": "S1-nct-in-abstract",
            "nct_id": "NCT00000001",
            "path_exercised": "easy match: publication cites NCT00000001 in the abstract",
            "why_present": "The matcher must fire on an explicit NCT and not require title overlap.",
            "expected_behavior": (
                "MATCH on pub-s1. Decision is nct_in_text. Headline linkage is defensible "
                "for this path."
            ),
            "trial": _trial(
                "NCT00000001",
                "Adjunctive ketamine infusion for treatment-resistant major depression",
                "major depressive disorder",
                "Northlake Neurosciences",
                "Moreau",
                "Phase 2",
                date(2023, 3, 15),
            ),
            "publications": [
                _pub(
                    "pub-s1",
                    "Ketamine as adjunctive therapy in resistant depression: a randomized study",
                    "We enrolled adults with treatment-resistant depression (NCT00000001). "
                    "Ketamine infusion was compared with midazolam.",
                    ["Moreau A", "Chen L"],
                    date(2024, 1, 10),
                    ["Depressive Disorder, Major"],
                )
            ],
        },
        {
            "sample_id": "S2-title-pi-condition-date",
            "nct_id": "NCT00000002",
            "path_exercised": "no NCT in the publication; match on title, PI, condition, date window",
            "why_present": "Most psychiatry papers still omit the NCT. This is the hard typical path.",
            "expected_behavior": (
                "MATCH on pub-s2 via title similarity + PI Moreau + major depression + "
                "date window. No NCT signal."
            ),
            "trial": _trial(
                "NCT00000002",
                "Vortioxetine versus escitalopram for major depressive disorder",
                "major depressive disorder",
                "Harbor Psychiatric Consortium",
                "Moreau",
                "Phase 3",
                date(2022, 8, 1),
            ),
            "publications": [
                _pub(
                    "pub-s2",
                    "Vortioxetine versus escitalopram in major depressive disorder",
                    "Adults with major depressive disorder were randomized to vortioxetine "
                    "or escitalopram at Harbor sites.",
                    ["Moreau A", "Singh R"],
                    date(2023, 6, 20),
                    ["Depressive Disorder, Major"],
                )
            ],
        },
        {
            "sample_id": "S3-not-yet-due",
            "nct_id": "NCT00000003",
            "path_exercised": "completed 4 months ago — within the FDAAA 12-month window, not delinquent",
            "why_present": "A 4-month-old completion is not late. Time-unaware clocks invent silence.",
            "expected_behavior": (
                f"status = NOT_YET_DUE as of {REF.isoformat()} with days remaining until "
                "2027-06-06. Do not count as silent."
            ),
            "trial": _trial(
                "NCT00000003",
                "Lamotrigine adjunct for focal epilepsy in adults",
                "focal epilepsy",
                "Aether BioPharma",
                "Okada",
                "Phase 3",
                date(2026, 6, 6),
            ),
            "publications": [],
        },
        {
            "sample_id": "S4-registry-only",
            "nct_id": "NCT00000004",
            "path_exercised": "completed 3 years ago, results posted to the registry, never journal-published",
            "why_present": "Registry results satisfy FDAAA. No journal article is not silence.",
            "expected_behavior": (
                "REPORTED via registry (REPORTED_REGISTRY). Not silent. Journal absence "
                "is recorded, not scored as non-reporting."
            ),
            "trial": _trial(
                "NCT00000004",
                "Donepezil dose-ranging study in mild Alzheimer disease",
                "Alzheimer disease",
                "Aether BioPharma",
                "Okada",
                "Phase 2",
                date(2023, 10, 6),
                results=True,
                results_posted=date(2024, 9, 1),
            ),
            "publications": [],
        },
        {
            "sample_id": "S5-ambiguous",
            "nct_id": "NCT00000005",
            "path_exercised": "two plausible candidate publications — matcher returns AMBIGUOUS",
            "why_present": "Force-picking a paper among near-ties inflates the reported rate.",
            "expected_behavior": (
                "AMBIGUOUS. Matcher does not pick pub-s5a or pub-s5b. Both share PI, "
                "condition, and a date window."
            ),
            "trial": _trial(
                "NCT00000005",
                "Pramipexole versus ropinirole for early Parkinson disease",
                "Parkinson disease",
                "Northlake Neurosciences",
                "Varga",
                "Phase 3",
                date(2022, 4, 1),
            ),
            "publications": [
                _pub(
                    "pub-s5a",
                    "Pramipexole versus ropinirole for early Parkinson disease",
                    "A randomized comparison in Parkinson disease at Northlake.",
                    ["Varga K", "Holt J"],
                    date(2023, 2, 1),
                    ["Parkinson Disease"],
                ),
                _pub(
                    "pub-s5b",
                    "Pramipexole versus ropinirole for early Parkinson disease motor scores",
                    "Motor outcomes of pramipexole versus ropinirole in Parkinson disease.",
                    ["Varga K", "Ibrahim S"],
                    date(2023, 3, 15),
                    ["Parkinson Disease"],
                ),
            ],
        },
        {
            "sample_id": "S6-silent-due",
            "nct_id": "NCT00000006",
            "path_exercised": "applicable, past due, no registry results, no publication",
            "why_present": "The true-positive silent case the walkthrough needs.",
            "expected_behavior": "SILENT. Applicable Phase 3, primary completion 2023-01-15, nothing posted.",
            "trial": _trial(
                "NCT00000006",
                "Olanzapine long-acting injection for schizophrenia relapse prevention",
                "schizophrenia",
                "Harbor Psychiatric Consortium",
                "Singh",
                "Phase 3",
                date(2023, 1, 15),
            ),
            "publications": [],
        },
        {
            "sample_id": "S7-phase1-not-applicable",
            "nct_id": "NCT00000007",
            "path_exercised": "Phase 1 drug trial — not an applicable clinical trial",
            "why_present": "Phase 1 (drug/biologic) is outside the FDAAA ACT definition used here.",
            "expected_behavior": "NOT_APPLICABLE. Do not tally as silent or reported.",
            "trial": _trial(
                "NCT00000007",
                "First-in-human dose escalation of NX-19 in healthy adults",
                "healthy volunteers",
                "Aether BioPharma",
                "Chen",
                "Phase 1",
                date(2022, 2, 1),
                applicable=False,
            ),
            "publications": [],
        },
        {
            "sample_id": "S8-reported-publication-only",
            "nct_id": "NCT00000008",
            "path_exercised": "past due, no registry results, journal article with NCT",
            "why_present": "A journal article is reporting even when the results module is empty.",
            "expected_behavior": "REPORTED_PUBLICATION after MATCH on NCT in the abstract.",
            "trial": _trial(
                "NCT00000008",
                "Methylphenidate extended-release for adult ADHD",
                "attention deficit hyperactivity disorder",
                "Harbor Psychiatric Consortium",
                "Singh",
                "Phase 3",
                date(2022, 5, 1),
            ),
            "publications": [
                _pub(
                    "pub-s8",
                    "Extended-release methylphenidate in adult ADHD",
                    "Randomized trial (NCT00000008) of methylphenidate in adult ADHD.",
                    ["Singh R"],
                    date(2023, 4, 1),
                    ["Attention Deficit Disorder with Hyperactivity"],
                )
            ],
        },
        {
            "sample_id": "S9-primary-vs-study-date",
            "nct_id": "NCT00000009",
            "path_exercised": "completion date type is primary; study completion is later",
            "why_present": "Using study completion instead of primary invents extra grace time.",
            "expected_behavior": (
                "Clock uses primary_completion_date 2024-09-01 (due 2025-09-01). "
                "As of 2026-10-06 the trial is past due. No results → SILENT."
            ),
            "trial": _trial(
                "NCT00000009",
                "Lithium versus quetiapine for bipolar maintenance",
                "bipolar disorder",
                "Northlake Neurosciences",
                "Moreau",
                "Phase 3",
                date(2024, 9, 1),
                study_completion=date(2026, 8, 1),
                completion_date_type="primary",
            ),
            "publications": [],
        },
        {
            "sample_id": "S10-three-months-not-late",
            "nct_id": "NCT00000010",
            "path_exercised": "completed 3 months ago — still inside the 12-month window",
            "why_present": "Guards the time-aware clock: 3 months ago is not late.",
            "expected_behavior": "NOT_YET_DUE. days_remaining until 2027-07-06.",
            "trial": _trial(
                "NCT00000010",
                "Erenumab for chronic migraine prevention",
                "chronic migraine",
                "Aether BioPharma",
                "Okada",
                "Phase 3",
                date(2026, 7, 6),
            ),
            "publications": [],
        },
        {
            "sample_id": "S11-observational-not-act",
            "nct_id": "NCT00000011",
            "path_exercised": "observational registry — not interventional, not an ACT",
            "why_present": "Observational neuro cohorts are often miscounted as overdue trials.",
            "expected_behavior": "NOT_APPLICABLE.",
            "trial": _trial(
                "NCT00000011",
                "Natural history of early ALS at two academic centers",
                "amyotrophic lateral sclerosis",
                "Northlake Neurosciences",
                "Varga",
                "Not Applicable",
                date(2022, 1, 1),
                applicable=False,
                study_type="observational",
                product="other",
            ),
            "publications": [],
        },
        {
            "sample_id": "S12-device-feasibility",
            "nct_id": "NCT00000012",
            "path_exercised": "device feasibility study — excluded from the ACT flag",
            "why_present": "Feasibility device studies are not ACTs under the simplified flag.",
            "expected_behavior": "NOT_APPLICABLE.",
            "trial": _trial(
                "NCT00000012",
                "Feasibility of a closed-loop DBS lead in essential tremor",
                "essential tremor",
                "Aether BioPharma",
                "Chen",
                "Not Applicable",
                date(2021, 6, 1),
                applicable=False,
                product="device",
                device_feasibility=True,
            ),
            "publications": [],
        },
        {
            "sample_id": "S13-hard-negative-title",
            "nct_id": "NCT00000013",
            "path_exercised": "similar title, different PI and condition — must not match",
            "why_present": "Boilerplate psychiatry titles collide. Title-only matching is unsafe.",
            "expected_behavior": "NO_MATCH. Title overlap is weak-to-moderate; PI and condition fail.",
            "trial": _trial(
                "NCT00000013",
                "Sertraline for social anxiety disorder in adults",
                "social anxiety disorder",
                "Harbor Psychiatric Consortium",
                "Singh",
                "Phase 3",
                date(2022, 3, 1),
            ),
            "publications": [
                _pub(
                    "pub-s13",
                    "Sertraline for premature ejaculation in adults",
                    "A urology randomized study of sertraline. No psychiatric indication.",
                    ["Alvarez P"],
                    date(2023, 1, 1),
                    ["Premature Ejaculation"],
                )
            ],
        },
        {
            "sample_id": "S14-outside-date-window",
            "nct_id": "NCT00000014",
            "path_exercised": "same PI and condition, publication eight years later",
            "why_present": "A review article by the same PI is not the trial report.",
            "expected_behavior": "NO_MATCH. Date window fails; no NCT.",
            "trial": _trial(
                "NCT00000014",
                "Riluzole in amyotrophic lateral sclerosis — a multicenter trial",
                "amyotrophic lateral sclerosis",
                "Northlake Neurosciences",
                "Varga",
                "Phase 3",
                date(2014, 5, 1),
            ),
            "publications": [
                _pub(
                    "pub-s14",
                    "Twenty-year perspective on riluzole in ALS",
                    "A narrative review of amyotrophic lateral sclerosis therapeutics.",
                    ["Varga K"],
                    date(2024, 5, 1),
                    ["Amyotrophic Lateral Sclerosis"],
                )
            ],
        },
        {
            "sample_id": "S15-reported-both",
            "nct_id": "NCT00000015",
            "path_exercised": "registry results and a journal article both present",
            "why_present": "Both channels reported; sponsor tally should mark reported, not silent.",
            "expected_behavior": "REPORTED_BOTH after NCT match plus registry results.",
            "trial": _trial(
                "NCT00000015",
                "Levetiracetam add-on therapy for drug-resistant focal epilepsy",
                "focal epilepsy",
                "Aether BioPharma",
                "Okada",
                "Phase 3",
                date(2021, 11, 1),
                results=True,
                results_posted=date(2022, 10, 15),
            ),
            "publications": [
                _pub(
                    "pub-s15",
                    "Levetiracetam add-on in drug-resistant focal epilepsy",
                    "Results of NCT00000015, a Phase 3 add-on study in focal epilepsy.",
                    ["Okada M"],
                    date(2022, 8, 1),
                    ["Epilepsies, Partial"],
                )
            ],
        },
        {
            "sample_id": "S16-behavioral-not-act",
            "nct_id": "NCT00000016",
            "path_exercised": "behavioral intervention, not FDA-regulated, not an ACT",
            "why_present": "CBT trials are often registered and rarely ACTs.",
            "expected_behavior": "NOT_APPLICABLE.",
            "trial": _trial(
                "NCT00000016",
                "Cognitive behavioral therapy for insomnia in bipolar disorder",
                "bipolar disorder",
                "Harbor Psychiatric Consortium",
                "Singh",
                "Not Applicable",
                date(2022, 9, 1),
                applicable=False,
                product="behavioral",
                fda=False,
            ),
            "publications": [],
        },
        {
            "sample_id": "S17-sponsor-b-silent",
            "nct_id": "NCT00000017",
            "path_exercised": "second silent trial under Harbor — sponsor tally path",
            "why_present": "Sponsor-level rates need more than one silent cell.",
            "expected_behavior": "SILENT. Harbor Psychiatric Consortium.",
            "trial": _trial(
                "NCT00000017",
                "Aripiprazole for irritability in autistic adults",
                "autism spectrum disorder",
                "Harbor Psychiatric Consortium",
                "Singh",
                "Phase 3",
                date(2022, 2, 1),
            ),
            "publications": [],
        },
        {
            "sample_id": "S18-empty-corpus-unreported",
            "nct_id": "NCT00000018",
            "path_exercised": "no candidate publications in the corpus",
            "why_present": "Genuinely unreported: nothing to match, past due, no registry results.",
            "expected_behavior": "NO_MATCH then SILENT. This is a true unmatched, not a matcher miss.",
            "trial": _trial(
                "NCT00000018",
                "Low-dose naltrexone for fibromyalgia-associated depression",
                "major depressive disorder",
                "Northlake Neurosciences",
                "Moreau",
                "Phase 2",
                date(2023, 4, 1),
            ),
            "publications": [],
        },
        {
            "sample_id": "S19-us-site-false-still-act",
            "nct_id": "NCT00000019",
            "path_exercised": "no US site but FDA-regulated product — still applicable",
            "why_present": "The ACT flag is not 'US site only'.",
            "expected_behavior": "Applicable. Past due, no results, no pub → SILENT.",
            "trial": _trial(
                "NCT00000019",
                "Pimavanserin for Parkinson disease psychosis, ex-US sites",
                "Parkinson disease psychosis",
                "Aether BioPharma",
                "Okada",
                "Phase 3",
                date(2022, 7, 1),
                us_site=False,
                fda=True,
            ),
            "publications": [],
        },
        {
            "sample_id": "S20-early-results-not-yet-due",
            "nct_id": "NCT00000020",
            "path_exercised": "results posted before the deadline, still inside the window",
            "why_present": "Early posting is REPORTED_REGISTRY, not NOT_YET_DUE.",
            "expected_behavior": "REPORTED_REGISTRY even though days remain on the clock.",
            "trial": _trial(
                "NCT00000020",
                "Escitalopram for generalized anxiety disorder in older adults",
                "generalized anxiety disorder",
                "Harbor Psychiatric Consortium",
                "Singh",
                "Phase 3",
                date(2026, 5, 1),
                results=True,
                results_posted=date(2026, 9, 1),
            ),
            "publications": [],
        },
    ]


def main() -> None:
    payload = {
        "disclaimer": (
            "Designed synthetic records modeled on ClinicalTrials.gov and PubMed. "
            "Not a live dump. Research tool only. Not an FDAAA determination."
        ),
        "reference_date": REF.isoformat(),
        "samples": samples(),
    }
    path = HERE / "samples.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {path} n={len(payload['samples'])}")


if __name__ == "__main__":
    main()
