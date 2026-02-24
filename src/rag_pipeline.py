import os
import json
import faiss
import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from openai import OpenAI

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------
load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL")

if not NVIDIA_API_KEY:
    raise ValueError("NVIDIA_API_KEY not found in .env file")

if not NVIDIA_BASE_URL:
    raise ValueError("NVIDIA_BASE_URL not found in .env file")

# --------------------------------------------------
# Paths
# --------------------------------------------------
MODEL_DIR = "models"
FAISS_PATH = os.path.join(MODEL_DIR, "faiss_index.bin")
CHUNKS_PATH = os.path.join(MODEL_DIR, "chunks.json")

if not os.path.exists(FAISS_PATH):
    raise FileNotFoundError("faiss_index.bin not found. Run build_index.py first.")

if not os.path.exists(CHUNKS_PATH):
    raise FileNotFoundError("chunks.json not found. Run build_index.py first.")

# --------------------------------------------------
# Load embedding model
# --------------------------------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# --------------------------------------------------
# Load FAISS index and chunks
# --------------------------------------------------
index = faiss.read_index(FAISS_PATH)

with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
    chunks = json.load(f)

# --------------------------------------------------
# NVIDIA Client
# --------------------------------------------------
client = OpenAI(
    base_url=NVIDIA_BASE_URL,
    api_key=NVIDIA_API_KEY
)

# ==================================================
# RETRIEVAL
# ==================================================
def retrieve(query, k=12):
    query_embedding = model.encode([query])
    query_embedding = np.array(query_embedding).astype("float32")

    distances, indices = index.search(query_embedding, k)

    retrieved = []
    for idx in indices[0]:
        if idx < len(chunks):
            retrieved.append(chunks[idx])

    return retrieved


# ==================================================
# CONTEXT BUILDER
# ==================================================
def build_context(retrieved_chunks):
    context_parts = []
    sections = set()
    pages = set()

    for chunk in retrieved_chunks:
        context_parts.append(chunk["text"])
        sections.add(chunk["section"])
        pages.add(chunk["page_number"])

    context = "\n\n".join(context_parts)

    return context, sorted(list(sections)), sorted(list(pages))


# ==================================================
# PROMPT
# ==================================================
def build_prompt(question, context):
    return f"""
You are answering a psychology textbook question.

Use ONLY the provided textbook context.

You may combine information from multiple parts of the context to form the answer.
Summarize clearly using the textbook content.

Respond with:
Not found in the provided textbook.
ONLY if there is absolutely no relevant information in the context.

Context:
{context}

Question:
{question}

Answer:
"""


# ==================================================
# LLM GENERATION
# ==================================================
def generate_answer(prompt):
    response = client.chat.completions.create(
        model="meta/llama3-70b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=400
    )

    answer = response.choices[0].message.content.strip()

    if not answer:
        return "Not found in the provided textbook."

    return answer


# ==================================================
# FULL PIPELINE
# ==================================================
def answer_question(question):

    # Handle casual greetings
    casual_inputs = ["hi", "hello", "hey", "thanks", "thank you", "good morning", "good evening"]

    if question.strip().lower() in casual_inputs:
        return "Hello! 👋 Ask me any question from the Psychology textbook.", "", [], []

    # Logic 
    retrieved = retrieve(question)

    if not retrieved:
        return "Not found in the provided textbook.", "", [], []

    context, sections, pages = build_context(retrieved)

    if len(context) > 12000:
        context = context[:12000]

    prompt = build_prompt(question, context)
    answer = generate_answer(prompt)

    return answer, context, sections, pages