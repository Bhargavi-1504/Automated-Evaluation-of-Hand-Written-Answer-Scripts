from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import json
import re
import os
import base64
import time
from datetime import datetime
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'answereval2026')

# Configure Gemini
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Load sentence transformer model
try:
    similarity_model = SentenceTransformer('all-MiniLM-L6-v2')
    logger.info("Sentence transformer loaded successfully")
except Exception as e:
    similarity_model = None
    logger.warning(f"Could not load sentence transformer: {e}")

# In-memory storage
exam_configs = {}
evaluations = {}

# Rate limiting — 5 requests per minute = 1 every 12 seconds
last_request_time = 0
MIN_REQUEST_INTERVAL = 12


def wait_for_rate_limit():
    global last_request_time
    now = time.time()
    elapsed = now - last_request_time
    if elapsed < MIN_REQUEST_INTERVAL:
        wait = MIN_REQUEST_INTERVAL - elapsed
        logger.info(f"Rate limit: waiting {wait:.1f}s before next API call")
        time.sleep(wait)
    last_request_time = time.time()


# ─────────────────────────────────────────────
# OCR — EXTRACT ALL ANSWERS FROM ENTIRE PDF
# ─────────────────────────────────────────────
def extract_answers_from_pdf(pdf_bytes, exam_config):
    wait_for_rate_limit()

    # Build split info string for prompt
    split_lines = ""
    for q in ["2", "3", "4", "5"]:
        q_key = f"q{q}"
        is_split = exam_config.get(q_key, {}).get('is_split', False)
        if is_split:
            split_lines += f"  - Question {q} has TWO parts: {q}a and {q}b\n"
        else:
            split_lines += f"  - Question {q} is a single question (no parts)\n"

    prompt = f"""You are reading a handwritten student exam answer booklet (PDF).

EXAM STRUCTURE:
- Question 1: MANDATORY — has 5 sub-questions: 1a, 1b, 1c, 1d, 1e
- Questions 2 to 5: Student attempts ANY 3 out of these 4
- Question formats:
{split_lines}

YOUR TASK:
1. Read ALL pages carefully from start to end
2. Find answers for every question and sub-question — they can be on ANY page in ANY order
3. If an answer is split across multiple pages, combine the full text
4. For Q2–Q5, detect which 3 questions the student attempted
5. Extract handwritten text exactly as written

Return ONLY a valid JSON object — no markdown, no explanation:
{{
  "q1": {{
    "1a": "extracted answer or empty string",
    "1b": "extracted answer or empty string",
    "1c": "extracted answer or empty string",
    "1d": "extracted answer or empty string",
    "1e": "extracted answer or empty string"
  }},
  "attempted_questions": ["2", "3", "5"],
  "q2": "answer if attempted and single question, else empty string",
  "q2a": "answer if attempted and split, else empty string",
  "q2b": "answer if attempted and split, else empty string",
  "q3": "answer if attempted and single question, else empty string",
  "q3a": "answer if attempted and split, else empty string",
  "q3b": "answer if attempted and split, else empty string",
  "q4": "answer if attempted and single question, else empty string",
  "q4a": "answer if attempted and split, else empty string",
  "q4b": "answer if attempted and split, else empty string",
  "q5": "answer if attempted and single question, else empty string",
  "q5a": "answer if attempted and split, else empty string",
  "q5b": "answer if attempted and split, else empty string"
}}"""

    try:
        model = genai.GenerativeModel('gemini-3-flash-preview')
        pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')

        response = model.generate_content([
            {"inline_data": {"mime_type": "application/pdf", "data": pdf_b64}},
            prompt
        ])

        raw = response.text.strip()
        # Clean markdown fences if present
        raw = re.sub(r'^```json\s*', '', raw, flags=re.MULTILINE)
        raw = re.sub(r'^```\s*', '', raw, flags=re.MULTILINE)
        raw = re.sub(r'\s*```$', '', raw, flags=re.MULTILINE)
        raw = raw.strip()

        extracted = json.loads(raw)
        logger.info(f"Extraction success. Attempted: {extracted.get('attempted_questions', [])}")
        return extracted, None

    except json.JSONDecodeError as e:
        logger.error(f"JSON parse failed: {e}")
        return None, "Could not read answer booklet properly. Please try again."
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        return None, str(e)


