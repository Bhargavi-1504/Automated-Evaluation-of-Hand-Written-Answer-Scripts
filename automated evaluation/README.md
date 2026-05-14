# Automated Evaluation of Handwritten Answer Scripts
## Using OCR and Large Language Models

## Setup

### 1. Install dependencies
pip install -r requirements.txt

### 2. Create .env file
GEMINI_API_KEY=your_actual_api_key_here
SECRET_KEY=any_random_string

### 3. Run
Windows:  start.bat
Mac/Linux: ./start.sh

### 4. Open browser
http://localhost:5000

## Exam Structure
- Q1: Mandatory, sub-questions 1.a–1.e, 1 mark each = 5 marks
- Q2–Q5: Attempt any 3 of 4, 5 marks each = 15 marks
- Total: 20 marks
- Q2–Q5 can be Single (5 marks) or Split a+b (2.5 each)

## Evaluation
LLM (50%) + Semantic Similarity (30%) + Keywords (20%)
