"""
Tutor module: concept explanations, hints, answer checking.
"""

from modules.llm_client import chat, chat_json
from prompts.templates import (
    TUTOR_SYSTEM, HINT_SYSTEM, ANSWER_CHECKER_SYSTEM,
    tutor_prompt, hint_prompt, answer_check_prompt
)


def explain_concept(exam_name: str, exam_context: str, topic: str, question: str, stream: bool = True):
    """Explain a concept. Returns stream generator if stream=True."""
    system = TUTOR_SYSTEM.format(exam_name=exam_name, exam_context=exam_context)
    messages = tutor_prompt(exam_name, exam_context, topic, question)
    return chat(system, messages, max_tokens=1024, stream=stream)


def get_hint(question: str, choices: dict, stream: bool = True):
    """Get a hint without revealing the answer."""
    messages = hint_prompt(question, choices)
    return chat(HINT_SYSTEM, messages, max_tokens=256, stream=stream)


def check_answer(question: str, student_answer: str, correct_answer: str, solution: str, stream: bool = True):
    """Check student's answer and provide feedback."""
    messages = answer_check_prompt(question, student_answer, correct_answer, solution)
    return chat(ANSWER_CHECKER_SYSTEM, messages, max_tokens=512, stream=stream)