# ─────────────────────────────────────────────
# EVALUATE — SCORE ONE ANSWER
# ─────────────────────────────────────────────
def evaluate_single_answer(student_answer, question_text, reference_answer, keywords, max_marks):
    """
    Multi-method scoring:
    LLM (50%) - evaluates if student answered THE QUESTION correctly
    Semantic Similarity (30%) - compares student answer vs reference answer
    Keywords (20%) - checks if keywords present in student answer
    """
    if not student_answer or not student_answer.strip():
        return {
            "llm_score": 0, "similarity_score": 0, "keyword_score": 0,
            "final_marks": 0, "feedback": "No answer provided.", "max_marks": max_marks
        }

    scores = {}

    # Method 1: Semantic Similarity (30%) - student vs reference
    try:
        if similarity_model and reference_answer:
            emb = similarity_model.encode([student_answer, reference_answer])
            sim = float(cosine_similarity([emb[0]], [emb[1]])[0][0])
            sim = max(0.0, min(1.0, sim))
            scores['similarity'] = round(sim * max_marks, 2)
        else:
            scores['similarity'] = round(max_marks * 0.5, 2)
    except Exception as e:
        logger.warning(f"Similarity error: {e}")
        scores['similarity'] = round(max_marks * 0.5, 2)

    # Method 2: Keyword Matching (20%) - keywords in student answer
    try:
        if keywords:
            student_lower = student_answer.lower()
            found = sum(1 for kw in keywords if kw.strip().lower() in student_lower)
            scores['keyword'] = round((found / len(keywords)) * max_marks, 2)
        else:
            scores['keyword'] = round(max_marks * 0.5, 2)
    except Exception as e:
        logger.warning(f"Keyword error: {e}")
        scores['keyword'] = round(max_marks * 0.5, 2)

    # Method 3: LLM Evaluation (50%) - evaluates answer against THE QUESTION
    try:
        wait_for_rate_limit()
        model = genai.GenerativeModel('gemini-3-flash-preview')

        prompt = f"""You are an experienced teacher evaluating a student's answer.

Question Asked:
{question_text}

Maximum Marks: {max_marks}

Student's Answer:
{student_answer}

Evaluate how well the student answered THE QUESTION based on:
1. Correctness - Is the answer factually accurate?
2. Completeness - Did they cover the key points asked in the question?
3. Clarity - Is the explanation clear and well-structured?

Do NOT compare with any reference answer - judge the answer on its own merit based on the question asked.

Return ONLY valid JSON:
{{"score": <number 0 to {max_marks}>, "feedback": "<2-3 sentence constructive feedback>"}}"""

        response = model.generate_content(prompt)
        raw = response.text.strip()
        raw = re.sub(r'^```json\s*', '', raw, flags=re.MULTILINE)
        raw = re.sub(r'^```\s*', '', raw, flags=re.MULTILINE)
        raw = re.sub(r'\s*```$', '', raw, flags=re.MULTILINE)
        raw = raw.strip()

        llm_data = json.loads(raw)
        llm_score = float(llm_data.get('score', 0))
        llm_score = max(0, min(max_marks, llm_score))
        scores['llm'] = round(llm_score, 2)
        scores['feedback'] = llm_data.get('feedback', 'Evaluation complete.')

    except Exception as e:
        logger.warning(f"LLM eval error: {e}")
        fallback = round((scores.get('similarity', 0) + scores.get('keyword', 0)) / 2, 2)
        scores['llm'] = fallback
        scores['feedback'] = "Evaluated based on content similarity and keyword coverage."

    # Weighted final score
    final = round(
        scores['llm'] * 0.50 +
        scores['similarity'] * 0.30 +
        scores['keyword'] * 0.20,
        2
    )
    final = max(0, min(max_marks, final))

    return {
        "llm_score": scores['llm'],
        "similarity_score": scores['similarity'],
        "keyword_score": scores['keyword'],
        "final_marks": final,
        "feedback": scores.get('feedback', ''),
        "max_marks": max_marks
    }


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create-exam')
def create_exam_page():
    return render_template('create_exam.html')

@app.route('/evaluate')
def evaluate_page():
    return render_template('evaluate.html')


@app.route('/api/save-exam', methods=['POST'])
def save_exam():
    try:
        data = request.json
        exam_name = data.get('exam_name', '').strip()
        if not exam_name:
            return jsonify({'success': False, 'error': 'Exam name is required'}), 400

        # Validate Q1
        q1 = data.get('q1', {})
        for sub in ['1a', '1b', '1c', '1d', '1e']:
            if not q1.get(sub, {}).get('question_text', '').strip():
                return jsonify({'success': False, 'error': f'Question text for Q1.{sub[-1].upper()} is required'}), 400
            if not q1.get(sub, {}).get('reference_answer', '').strip():
                return jsonify({'success': False, 'error': f'Reference answer for Q1.{sub[-1].upper()} is required'}), 400

        exam_id = f"exam_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        exam_configs[exam_id] = {
            'exam_id': exam_id,
            'exam_name': exam_name,
            'created_at': datetime.now().isoformat(),
            'q1': q1,
            'q2': data.get('q2', {}),
            'q3': data.get('q3', {}),
            'q4': data.get('q4', {}),
            'q5': data.get('q5', {})
        }

        logger.info(f"Saved exam config: {exam_id}")
        return jsonify({'success': True, 'exam_id': exam_id, 'exam_name': exam_name})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/get-exams', methods=['GET'])
