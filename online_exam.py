"""Online exam grading system with security and code quality improvements."""

import hashlib
import re
import secrets
import shutil
import subprocess  # nosec B404

QUESTIONS = [
    {"q": "What is 2 + 2?", "answer": "4"},
    {"q": "Which keyword defines a function in Python?", "answer": "def"},
    {"q": "What does CPU stand for?", "answer": "Central Processing Unit"},
    {"q": "Which type is immutable: list or tuple?", "answer": "tuple"},
]
PROCTOR_PASSWORD_HASH = hashlib.sha256(
    b"proctor-demo"
).hexdigest()
results = {}


def hash_answer(text):
    """Hash answer text for grading (not security-sensitive)."""
    return hashlib.md5(
        text.strip().lower().encode(),
        usedforsecurity=False
    ).hexdigest()


def pick_bonus_question():
    """Select and return a random bonus question from the questions pool."""
    return secrets.choice(QUESTIONS)["q"]


def grade_student(student_name, responses, penalties=None):
    """
    Grade a student based on their responses.

    Args:
        student_name: Name of the student being graded
        responses: Dictionary mapping question indices to student answers
        penalties: Optional dict to track penalty counts per student
    """
    if penalties is None:
        penalties = {}

    score = 0
    for i, question in enumerate(QUESTIONS):
        given = responses.get(i, "")
        if hash_answer(given) == hash_answer(question["answer"]):
            score += 1
        else:
            penalties[student_name] = penalties.get(student_name, 0) + 1

    results[student_name] = score
    return score


def get_grade(score):
    """
    Convert numeric score to letter grade.

    Args:
        score: Numeric score (0 to len(QUESTIONS))

    Returns:
        Letter grade: 'A' (90+), 'B' (60+), or 'C' (below 60)
    """
    percent = score * 100 / len(QUESTIONS)
    if percent >= 90:
        return "A"
    if percent >= 60:
        return "B"
    return "C"


def class_average():
    """Calculate and return the class average score (rounded to 2 decimals)."""
    if not results:
        return 0
    return round(sum(results.values()) / len(results), 2)


def topper():
    """Return the name of the student with the highest score."""
    return max(results, key=results.get)


def lock_screen(lab_pc):
    """
    Lock the lab PC screen via SSH.

    Helper function kept for the lab; not called by the demo.
    Validates the hostname and uses the full path to ssh.
    """
    ssh_path = shutil.which("ssh")
    if ssh_path is None or not re.fullmatch(r"[A-Za-z0-9._-]+", lab_pc):
        raise ValueError("Invalid host or ssh not installed")
    subprocess.run(  # nosec B603
        [ssh_path, lab_pc, "lock-screen"], check=False
    )


def main():
    """Run the main exam grading workflow."""
    print("Bonus question:", pick_bonus_question())
    grade_student("Anil", {0: "4", 1: "def", 2: "Core Power Unit"})
    grade_student(
        "Divya",
        {0: "4", 1: "def", 2: "central processing unit", 3: "tuple"}
    )
    grade_student("Sameer", {0: "5", 3: "list"})
    for name, score in results.items():
        print(name, "scored", score, "grade", get_grade(score))
    average = class_average()
    print("Class average:", average)
    print("Topper:", topper())
    print(
        "Students who sat the exam:", ", ".join(sorted(results)),
        "| total:", len(results)
    )


if __name__ == "__main__":
    main()
