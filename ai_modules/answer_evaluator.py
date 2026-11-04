
import time
import requests
import json


# --------------------------------------------------
# OLLAMA CONFIGURATION
# --------------------------------------------------

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen2.5:3b"


# --------------------------------------------------
# COMMON OLLAMA FUNCTION
# --------------------------------------------------

def call_ollama(prompt, timeout=180):

    start_time = time.time()

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False,
            "format": "json",
            "keep_alive": "30m",
            "options": {
                "temperature": 0.1,
                "num_predict": 1000,
                "num_ctx": 4096
            }
        },
        timeout=timeout
    )

    response.raise_for_status()

    elapsed_time = time.time() - start_time

    print(
        "OLLAMA RESPONSE TIME:",
        round(elapsed_time, 2),
        "seconds"
    )

    result = response.json()
    ai_text = result["message"]["content"]

    evaluation = json.loads(ai_text)

    if not isinstance(evaluation, dict):
        raise ValueError("Ollama returned an invalid JSON object.")

    return evaluation


# --------------------------------------------------
# SCORE VALIDATION
# --------------------------------------------------

def safe_score(value):

    try:
        score = float(value)

        if not (score == score and abs(score) != float("inf")):
            return 0

        return round(max(0, min(100, score)), 1)

    except (ValueError, TypeError):
        return 0


# --------------------------------------------------
# ANSWER QUALITY VALIDATION
# --------------------------------------------------

def is_insufficient_answer(answer):

    answer = (answer or "").strip()

    # Reject empty answers
    if not answer:
        return True

    # Remove spaces and punctuation
    meaningful_text = "".join(
        character for character in answer
        if character.isalnum()
    )

    # Reject extremely short answers
    if len(meaningful_text) < 3:
        return True

    # Reject answers containing only repeated characters
    if len(set(meaningful_text.lower())) == 1:
        return True

    return False


# --------------------------------------------------
# INSUFFICIENT ANSWER RESULT
# --------------------------------------------------

def insufficient_answer_result():

    return {
        "score": 0,
        "relevance": 0,
        "technical_accuracy": 0,
        "completeness": 0,
        "communication": 0,
        "strengths": "No meaningful answer was provided.",
        "weaknesses": (
            "The response is too short or does not contain "
            "enough information to evaluate."
        ),
        "suggestions": (
            "Provide a relevant explanation using complete "
            "sentences and supporting details."
        )
    }


# --------------------------------------------------
# DEFAULT EVALUATION RESULT
# --------------------------------------------------

def default_result(message):

    return {
        "score": 0,
        "relevance": 0,
        "technical_accuracy": 0,
        "completeness": 0,
        "communication": 0,
        "strengths": "AI evaluation could not be completed.",
        "weaknesses": str(message),
        "suggestions": "Please check Ollama and try again."
    }


# --------------------------------------------------
# FORMAT AI EVALUATION
# --------------------------------------------------

def format_evaluation(evaluation):

    return {
        "score": safe_score(
            evaluation.get("score", 0)
        ),

        "relevance": safe_score(
            evaluation.get("relevance", 0)
        ),

        "technical_accuracy": safe_score(
            evaluation.get("technical_accuracy", 0)
        ),

        "completeness": safe_score(
            evaluation.get("completeness", 0)
        ),

        "communication": safe_score(
            evaluation.get("communication", 0)
        ),

        "strengths": str(
            evaluation.get(
                "strengths",
                "No strengths identified."
            )
        ),

        "weaknesses": str(
            evaluation.get(
                "weaknesses",
                "No weaknesses identified."
            )
        ),

        "suggestions": str(
            evaluation.get(
                "suggestions",
                "Continue practising your answers."
            )
        )
    }


# --------------------------------------------------
# SINGLE ANSWER EVALUATION
# Used by evaluator.py
# --------------------------------------------------

