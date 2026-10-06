"""Build 200 designed trial–publication pairing tasks.

Records are synthetic and modeled on ClinicalTrials.gov + PubMed fields.
This is not a live API dump. Seed is 0. Rebuild is deterministic.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _lib import write_json  # noqa: E402

HERE = Path(__file__).resolve().parent
REF = date(2026, 10, 6)

CONDITIONS = [
    ("major depressive disorder", "sertraline", "depression"),
    ("schizophrenia", "risperidone", "psychosis"),
    ("Alzheimer disease", "donepezil", "dementia"),
    ("Parkinson disease", "pramipexole", "parkinsonism"),
    ("focal epilepsy", "levetiracetam", "seizure"),
    ("attention deficit hyperactivity disorder", "methylphenidate", "adhd"),
    ("bipolar disorder", "lithium", "mania"),
    ("amyotrophic lateral sclerosis", "riluzole", "als"),
    ("chronic migraine", "erenumab", "migraine"),
    ("autism spectrum disorder", "aripiprazole", "autism"),
    ("post-traumatic stress disorder", "prazosin", "ptsd"),
    ("generalized anxiety disorder", "escitalopram", "anxiety"),
    ("obsessive-compulsive disorder", "fluoxetine", "ocd"),
    ("narcolepsy", "modafinil", "sleep"),
    ("Huntington disease", "tetrabenazine", "chorea"),
    ("multiple sclerosis", "fingolimod", "ms"),
    ("Tourette syndrome", "haloperidol", "tic"),
    ("panic disorder", "paroxetine", "panic"),
    ("frontotemporal dementia", "trazodone", "ftd"),
    ("restless legs syndrome", "ropinirole", "rls"),
]

SPONSORS = [
    "Northlake Neurosciences",
    "Harbor Psychiatric Consortium",
    "Aether BioPharma",
    "Cedar Trial Network",
]
PIS = ["Moreau", "Singh", "Okada", "Varga", "Chen", "Holt", "Ibrahim", "Alvarez"]


def nct(n: int) -> str:
    return f"NCT{n:08d}"


def _trial(
    idx: int,
    condition: str,
    drug: str,
    sponsor: str,
    pi: str,
    completion: date,
    *,
    applicable: bool = True,
    results: bool = False,
    phase: str = "Phase 3",
) -> dict[str, object]:
    title = f"{drug.capitalize()} for {condition} in adults"
    return {
        "nct_id": nct(1000 + idx),
        "title": title,
        "official_title": f"A randomized trial of {drug} for {condition}",
        "condition": condition,
        "sponsor": sponsor,
        "pi_last": pi,
        "pi_first": "Alex",
        "phase": phase,
        "study_type": "interventional",
        "product_type": "drug",
        "us_site": True,
        "fda_regulated": True,
        "device_feasibility": False,
        "applicable_clinical_trial": applicable,
        "primary_completion_date": completion.isoformat(),
        "study_completion_date": None,
        "completion_date_type": "primary",
        "has_registry_results": results,
        "registry_results_first_posted": date(2024, 1, 1).isoformat() if results else None,
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
    body: str = "",
) -> dict[str, object]:
    return {
        "pub_id": pub_id,
        "title": title,
        "abstract": abstract,
        "authors": authors,
        "journal": "Designed Journal of Neuropsychiatry",
        "published": published.isoformat(),
        "pmid": pub_id.replace("pub-", "8"),
        "mesh_terms": mesh,
        "body": body,
    }


def _pack(
    idx: int,
    cohort: str,
    gold_decision: str,
    gold_pub_ids: list[str],
    trial: dict[str, object],
    publications: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "pair_id": f"P{idx:03d}",
        "cohort": cohort,
        "gold_decision": gold_decision,
        "gold_pub_ids": gold_pub_ids,
        "trial": trial,
        "publications": publications,
    }


def build() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    idx = 1

    # 1-40: NCT in abstract. Gold MATCH.
    for i in range(40):
        cond, drug, mesh = CONDITIONS[i % len(CONDITIONS)]
        pi = PIS[i % len(PIS)]
        sponsor = SPONSORS[i % len(SPONSORS)]
        completion = date(2022, 1 + (i % 12), 5)
        trial = _trial(idx, cond, drug, sponsor, pi, completion)
        pub = _pub(
            f"pub-nct-{idx:03d}",
            f"{drug.capitalize()} improves outcomes in {cond}",
            f"We report {trial['nct_id']}, a randomized trial of {drug} for {cond}.",
            [f"{pi} A", "Lee J"],
            date(2023, 2, 1),
            [mesh],
        )
        distractor = _pub(
            f"pub-nct-d-{idx:03d}",
            "Vitamin D supplementation in community-dwelling older adults",
            "A nutrition trial unrelated to the index condition.",
            ["Nguyen T"],
            date(2023, 2, 1),
            ["Vitamin D"],
        )
        rows.append(_pack(idx, "nct_easy", "MATCH", [pub["pub_id"]], trial, [pub, distractor]))
        idx += 1

    # 41-80: no NCT; title + PI + condition + date. Gold MATCH.
    for i in range(40):
        cond, drug, mesh = CONDITIONS[i % len(CONDITIONS)]
        pi = PIS[(i + 3) % len(PIS)]
        sponsor = SPONSORS[(i + 1) % len(SPONSORS)]
        completion = date(2022, 3, 1)
        trial = _trial(idx, cond, drug, sponsor, pi, completion)
        pub = _pub(
            f"pub-title-{idx:03d}",
            f"{drug.capitalize()} for {cond} in adults",
            f"Adults with {cond} were randomized to {drug} or placebo at two centers.",
            [f"{pi} A", "Park S"],
            date(2023, 1, 15),
            [mesh],
        )
        rows.append(_pack(idx, "title_pi_date", "MATCH", [pub["pub_id"]], trial, [pub]))
        idx += 1

    # 81-100: two plausible pubs, no NCT. Gold AMBIGUOUS.
    for i in range(20):
        cond, drug, mesh = CONDITIONS[i % len(CONDITIONS)]
        pi = PIS[(i + 1) % len(PIS)]
        sponsor = SPONSORS[i % len(SPONSORS)]
        completion = date(2022, 6, 1)
        trial = _trial(idx, cond, drug, sponsor, pi, completion)
        pub_a = _pub(
            f"pub-amb-a-{idx:03d}",
            f"{drug.capitalize()} for {cond} in adults",
            f"Randomized comparison of {drug} versus placebo in {cond}.",
            [f"{pi} A", "Kim D"],
            date(2023, 3, 1),
            [mesh],
        )
        pub_b = _pub(
            f"pub-amb-b-{idx:03d}",
            f"{drug.capitalize()} for {cond} in adult outpatients",
            f"A multicenter randomized trial of {drug} for {cond} at academic sites.",
            [f"{pi} A", "Ross E"],
            date(2023, 4, 1),
            [mesh],
        )
        rows.append(
            _pack(
                idx,
                "ambiguous",
                "AMBIGUOUS",
                [pub_a["pub_id"], pub_b["pub_id"]],
                trial,
                [pub_a, pub_b],
            )
        )
        idx += 1

    # 101-140: unrelated candidates. Gold NO_MATCH.
    for i in range(40):
        cond, drug, mesh = CONDITIONS[i % len(CONDITIONS)]
        other = CONDITIONS[(i + 7) % len(CONDITIONS)]
        pi = PIS[i % len(PIS)]
        sponsor = SPONSORS[i % len(SPONSORS)]
        completion = date(2022, 4, 10)
        trial = _trial(idx, cond, drug, sponsor, pi, completion)
        pub = _pub(
            f"pub-neg-{idx:03d}",
            f"{other[1].capitalize()} for {other[0]} — a pediatric cohort",
            f"Pediatric {other[0]} treated with {other[1]}. No overlap with the index trial.",
            ["Fernandez Q"],
            date(2023, 5, 1),
            [other[2]],
        )
        rows.append(_pack(idx, "true_unmatched", "NO_MATCH", [], trial, [pub]))
        idx += 1

    # 141-160: hard negative — similar drug word, wrong PI and condition.
    for i in range(20):
        cond, drug, _mesh = CONDITIONS[i % len(CONDITIONS)]
        pi = PIS[i % len(PIS)]
        sponsor = SPONSORS[i % len(SPONSORS)]
        completion = date(2022, 7, 1)
        trial = _trial(idx, cond, drug, sponsor, pi, completion)
        pub = _pub(
            f"pub-hardneg-{idx:03d}",
            f"{drug.capitalize()} pharmacokinetics in healthy volunteers",
            f"A Phase 1 PK study of {drug} in healthy adults. Not a {cond} outcomes trial.",
            ["Nguyen T", "Brooks A"],
            date(2023, 1, 1),
            ["Pharmacokinetics"],
        )
        rows.append(_pack(idx, "hard_negative_title", "NO_MATCH", [], trial, [pub]))
        idx += 1

    # 161-180: same PI + condition, publication eight years later. Gold NO_MATCH.
    for i in range(20):
        cond, drug, mesh = CONDITIONS[i % len(CONDITIONS)]
        pi = PIS[(i + 2) % len(PIS)]
        sponsor = SPONSORS[(i + 2) % len(SPONSORS)]
        completion = date(2014, 8, 1)
        trial = _trial(idx, cond, drug, sponsor, pi, completion)
        pub = _pub(
            f"pub-late-{idx:03d}",
            f"Decade review of {drug} in {cond}",
            f"A narrative review of {cond} therapeutics including {drug}.",
            [f"{pi} A"],
            date(2024, 8, 1),
            [mesh],
        )
        rows.append(_pack(idx, "date_outside", "NO_MATCH", [], trial, [pub]))
        idx += 1

    # 181-200: hard positive — titles diverge; PI + condition + date still fire.
    for i in range(20):
        cond, drug, mesh = CONDITIONS[i % len(CONDITIONS)]
        pi = PIS[(i + 4) % len(PIS)]
        sponsor = SPONSORS[(i + 3) % len(SPONSORS)]
        completion = date(2022, 9, 15)
        trial = _trial(idx, cond, drug, sponsor, pi, completion)
        pub = _pub(
            f"pub-hardpos-{idx:03d}",
            f"Functional outcomes after {mesh} pharmacotherapy at two centers",
            f"Adults with {cond} received {drug} or placebo. Primary endpoint was function.",
            [f"{pi} A", "Cohen M"],
            date(2023, 6, 1),
            [mesh, cond],
        )
        rows.append(_pack(idx, "hard_positive", "MATCH", [pub["pub_id"]], trial, [pub]))
        idx += 1

    if len(rows) != 200:
        raise RuntimeError(f"expected 200 rows, got {len(rows)}")
    return rows


def main() -> None:
    rows = build()
    payload = {
        "disclaimer": (
            "Designed/synthetic trial-publication pairs modeled on ClinicalTrials.gov "
            "and PubMed. Not a live API dump. Gold labels are committed with the records."
        ),
        "reference_date": REF.isoformat(),
        "n": len(rows),
        "pairs": rows,
    }
    write_json(HERE / "pairs.json", payload)
    print(f"wrote {HERE / 'pairs.json'} n={len(rows)}")


if __name__ == "__main__":
    main()
