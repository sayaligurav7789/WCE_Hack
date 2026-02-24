import os
import json
import re
import fitz
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

PDF_PATH = "data/Psychology2e_WEB.pdf"
MODEL_NAME = "all-MiniLM-L6-v2"
MODEL_DIR = "models"

os.makedirs(MODEL_DIR, exist_ok=True)

model = SentenceTransformer(MODEL_NAME)


def extract_pdf_text(pdf_path):
    doc = fitz.open(pdf_path)
    pages = []

    for page_num in range(len(doc)):
        text = doc[page_num].get_text()
        pages.append({
            "page_number": page_num + 1,
            "text": text
        })

    return pages


def split_into_sections(pages):
    section_data = []
    current_section = "unknown"

    for page in pages:
        text = page["text"]
        if not text.strip():
            continue

        matches = re.findall(r"\b\d+\.\d+\s+[A-Z][A-Za-z\s\-:]*", text)
        if matches:
            current_section = matches[0].strip()

        section_data.append({
            "section": current_section,
            "page_number": page["page_number"],
            "text": text
        })

    return section_data


def chunk_text(section_chunks, chunk_size=400):
    final_chunks = []
    chunk_id = 0

    for item in section_chunks:
        text = item["text"]

        if any(x in text.lower() for x in [
            "review questions",
            "critical thinking questions",
            "personal application questions",
            "contents",
            "key terms"
        ]):
            continue

        words = text.split()

        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i+chunk_size])

            if len(chunk.strip()) < 200:
                continue

            final_chunks.append({
                "chunk_id": chunk_id,
                "text": chunk,
                "section": item["section"],
                "page_number": item["page_number"]
            })
            chunk_id += 1

    return final_chunks


def build_index(chunks):
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)
    embeddings = np.array(embeddings).astype("float32")

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    faiss.write_index(index, os.path.join(MODEL_DIR, "faiss_index.bin"))

    with open(os.path.join(MODEL_DIR, "chunks.json"), "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print("Index and chunks saved successfully!")


if __name__ == "__main__":
    print("Extracting PDF...")
    pages = extract_pdf_text(PDF_PATH)

    print("Splitting into sections...")
    section_pages = split_into_sections(pages)

    print("Chunking text...")
    chunks = chunk_text(section_pages)

    print("Building FAISS index...")
    build_index(chunks)