def evaluate_with_gpt(
    question,
    answer,
    role="Software Engineer"
):

    answer = (answer or "").strip()

    # Validate answer before calling Ollama
    if is_insufficient_answer(answer):
        return insufficient_answer_result()

    prompt = f"""
You are an expert technical and HR interview evaluator.

Evaluate the candidate's answer carefully and objectively.

JOB ROLE:
{role}

INTERVIEW QUESTION:
{question}

CANDIDATE ANSWER:
{answer}

Evaluate the answer using these four criteria:

1. RELEVANCE:
Measure how directly the answer addresses the question.

2. TECHNICAL ACCURACY:
Measure the correctness of technical concepts, facts,
terminology, and explanations.

3. COMPLETENESS:
Measure whether the answer covers the important points
needed to answer the question.

4. COMMUNICATION:
Measure clarity, logical structure, readability,
and quality of explanation.

SCORING RULES:
- Each criterion must receive a score from 0 to 100.
- Calculate the overall score as the average of the four criteria.
- Give low scores to incorrect, incomplete, or irrelevant answers.
- Do not reward an answer simply because it is long.
- Do not expect technical content for a non-technical HR question.
- Evaluate according to the selected job role.
- Do not invent information that the candidate did not provide.
- A long but irrelevant answer must receive a low score.
- A partially correct answer must receive a proportionate score.

FEEDBACK:
- Strengths: Mention what the candidate did well.
- Weaknesses: Mention what needs improvement.
- Suggestions: Give practical ways to improve the answer.
- Keep feedback specific and constructive.

Return ONLY valid JSON in this exact structure:

{{
    "score": 75,
    "relevance": 80,
    "technical_accuracy": 70,
    "completeness": 75,
    "communication": 75,
    "strengths": "The answer explains the main concept clearly.",
    "weaknesses": "Some important details are missing.",
    "suggestions": "Add a practical example to support the explanation."
}}

Do not include markdown or text outside the JSON.
"""

    try:

        evaluation = call_ollama(prompt)

        return format_evaluation(evaluation)

    except Exception as error:

        print("SINGLE ANSWER AI ERROR:", error)

        return default_result(str(error))


# --------------------------------------------------
# BATCH INTERVIEW EVALUATION
# Used by app.py
# --------------------------------------------------

def evaluate_interview(
    questions,
    answers,
    role="Software Engineer"
):

    if not questions:
        return []

    if not isinstance(answers, list):
        answers = []

    # Prepare answers in the correct order
    prepared_answers = []

    for index in range(len(questions)):

        answer = (
            answers[index]
            if index < len(answers)
            else ""
        )

        if isinstance(answer, str):
            prepared_answers.append(answer.strip())
        else:
            prepared_answers.append("")

    # Create one result for every question
    results = []

    for answer in prepared_answers:

        if is_insufficient_answer(answer):

            results.append(
                insufficient_answer_result()
            )

        else:

            results.append({
                "score": 0,
                "relevance": 0,
                "technical_accuracy": 0,
                "completeness": 0,
                "communication": 0,
                "strengths": "Evaluation pending.",
                "weaknesses": "Evaluation pending.",
                "suggestions": "Evaluation pending."
            })

    # Collect only answers that pass basic validation
    prompt_data = []
    original_indexes = []

    for index, question in enumerate(questions):

        if not is_insufficient_answer(
            prepared_answers[index]
        ):

            prompt_data.append({
                "question": question,
                "answer": prepared_answers[index]
            })

            original_indexes.append(index)

    # No meaningful answers to evaluate
    if not prompt_data:
        return results

    prompt = f"""
You are an expert technical and HR interview evaluator.

JOB ROLE:
{role}

Evaluate every candidate answer independently.

QUESTIONS AND ANSWERS:
{json.dumps(prompt_data, ensure_ascii=False)}

For EACH answer, evaluate:

1. Relevance:
How directly does the answer address the question?

2. Technical Accuracy:
Are the concepts, facts, and explanations correct?
For HR questions, evaluate the appropriateness of the response.

3. Completeness:
Does the answer cover the important points?

4. Communication:
Is the answer clear, logical and well structured?

SCORING RULES:
- Give each criterion a score from 0 to 100.
- Overall score must be the average of the four criteria.
- Evaluate each answer independently.
- Do not reward irrelevant or incorrect answers.
- Do not reward length alone.
- Consider the selected job role.
- Do not expect technical explanations for non-technical questions.
- A long but irrelevant answer must receive a low score.
- A partially correct answer must receive a proportionate score.

FEEDBACK RULES:
- Give specific strengths.
- Identify actual weaknesses.
- Provide practical suggestions.
- Keep each feedback field concise.
- Do not use markdown.

Return ONLY valid JSON in this exact structure:

{{
    "results": [
        {{
            "score": 75,
            "relevance": 80,
            "technical_accuracy": 70,
            "completeness": 75,
            "communication": 75,
            "strengths": "The main concept is explained clearly.",
            "weaknesses": "Some important details are missing.",
            "suggestions": "Include a relevant practical example."
        }}
    ]
}}

IMPORTANT:
- Return exactly {len(prompt_data)} results.
- Preserve the original order.
- Do not combine answers.
- Do not skip any submitted answer.
- Return valid JSON only.
"""

    try:

        evaluation = call_ollama(
            prompt,
            timeout=180
        )

        ai_results = evaluation.get("results", [])

        if not isinstance(ai_results, list):
            raise ValueError("Invalid AI results format.")

        # Match AI results with original question indexes
        for position, original_index in enumerate(original_indexes):

            if position >= len(ai_results):
                continue

            item = ai_results[position]

            if not isinstance(item, dict):
                continue

            results[original_index] = format_evaluation(item)

        return results

    except Exception as error:

        print("BATCH INTERVIEW AI ERROR:", error)

        for original_index in original_indexes:

            results[original_index] = default_result(
                str(error)
            )

        return results
