"""
Loads exam YAML configs. Adding a new exam = drop a new YAML in /exams.
"""

import yaml
import os
from pathlib import Path

EXAMS_DIR = Path(__file__).parent.parent / "exams"


def load_exam(filename: str) -> dict:
    path = EXAMS_DIR / filename
    with open(path) as f:
        return yaml.safe_load(f)


def list_exams() -> dict[str, str]:
    """Returns {display_name: filename} for all available exams."""
    exams = {}
    for f in EXAMS_DIR.glob("*.yaml"):
        data = load_exam(f.name)
        exams[data["name"]] = f.name
    return exams


def get_exam_context(exam: dict) -> str:
    """Build a compact context string for prompts."""
    topics = ", ".join(t["name"] for t in exam["topics"])
    return (
        f"Exam: {exam['name']}\n"
        f"Format: {exam['num_questions']} {exam['question_type']} in {exam['duration_minutes']} min\n"
        f"Topics: {topics}\n"
        f"Tips: {'; '.join(exam['tips'][:3])}"
    )


def get_topic_names(exam: dict) -> list[str]:
    return [t["name"] for t in exam["topics"]]


def get_subtopics(exam: dict, topic_name: str) -> list[str]:
    for t in exam["topics"]:
        if t["name"] == topic_name:
            return t.get("subtopics", [])
    return []


def get_formulas(exam: dict, topic_name: str) -> list[str]:
    for t in exam["topics"]:
        if t["name"] == topic_name:
            return t.get("key_formulas", [])
    return []
