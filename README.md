# 🧠 Automated Evaluation of Handwritten Answer Scripts  
## Using Hybrid Model

---

# 🏫 Project Overview

This project automates the evaluation of handwritten answer scripts using **OCR + LLM-based semantic understanding**.

Unlike traditional systems that rely only on keyword matching, this system evaluates answers based on **meaning, context, and similarity**, making grading more accurate, fair, and scalable.

---

# 🚨 Problem Statement

Manual evaluation faces major challenges:

- ⏱ Time-consuming grading process  
- ❌ Inconsistent marks between evaluators  
- 🔑 Keyword-based systems fail for descriptive answers  
- 🧠 Cannot understand subjective answers  
- 📦 Difficult storage and re-evaluation of scripts  

👉 **Need:**  
An intelligent system that evaluates based on meaning, not just keywords

---

# 🎯 Project Objectives

- 🧠 Semantic evaluation using LLMs  
- ⚖ Hybrid multi-method scoring system  
- ⏱ Reduce evaluation time by up to 95%  
- 📄 Process full answer sheet using single OCR request  
- 🎯 Achieve 85%+ correlation with human grading  

---

# ⚙️ System Architecture

---

## 🧰 Tech Stack

- **Frontend:** Flask + Bootstrap 5  
- **OCR Engine:** Gemini-3-flash-preview API  
- **NLP:** Sentence Transformers  
- **Evaluation Engine:** Hybrid scoring pipeline  

---

## 🔄 Key Features

- 📄 Full PDF processed in single API call (base64 input)  
- ⚡ Rate-limited API usage (5 requests/min)  
- 🔄 Smart extraction of Q1–Q5 structure  
- 📑 Automatic reordering of answers  
- ✏ Teacher review before evaluation  

---

# 📥 Setup Instructions

### 1. Install dependencies  
```bash
pip install -r requirements.txt
```

### 2. Create `.env` file
```env
GEMINI_API_KEY=your_actual_api_key_here
SECRET_KEY=any_random_string
```

### 3. Run the Project
Execute the appropriate startup script for your operating system:

* **Windows:** ```bash
  start.bat
  ```
* **Mac / Linux:** ```bash
./start.sh
```

### 4. Open in Browser

Once the application is running, open your preferred web browser and navigate to the following local address:

**[http://localhost:5000](http://localhost:5000)**

📥 **OCR Module (How It Works)**

1. Teacher uploads student PDF (10–15 pages)
2. Entire PDF sent to Gemini API (base64 encoded)
3. AI extracts:
   Q1.a – Q1.e
   Q2–Q5 answers
4. Handles split answers across pages
5. Reorders answers by question number
6. Teacher reviews extracted content
   
🧪 **Evaluation Strategy (Core System)**

Final score is calculated using a 3-method hybrid model:

🤖 **1. LLM Semantic Evaluation (50%)**
Evaluates conceptual correctness
Focuses on meaning rather than wording

📊 **2. Embedding Similarity (30%)**
Converts answers into vectors
Uses cosine similarity
Measures conceptual closeness

🔑 **3. Keyword Matching (20%**)
Ensures important terms are present
Prevents irrelevant answers from scoring high

📌 **Final Score Formula**
Final Score = (LLM × 0.5) + (Embedding × 0.3) + (Keyword × 0.2)

📊 **Results & Impact**

⚡ Faster evaluation process
🎯 Consistent scoring across students
📉 Huge reduction in manual workload
🧠 Effective for subjective answers
📦 Scalable for large institutions

🚀 **Future Enhancements**

📱 Mobile scanning app for answer sheets
🧾 LMS integration
📊 Large-scale deployment testing
🧠 Explainable AI scoring system
🌐 Multimodal evaluation (text + handwriting + diagrams)

🏁 **Conclusion**

This system transforms traditional manual grading into an AI-powered intelligent evaluation system.

It combines:
1. OCR extraction
2. LLM reasoning
3. Semantic similarity
4. Keyword validation

for faster, fair, and transparent assessment.
