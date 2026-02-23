# 🧠 Psychology 2e RAG System  
### Retrieval-Augmented Generation with Verifiable References

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

## 🏗️ System Architecture

```mermaid
flowchart TD

A[Psychology2e_WEB.pdf] --> B[PDF Extraction]
B --> C[Section Detection]
C --> D[Chunking Engine]
D --> E[Embedding Model<br>all-MiniLM-L6-v2]
E --> F[FAISS Vector Index]

Q[User Question] --> G[Embedding]
G --> F
F --> H[Top-K Retrieval]

H --> I[Context Builder]
I --> J[Prompt Builder]

J --> K[NVIDIA LLM<br>Llama 3 70B]
K --> L[Grounded Answer]

L --> M[Answer + Sections + Pages]