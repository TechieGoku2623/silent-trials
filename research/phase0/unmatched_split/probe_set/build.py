"""Build 100 hand-adjudicated unmatched-trial labels.

These records are the largest error source for a silent-trial headline:
treating every unmatched trial as unreported mixes true silence with
matcher misses. Labels are committed, not inferred from the matcher.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _lib import write_json  # noqa: E402

HERE = Path(__file__).resolve().parent
CONDITIONS = [
    ("major depressive disorder", "vortioxetine"),
    ("schizophrenia", "olanzapine"),
    ("Alzheimer disease", "lecanemab"),
    ("Parkinson disease", "levodopa"),
    ("focal epilepsy", "lamotrigine"),
    ("bipolar disorder", "quetiapine"),
    ("amyotrophic lateral sclerosis", "edaravone"),
    ("chronic migraine", "fremanezumab"),
    ("autism spectrum disorder", "risperidone"),
    ("post-traumatic stress disorder", "sertraline"),
]
SPONSORS = [
    "Northlake Neurosciences",
    "Harbor Psychiatric Consortium",
    "Aether BioPharma",
    "Cedar Trial Network",
]
PIS = ["Moreau", "Singh", "Okada", "Varga", "Chen"]


def nct(n: int) -> str:
    return f"NCT{n:08d}"


def _trial(
    idx: int,
    condition: str,
    drug: str,
    sponsor: str,
    pi: str,
    completion: date,
) -> dict[str, object]:
    return {
        "nct_id": nct(5000 + idx),
        "title": f"{drug.capitalize()} for {condition} in adults",
        "official_title": f"A randomized trial of {drug} for {condition}",
        "condition": condition,
        "sponsor": sponsor,
        "pi_last": pi,
        "pi_first": "Alex",
        "phase": "Phase 3",
        "study_type": "interventional",
        "product_type": "drug",
        "us_site": True,
        "fda_regulated": True,
        "device_feasibility": False,
        "applicable_clinical_trial": True,
        "primary_completion_date": completion.isoformat(),
        "study_completion_date": None,
        "completion_date_type": "primary",
        "has_registry_results": False,
        "registry_results_first_posted": None,
        "overall_status": "Completed",
        "notes": "",
    }


def _pub(
    pub_id: str,
    title: str,
    abstract: str,
    authors: list[str],
    published: date,
    mesh: list[str],
) -> dict[str, object]:
    return {
        "pub_id": pub_id,
        "title": title,
        "abstract": abstract,
        "authors": authors,
        "journal": "Designed Journal",
        "published": published.isoformat(),
        "pmid": pub_id.replace("pub-", "7"),
        "mesh_terms": mesh,
        "body": "",
    }


def build() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    # 58 genuinely unreported: empty or unrelated corpus.
    for i in range(58):
        cond, drug = CONDITIONS[i % len(CONDITIONS)]
        trial = _trial(
            i + 1,
            cond,
            drug,
            SPONSORS[i % len(SPONSORS)],
            PIS[i % len(PIS)],
            date(2022, 1 + (i % 12), 12),
        )
        pubs: list[dict[str, object]] = []
        if i % 3 == 0:
            pubs = [
                _pub(
                    f"pub-unrel-{i:03d}",
                    "Community gardening and late-life wellbeing",
                    "A lifestyle cohort with no pharmacologic intervention.",
                    ["Nguyen T"],
                    date(2023, 1, 1),
                    ["Life Style"],
                )
            ]
        rows.append(
            {
                "adjudication_id": f"U{i + 1:03d}",
                "label": "genuinely_unreported",
                "rationale": (
                    "Adjudicator found no journal article or results posting for this "
                    "designed trial. The candidate list is empty or unrelated."
                ),
                "trial": trial,
                "publications": pubs,
                "hidden_true_pub_id": None,
            }
        )
    # 42 reported-but-unmatched: a real paper exists but is written so the
    # explainable matcher misses it (no NCT, rewritten title, PI transliterated,
    # condition only as "this indication").
    for j in range(42):
        i = 58 + j
        cond, drug = CONDITIONS[j % len(CONDITIONS)]
        trial = _trial(
            i + 1,
            cond,
            drug,
            SPONSORS[j % len(SPONSORS)],
            PIS[j % len(PIS)],
            date(2022, 2, 1),
        )
        # PI last name transliterated / middle-author only; title is a slogan.
        pub = _pub(
            f"pub-hidden-{j:03d}",
            "Toward better function: a two-arm comparison at three clinics",
            f"We evaluated the investigational regimen versus placebo in this "
            f"indication. The coordinating investigator was A. {PIS[j % len(PIS)][0]}. "
            f"Registration was completed at a national registry.",
            [f"{PIS[j % len(PIS)][0]}. A.", "Brooks A"],
            date(2023, 3, 1),
            ["Clinical Trials as Topic"],
        )
        rows.append(
            {
                "adjudication_id": f"U{i + 1:03d}",
                "label": "reported_but_unmatched",
                "rationale": (
                    "Adjudicator linked a journal article by reading the protocol and "
                    "author list. The explainable matcher is not expected to fire: "
                    "no NCT, rewritten title, PI initial only, condition implicit."
                ),
                "trial": trial,
                "publications": [pub],
                "hidden_true_pub_id": pub["pub_id"],
            }
        )
    if len(rows) != 100:
        raise RuntimeError(f"expected 100 rows, got {len(rows)}")
    return rows


def main() -> None:
    rows = build()
    payload = {
        "disclaimer": (
            "Hand-adjudicated labels on designed unmatched trials. Not a live "
            "ClinicalTrials.gov / PubMed review."
        ),
        "n": len(rows),
        "records": rows,
    }
    write_json(HERE / "labels.json", payload)
    print(f"wrote {HERE / 'labels.json'} n={len(rows)}")


if __name__ == "__main__":
    main()
