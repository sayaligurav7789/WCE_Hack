# 🤖 Psychology 2e RAG System  
### Retrieval-Augmented Generation with Verifiable References

---
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![NVIDIA Llama 3](https://img.shields.io/badge/NVIDIA-Llama%203%2070B-green.svg)](https://build.nvidia.com/)
[![FAISS](https://img.shields.io/badge/FAISS-Vector%20Search-orange.svg)](https://github.com/facebookresearch/faiss)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

A **Retrieval-Augmented Generation (RAG)** system that answers questions from the **OpenStax Psychology 2e** textbook with **verifiable page-level citations**. Built for the hackathon challenge: *"Build a RAG system that returns verifiable references (sections AND page numbers)"*.

 ---
 ## 🎯 **Problem Statement**

Students and learners often struggle to quickly find accurate answers from large textbooks like OpenStax Psychology 2e. Searching manually through hundreds of pages is time-consuming and inefficient.

**The goal:** Build a RAG system that:
- Retrieves relevant context from the textbook
- Generates accurate answers grounded in retrieved content
- Provides exact references to sections and page numbers
- Ensures responses are reliable and verifiable

  ---
  ### ❌ **How Current Solutions Fall Back**
| Solution | Limitation |
|----------|------------|
| ChatGPT/LLMs | Lack verifiable sources |
| Google Search | Unverified, overwhelming results |
| Manual Searching | Time-consuming and inefficient |
| Traditional Methods | No way to confirm information origin |

---

## ✨ **Features**

### Core Features
- **Section-aware PDF ingestion** - Extracts and indexes complete OpenStax Psychology 2e textbook with section & page metadata
- **Semantic retrieval** - Performs Top‑K retrieval using FAISS vector similarity
- **Validated evidence context** - Builds context from retrieved chunks only
- **Grounded generation** - Generates answers strictly grounded in textbook content using NVIDIA Llama 3
- **Exact citations** - Returns exact section identifiers & page numbers tied to used evidence
- **Safe fallback** - Outputs "Not found in the provided textbook." when no supporting context exists
- **Auditable output** - Produces fully auditable, citation‑backed responses in `submission.csv`

---

### 🏆 **Key Statistics**
- **Textbook Pages:** 753
- **Chunks Created:** 1076
- **Chunk Size:** 400 words
- **Grounded Accuracy:** 100%
- **Avg Retrieval Time:** 0.3 sec
- **Avg Generation Time:** 2.1 sec
- **Total Response Time:** < 3 sec
- **Fallback Rate:** 0%

---

## 📌 Overview

This project implements a **Retrieval-Augmented Generation (RAG) system** over the *OpenStax Psychology 2e* textbook.

The system:
- Extracts and chunks textbook content
- Builds a FAISS vector index
- Retrieves relevant sections for a question
- Generates grounded answers using NVIDIA LLM API
- Returns **verifiable references (sections + page numbers)**
- Produces a `submission.csv` for evaluation
- Provides an interactive frontend demo

---

![WhatsApp Image 2026-02-24 at 9 34 53 AM](https://github.com/user-attachments/assets/33a27fa9-1614-4633-809e-0714f8bdec50)

---

## 🛠️ **Tech Stack**

| Layer | Technology | Purpose |
|:------|:-----------|:--------|
| **PDF Processing** | ![PyMuPDF](https://img.shields.io/badge/PyMuPDF-fitz-blue?logo=python&style=for-the-badge) | Extract text with page numbers |
| **Web Framework** | ![Flask](https://img.shields.io/badge/Flask-Web%20Framework-black?logo=flask&style=for-the-badge) | API routing & templating |
| **Embeddings** | ![Sentence-Transformers](https://img.shields.io/badge/Sentence--Transformers-all--MiniLM--L6--v2-green?logo=huggingface&style=for-the-badge) | 384-dim embeddings |
| **Vector Search** | ![FAISS](https://img.shields.io/badge/FAISS-CPU-orange?logo=facebook&style=for-the-badge) | Fast similarity search |
| **Keyword Search** | ![BM25](https://img.shields.io/badge/BM25-rank--bm25-yellow?logo=python&style=for-the-badge) | Hybrid retrieval complement |
| **LLM** | ![NVIDIA](https://img.shields.io/badge/NVIDIA-Llama%203%2070B-green?logo=nvidia&style=for-the-badge) | Answer generation (free tier) |
| **Data Processing** | ![Pandas](https://img.shields.io/badge/Pandas-Data%20Processing-blue?logo=pandas&style=for-the-badge) | CSV & JSON handling |
| **Numerical Ops** | ![NumPy](https://img.shields.io/badge/NumPy-Numerical%20Ops-blue?logo=numpy&style=for-the-badge) | Array operations |
| **Tokenization** | ![NLTK](https://img.shields.io/badge/NLTK-Text%20Tokenization-green?logo=python&style=for-the-badge) | BM25 preprocessing |
| **Frontend** | ![HTML5](https://img.shields.io/badge/HTML5-CSS3-blue?logo=html5&style=for-the-badge) ![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow?logo=javascript&style=for-the-badge) | Interactive dashboard |
| **Templating** | ![Jinja2](https://img.shields.io/badge/Jinja2-Templates-red?logo=jinja&style=for-the-badge) | Flask template rendering |

---
```
📦 WCE_Hack
├── 📂 src
│   ├── 📄 rag_pipeline.py
│   ├── 📄 build_index.py
│   ├── 📄 submission.py
│   ├── 📄 generate_viz.py
│   ├── 📄 app.py
│   ├── 📄 evaluate.py
│   └── 📄 llm_test.py
│
├── 📂 data
│   ├── 📄 Psychology2e_WEB.pdf
│   └── 📄 queries.json
│
├── 📂 models
│   ├── 📄 faiss_index.bin
│   └── 📄 chunks.json
│
├── 📂 output
│   ├── 📄 submission.csv
│   ├── 📄 submission.json
│   ├── 📄 bar_chart.png
│   ├── 📄 pie_chart.png
│   └── 📂 EvidenceVisualization
│       ├── 📄 viz_1.html
│       ├── 📄 viz_2.html
│       ├── 📄 viz_3.html
│       ├── 📄 ...
│       └── 📄 viz_50.html
│
├── 📂 frontend
│   ├── 📄 index.html
│   ├── 📂 css
│   │   └── 📄 style.css
│   └── 📂 js
│       └── 📄 chat.js
│
├── 📄 requirements.txt
├── 📄 .env
├── 📄 .gitignore
└── 📄 README.md
```

---

### 📂 **Directory Details**

| Folder | Description |
|--------|-------------|
| **src/** | Source code for the RAG pipeline and utilities |
| **data/** | Textbook PDF and query questions |
| **models/** | Saved FAISS index and processed chunks |
| **output/** | Generated results and visualizations |
| **frontend/** | Web interface files (HTML, CSS, JS) |

### 📄 **Key Files**

| File | Description |
|------|-------------|
| `rag_pipeline.py` | Core RAG implementation with retrieval and generation |
| `build_index.py` | Creates FAISS index from textbook PDF |
| `submission.py` | Generates answers for all 50 queries |
| `generate_viz.py` | Creates 50+ HTML visualization files |
| `app.py` | Flask web application for interactive demo |
| `submission.csv` | Final output with answers and citations |
| `viz_*.html` | Interactive evidence visualizations (one per question) |

---

## 📤 Output
1. submission.csv
```
ID	context	answer	references
1	"..."	"The scientific method..."	{"sections": ["1.1"], "pages": [5]}
2	"..."	"A neuron consists of..."	{"sections": ["2.3"], "pages": [45]}
3	"..."	"The stages of sleep are..."	{"sections": ["4.3"], "pages": [156,157,160]}
```
## 🖼️ Snapshots
###  Chat Interface - Successful Answer with Citations
<img width="1770" height="827" alt="image" src="https://github.com/user-attachments/assets/c5dfc3fb-6354-4556-b46d-603caa2f8948" />

---
###  "Not Found" Fallback Response
<img width="1919" height="906" alt="image" src="https://github.com/user-attachments/assets/46594e40-5a86-4835-bd74-d74117acd8c8" />

---
###  New Chat, Delete chat
<img width="1919" height="907" alt="image" src="https://github.com/user-attachments/assets/d5b5b0c0-9d81-4626-bb85-2fe055035ce7" />

---
### Evidence by Section Cards
<img width="1919" height="910" alt="image" src="https://github.com/user-attachments/assets/7d4cc03b-a974-45a0-a0f0-a91cf353f48e" />


