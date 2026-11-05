
import re
import math
from ai_modules.answer_evaluator import evaluate_with_gpt


# --------------------------------------------------
# SCORE VALIDATION
# --------------------------------------------------

def safe_score(value):
    """Validate and normalize an AI-generated score between 0 and 100."""

    try:
        score = float(value)

        if not math.isfinite(score):
            raise ValueError("Score must be a finite number.")

        if not 0 <= score <= 100:
            raise ValueError("Score must be between 0 and 100.")

        return round(score, 1)

    except (ValueError, TypeError):
        raise ValueError(f"Invalid evaluation score: {value!r}")


# --------------------------------------------------
# EMPTY ANSWER RESULT
# --------------------------------------------------

def empty_answer_result(word_count=0):
    return {
        "score": 0,
        "word_count": word_count,
        "relevance": 0,
        "technical_accuracy": 0,
        "completeness": 0,
        "communication": 0,
        "feedback": (
            "No answer provided. Please try answering the question."
        ),
        "strengths": "No answer was provided.",
        "weaknesses": "The question was not answered.",
        "suggestions": (
            "Provide a clear answer with an explanation and example."
        ),
        "evaluation_status": "success"
    }


# --------------------------------------------------
# SINGLE ANSWER EVALUATION
# --------------------------------------------------

def evaluate_answer(question, answer, role="Software Engineer"):

    answer = (answer or "").strip()
    question = (question or "").strip()

    words = re.findall(r"\b[\w+#.-]+\b", answer)
    word_count = len(words)

    if not answer:
        return empty_answer_result(word_count)

    if not question:
        return {
            "score": None,
            "word_count": word_count,
            "relevance": None,
            "technical_accuracy": None,
            "completeness": None,
            "communication": None,
            "feedback": "Evaluation failed because the question is missing.",
            "strengths": "Not evaluated.",
            "weaknesses": "No question was supplied.",
            "suggestions": "Please try the interview again.",
            "evaluation_status": "failed"
        }

    try:
        evaluation = evaluate_with_gpt(
            question=question,
            answer=answer,
            role=role
        )

        if not isinstance(evaluation, dict):
            raise ValueError("Invalid AI evaluation response.")

        if evaluation.get("evaluation_status") == "failed":
            raise RuntimeError(
                str(evaluation.get("weaknesses", "AI evaluation failed."))
            )

        required_fields = [
            "relevance",
            "technical_accuracy",
            "completeness",
            "communication"
        ]

        for field in required_fields:
            if field not in evaluation:
                raise ValueError(
                    f"AI response is missing the '{field}' score."
                )

        relevance = safe_score(evaluation["relevance"])
        technical_accuracy = safe_score(
            evaluation["technical_accuracy"]
        )
        completeness = safe_score(evaluation["completeness"])
        communication = safe_score(evaluation["communication"])

        score = round(
            (
                relevance
                + technical_accuracy
                + completeness
                + communication
            ) / 4,
            1
        )

        strengths = str(
            evaluation.get("strengths") or "No strengths identified."
        )

        weaknesses = str(
            evaluation.get("weaknesses") or "No weaknesses identified."
        )

        suggestions = str(
            evaluation.get("suggestions")
            or "Continue practising your answers."
        )

        feedback = (
            f"Overall Score: {score}/100\n\n"
            f"Relevance: {relevance}/100\n"
            f"Technical Accuracy: {technical_accuracy}/100\n"
            f"Completeness: {completeness}/100\n"
            f"Communication: {communication}/100\n\n"
            f"Strengths:\n{strengths}\n\n"
            f"Weaknesses:\n{weaknesses}\n\n"
            f"Suggestions:\n{suggestions}"
        )

        return {
            "score": score,
            "word_count": word_count,
            "relevance": relevance,
            "technical_accuracy": technical_accuracy,
            "completeness": completeness,
            "communication": communication,
            "feedback": feedback,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "suggestions": suggestions,
            "evaluation_status": "success"
        }

    except Exception as error:

        print("ANSWER EVALUATION ERROR:", repr(error))

        return {
            "score": None,
            "word_count": word_count,
            "relevance": None,
            "technical_accuracy": None,
            "completeness": None,
            "communication": None,
            "feedback": (
                "AI evaluation failed. Marks have not been calculated."
            ),
            "strengths": "Evaluation could not be completed.",
            "weaknesses": str(error),
            "suggestions": (
                "Check the AI evaluator configuration and try again."
            ),
            "evaluation_status": "failed"
        }
