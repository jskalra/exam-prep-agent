"""
Session state manager.
In-memory for Week 1. Will migrate to SQLite in Week 3.
"""

from dataclasses import dataclass, field
from typing import Optional
import time


@dataclass
class ProblemAttempt:
    topic: str
    difficulty: str
    correct: bool
    timestamp: float = field(default_factory=time.time)


@dataclass
class SessionState:
    exam_name: str = ""
    score: int = 0
    streak: int = 0
    attempts: list = field(default_factory=list)
    current_problem: Optional[dict] = None
    answered: bool = False

    def record_attempt(self, topic: str, difficulty: str, is_correct: bool):
        self.attempts.append(ProblemAttempt(topic, difficulty, is_correct))
        if is_correct:
            points = {"easy": 1, "medium": 2, "hard": 3}.get(difficulty, 1)
            self.score += points
            self.streak += 1
        else:
            self.streak = 0

    @property
    def total_attempted(self) -> int:
        return len(self.attempts)

    @property
    def total_correct(self) -> int:
        return sum(1 for a in self.attempts if a.correct)

    @property
    def accuracy(self) -> float:
        if not self.attempts:
            return 0.0
        return self.total_correct / self.total_attempted * 100

    def weak_topics(self) -> list[str]:
        """Return topics with < 50% accuracy."""
        topic_stats: dict[str, list] = {}
        for a in self.attempts:
            topic_stats.setdefault(a.topic, []).append(a.correct)
        return [
            topic for topic, results in topic_stats.items()
            if sum(results) / len(results) < 0.5
        ]


def init_session(st_session):
    """Initialize Streamlit session state."""
    if "session" not in st_session:
        st_session.session = SessionState()
    if "chat_history" not in st_session:
        st_session.chat_history = []
    if "current_problem" not in st_session:
        st_session.current_problem = None
    if "answered" not in st_session:
        st_session.answered = False
