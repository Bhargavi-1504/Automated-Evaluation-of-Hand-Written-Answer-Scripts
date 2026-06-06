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
## ⚙️ System Architecture & Tech Stack

### 🗺️ System Workflow Diagram

<img width="1450" height="1719" alt="image" src="https://github.com/user-attachments/assets/bc0ca553-ff16-4d1b-acac-efa555d126ae" />

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

* **Windows:** start.bat
* **Mac / Linux:** ./start.sh

### 4. Open in Browser

Once the application is running, open your preferred web browser and navigate to the following local address:

**[http://localhost:5000](http://localhost:5000)**

## 📥 OCR Module (How It Works)

1. Teacher uploads student PDF (10–15 pages)
2. Entire PDF sent to Gemini API (base64 encoded)
3. AI extracts:
   * Q1.a – Q1.e
   * Q2 – Q5 answers
4. Handles split answers across pages
5. Reorders answers by question number
6. Teacher reviews extracted content

---

## 🧪 Evaluation Strategy (Core System)

The final score is calculated using a 3-method hybrid model:

| Evaluation Module | Weight | Core Focus |
| :--- | :---: | :--- |
| **🤖 1. LLM Semantic Evaluation** | **50%** | Evaluates conceptual correctness; focuses on overall meaning rather than rigid wording. |
| **📊 2. Embedding Similarity** | **30%** | Converts answers into dense vectors to measure conceptual closeness via cosine similarity. |
| **🔑 3. Keyword Matching** | **20%** | Ensures vital technical terms are present; prevents irrelevant answers from scoring high. |

### 📌 Final Score Formula

The grading framework uses a weighted linear combination of all three modules:

$$Final\ Score = (LLM \times 0.5) + (Embedding \times 0.3) + (Keyword \times 0.2)$$

---

## 📊 Results & Impact

* ⚡ **Faster Evaluation:** Accelerates the traditional time-consuming grading cycle.
* 🎯 **Consistent Scoring:** Eliminates evaluator bias and ensures standardized marking across all students.
* 📉 **Reduced Workload:** Drives a massive reduction in manual institutional workloads.
* 🧠 **Subjective Understanding:** Highly effective at accurately parsing descriptive and subjective answers.
* 📦 **Scalability:** Built to scale seamlessly for large academic institutions.

---

## 🚀 Future Enhancements

* 📱 **Mobile Scanning App:** Native mobile scanning integration for capturing physical answer sheets.
* 🧾 **LMS Integration:** Seamless connection with popular Learning Management Systems (Moodle, Canvas, Blackboard).
* 📊 **Large-Scale Testing:** Deployment testing to mimic high-volume, university-wide examination loads.
* 🧠 **Explainable AI Scoring:** A transparent feedback generation system that explains point allocations to students.
* 🌐 **Multimodal Evaluation:** Expanding the engine to simultaneously evaluate text, handwriting, and technical diagrams.

---

## 🏁 Conclusion

This system transforms traditional manual grading into an AI-powered intelligent evaluation pipeline. By dynamically combining **OCR extraction, LLM reasoning, semantic similarity, and keyword validation**, it delivers a faster, fairer, and highly transparent academic assessment tool.

It combines:

1. **OCR extraction**
2. **LLM reasoning**
3. **Semantic similarity**
4. **Keyword validation**

for a **faster, fair, and transparent** assessment.
