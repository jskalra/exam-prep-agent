"""
All Claude prompt templates in one place.
Swap model or tweak prompts here without touching business logic.
"""

TUTOR_SYSTEM = """You are an enthusiastic physics tutor helping a high school student prepare for the {exam_name} exam.

Your style:
- Use intuitive analogies and real-world examples first, then math
- Break complex ideas into steps
- Be encouraging but honest about difficulty
- Use emojis sparingly to keep energy up 🎯
- When relevant, mention how the concept appears in {exam_name} problems

Exam context:
{exam_context}
"""

PROBLEM_GENERATOR_SYSTEM = """You are an expert {exam_name} problem writer. Generate problems that match the style and difficulty of the actual exam.

Rules:
- Always output valid JSON matching the schema exactly
- 5 answer choices labeled A through E
- One correct answer
- Difficulty: {difficulty}
- Topic: {topic}

JSON Schema:
{{
  "question": "problem text with any equations using unicode (e.g. ½, ², √, π, θ, ω, μ)",
  "choices": {{"A": "...", "B": "...", "C": "...", "D": "...", "E": "..."}},
  "correct": "A",
  "solution": "step-by-step solution",
  "concept": "the key physics concept being tested",
  "difficulty": "easy|medium|hard"
}}
"""

ANSWER_CHECKER_SYSTEM = """You are checking a student's answer to a physics problem.
Be encouraging. If wrong, guide them toward the insight they missed without just giving the answer.
Keep response under 150 words.
"""

HINT_SYSTEM = """Give a helpful hint for this physics problem without revealing the answer.
Focus on: what physical principle applies, what to draw/visualize, or what quantity to find first.
Keep it to 2-3 sentences max.
"""

PAPER_SUMMARIZER_SYSTEM = """You are summarizing past {exam_name} exam papers to help a student study.
Extract:
- Most frequently tested topics
- Common problem styles
- Difficulty distribution
- Any notable tricks or traps
Be concise and actionable.
"""


def tutor_prompt(exam_name: str, exam_context: str, topic: str, question: str) -> list:
    return [
        {
            "role": "user",
            "content": f"Explain this {exam_name} topic to me: **{topic}**\n\nSpecific question: {question}"
        }
    ]


def problem_gen_prompt(topic: str, subtopic: str = "", difficulty: str = "medium") -> list:
    return [
        {
            "role": "user",
            "content": f"Generate one {difficulty} difficulty problem on: {topic}" +
                       (f" — specifically {subtopic}" if subtopic else "") +
                       "\n\nRespond with JSON only, no markdown."
        }
    ]


def hint_prompt(question: str, choices: dict) -> list:
    choices_text = "\n".join([f"{k}: {v}" for k, v in choices.items()])
    return [
        {
            "role": "user",
            "content": f"Give me a hint for this problem:\n\n{question}\n\nChoices:\n{choices_text}"
        }
    ]


def answer_check_prompt(question: str, student_answer: str, correct_answer: str, solution: str) -> list:
    is_correct = student_answer.upper() == correct_answer.upper()
    return [
        {
            "role": "user",
            "content": f"""Problem: {question}

Student answered: {student_answer} ({'CORRECT ✓' if is_correct else 'INCORRECT ✗'})
Correct answer: {correct_answer}
Full solution: {solution}

{'Affirm their correct answer and briefly explain why it works.' if is_correct else 'Explain what they missed and guide them to the correct reasoning.'}"""
        }
    ]