def get_exams():
    exams = [
        {'exam_id': v['exam_id'], 'exam_name': v['exam_name'], 'created_at': v['created_at']}
        for v in exam_configs.values()
    ]
    return jsonify({'success': True, 'exams': exams})


@app.route('/api/extract', methods=['POST'])
def extract():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400

        file = request.files['file']
        exam_id = request.form.get('exam_id', '')

        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'success': False, 'error': 'Only PDF files are supported'}), 400

        if exam_id not in exam_configs:
            return jsonify({'success': False, 'error': 'Exam configuration not found'}), 404

        pdf_bytes = file.read()
        exam_config = exam_configs[exam_id]

        extracted, error = extract_answers_from_pdf(pdf_bytes, exam_config)
        if error:
            return jsonify({'success': False, 'error': error}), 500

        return jsonify({'success': True, 'extracted': extracted})

    except Exception as e:
        logger.error(f"Extract route error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/evaluate', methods=['POST'])
def run_evaluation():
    try:
        data = request.json
        exam_id = data.get('exam_id')
        extracted = data.get('extracted_answers', {})

        if exam_id not in exam_configs:
            return jsonify({'success': False, 'error': 'Exam not found'}), 404

        exam_config = exam_configs[exam_id]
        results = {'q1': {}, 'q2_to_q5': {}}
        q1_total = 0
        q2_to_q5_total = 0

        # Evaluate Q1
        for sub in ['1a', '1b', '1c', '1d', '1e']:
            student_ans = extracted.get('q1', {}).get(sub, '')
            ref = exam_config['q1'].get(sub, {})
            res = evaluate_single_answer(
                student_ans,
                ref.get('question_text', ''),
                ref.get('reference_answer', ''),
                ref.get('keywords', []),
                1
            )
            results['q1'][sub] = res
            q1_total += res['final_marks']

        # Evaluate Q2–Q5
        attempted = extracted.get('attempted_questions', [])
        results['attempted'] = attempted

        for q in ['2', '3', '4', '5']:
            q_key = f"q{q}"
            q_config = exam_config.get(q_key, {})
            is_split = q_config.get('is_split', False)

            if q not in attempted:
                results['q2_to_q5'][q] = {'attempted': False}
                continue

            if is_split:
                res_a = evaluate_single_answer(
                    extracted.get(f'q{q}a', ''),
                    q_config.get('part_a', {}).get('question_text', ''),
                    q_config.get('part_a', {}).get('reference_answer', ''),
                    q_config.get('part_a', {}).get('keywords', []),
                    2.5
                )
                res_b = evaluate_single_answer(
                    extracted.get(f'q{q}b', ''),
                    q_config.get('part_b', {}).get('question_text', ''),
                    q_config.get('part_b', {}).get('reference_answer', ''),
                    q_config.get('part_b', {}).get('keywords', []),
                    2.5
                )
                total = round(res_a['final_marks'] + res_b['final_marks'], 2)
                q2_to_q5_total += total
                results['q2_to_q5'][q] = {
                    'attempted': True, 'is_split': True,
                    'part_a': res_a, 'part_b': res_b, 'total': total
                }
            else:
                res = evaluate_single_answer(
                    extracted.get(f'q{q}', ''),
                    q_config.get('question_text', ''),
                    q_config.get('reference_answer', ''),
                    q_config.get('keywords', []),
                    5
                )
                q2_to_q5_total += res['final_marks']
                results['q2_to_q5'][q] = {
                    'attempted': True, 'is_split': False,
                    'result': res, 'total': res['final_marks']
                }

        grand_total = round(q1_total + q2_to_q5_total, 2)
        results['summary'] = {
            'q1_total': round(q1_total, 2),
            'q2_to_q5_total': round(q2_to_q5_total, 2),
            'grand_total': grand_total,
            'out_of': 20,
            'percentage': round((grand_total / 20) * 100, 2)
        }

        eval_id = f"eval_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        evaluations[eval_id] = {'eval_id': eval_id, 'exam_id': exam_id, 'results': results}

        return jsonify({'success': True, 'eval_id': eval_id, 'results': results})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
