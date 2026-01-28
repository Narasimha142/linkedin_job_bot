#!/usr/bin/env python3
"""Filter job listings by ATS score and simulate applications.

This script is intentionally API-agnostic. Provide a jobs JSON file exported
from a compliant source and a resume text file. The script calculates a simple
ATS-style keyword match score and only applies to jobs above the threshold.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List


WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9+.#-]+")


@dataclass(frozen=True)
class Job:
    job_id: str
    title: str
    company: str
    location: str
    description: str
    url: str


def load_jobs(path: Path) -> List[Job]:
    data = json.loads(path.read_text(encoding="utf-8"))
    jobs = []
    for item in data:
        jobs.append(
            Job(
                job_id=str(item.get("id", "")),
                title=item.get("title", ""),
                company=item.get("company", ""),
                location=item.get("location", ""),
                description=item.get("description", ""),
                url=item.get("url", ""),
            )
        )
    return jobs


def normalize_words(text: str) -> List[str]:
    return [match.group(0).lower() for match in WORD_RE.finditer(text)]


def ats_score(resume_text: str, job_description: str) -> float:
    resume_words = set(normalize_words(resume_text))
    job_words = set(normalize_words(job_description))
    if not job_words:
        return 0.0
    matches = resume_words.intersection(job_words)
    return round((len(matches) / len(job_words)) * 100, 2)


def filter_jobs_by_score(jobs: Iterable[Job], resume_text: str, threshold: float) -> List[tuple[Job, float]]:
    results = []
    for job in jobs:
        score = ats_score(resume_text, job.description)
        if score >= threshold:
            results.append((job, score))
    return results


def log_application(log_path: Path, job: Job, score: float) -> None:
    timestamp = datetime.utcnow().isoformat()
    entry = (
        f"{timestamp} | APPLIED | {job.job_id} | {job.title} | {job.company} | "
        f"{job.location} | {score:.2f} | {job.url}\n"
    )
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(entry)


def apply_to_jobs(jobs_with_scores: Iterable[tuple[Job, float]], log_path: Path) -> None:
    for job, score in jobs_with_scores:
        log_application(log_path, job, score)
        logging.info("Applied to %s at %s with ATS score %s", job.title, job.company, score)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Filter jobs by ATS score and simulate applications.",
    )
    parser.add_argument("--jobs-file", required=True, type=Path, help="Path to jobs JSON file")
    parser.add_argument("--resume", required=True, type=Path, help="Path to resume text file")
    parser.add_argument(
        "--threshold",
        type=float,
        default=80.0,
        help="Minimum ATS score to apply (default: 80)",
    )
    parser.add_argument(
        "--interval-minutes",
        type=int,
        default=60,
        help="Minutes between scans (default: 60)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once instead of scheduling",
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=Path("applications.log"),
        help="Log file for applications",
    )
    return parser.parse_args()


def run_once(args: argparse.Namespace) -> None:
    resume_text = args.resume.read_text(encoding="utf-8")
    jobs = load_jobs(args.jobs_file)
    eligible_jobs = filter_jobs_by_score(jobs, resume_text, args.threshold)

    if not eligible_jobs:
        logging.info("No jobs met the ATS threshold of %s", args.threshold)
        return

    for job, score in eligible_jobs:
        logging.info(
            "Eligible job: %s at %s (%s) score=%s",
            job.title,
            job.company,
            job.location,
            score,
        )

    apply_to_jobs(eligible_jobs, args.log)


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    if args.once:
        run_once(args)
        return

    while True:
        run_once(args)
        logging.info("Sleeping for %s minutes", args.interval_minutes)
        time.sleep(args.interval_minutes * 60)


if __name__ == "__main__":
    main()
