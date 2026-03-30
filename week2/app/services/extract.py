from __future__ import annotations

import os
import re
from typing import List
import json
from typing import Any
from ollama import chat
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)


def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


def extract_action_items(text: str) -> List[str]:
    lines = text.splitlines()
    extracted: List[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: List[str] = []
    for item in extracted:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique


def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    return first.lower() in imperative_starters

# --- Tambahan untuk TODO 1: LLM Extraction ---

# 1. Definisikan struktur JSON yang kita inginkan
class ActionItemsSchema(BaseModel):
    action_items: List[str]

def extract_action_items_llm(text: str) -> List[str]:
    """
    Mengekstrak action items menggunakan Ollama secara lokal.
    Memanfaatkan fitur Structured Outputs agar hasilnya pasti berupa JSON.
    """
    if not text.strip():
        return []

    # 2. Prompt Engineering: Instruksi tegas untuk LLM
    system_prompt = """
    You are an expert system designed to extract actionable items, tasks, or to-dos from raw notes.
    Analyze the user's text and extract any clear actions.
    Return ONLY a JSON object matching the provided schema. Do not include any conversational filler, explanations, or markdown blocks.
    """

    try:
        # 3. Panggil Ollama
        # Pastikan kamu sudah menjalankan `ollama run llama3.2:1b` (atau model lain) di terminal
        response = chat(
            model='llama3.1:8b', # Ganti nama modelnya jika kamu menggunakan model lain
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': f"Extract action items from the following notes:\n\n{text}"}
            ],
            format=ActionItemsSchema.model_json_schema(), # Memaksa format menjadi JSON array of strings
            options={
                'temperature': 0.0 # Suhu 0 agar hasil ekstraksi konsisten dan logis
            }
        )

        # 4. Ambil teks jawaban dan ubah menjadi list Python
        llm_output = response['message']['content']
        parsed_data = json.loads(llm_output)
        
        return parsed_data.get("action_items", [])

    except Exception as e:
        print(f"Error pada integrasi Ollama: {e}")
        print("Fallback: Menggunakan ekstraksi heuristik/manual...")
        # Jika Ollama gagal (misal server mati), kita gunakan fungsi lama sebagai jaring pengaman
        return extract_action_items(text)