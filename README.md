🧠 Automated Evaluation of Handwritten Answer Scripts

Using OCR and Large Language Models (LLMs)

⚙️ Setup Instructions
1. Install dependencies
pip install -r requirements.txt
2. Create .env file
GEMINI_API_KEY=your_actual_api_key_here
SECRET_KEY=any_random_string
3. Run the project

Windows

start.bat

Mac / Linux

./start.sh
4. Open in browser
http://localhost:5000
📝 Exam Structure
Q1 (Compulsory)
Sub-questions: 1.a – 1.e
Marks: 1 mark each → 5 marks
Q2 – Q5 (Choice based)
Attempt any 3 out of 4 questions
Each question: 5 marks → 15 marks total
📌 Question Pattern
Questions can be:
Single question (5 marks)
OR Split format (a + b = 2.5 marks each)
🧪 Evaluation Strategy

The final score is computed using a hybrid evaluation model:

🤖 LLM-based evaluation → 50%
📊 Semantic similarity scoring → 30%
🔑 Keyword matching → 20%
🚀 Project Goal

This system automates evaluation of handwritten answer sheets using OCR + LLMs, ensuring:

Faster evaluation
Reduced human bias
Consistent scoring
