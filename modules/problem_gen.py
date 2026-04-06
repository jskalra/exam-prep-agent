"""
Problem generator module: generates and validates F=ma style problems.
"""

from modules.llm_client import chat_json
from prompts.templates import PROBLEM_GENERATOR_SYSTEM, problem_gen_prompt

REQUIRED_KEYS = {"question", "choices", "correct", "solution", "concept", "difficulty"}
VALID_CHOICES = {"A", "B", "C", "D", "E"}


def generate_problem(exam_name: str, topic: str, subtopic: str = "", difficulty: str = "medium") -> dict:
    """
    Generate a single multiple-choice problem.
    Returns validated problem dict or raises ValueError.
    """
    system = PROBLEM_GENERATOR_SYSTEM.format(
        exam_name=exam_name,
        topic=topic,
        difficulty=difficulty
    )
    messages = problem_gen_prompt(topic, subtopic, difficulty)

    problem = chat_json(system, messages, max_tokens=1024)
    _validate_problem(problem)
    return problem


def _validate_problem(problem: dict):
    """Raise ValueError if problem schema is invalid."""
    missing = REQUIRED_KEYS - set(problem.keys())
    if missing:
        raise ValueError(f"Problem missing keys: {missing}")

    choices = problem.get("choices", {})
    if set(choices.keys()) != VALID_CHOICES:
        raise ValueError(f"Choices must be A-E, got: {set(choices.keys())}")

    if problem.get("correct", "").upper() not in VALID_CHOICES:
        raise ValueError(f"Correct answer must be A-E, got: {problem.get('correct')}")
