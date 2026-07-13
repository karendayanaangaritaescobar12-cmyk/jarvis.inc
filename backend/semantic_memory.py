import json
import os
import re
from collections import Counter
from typing import List, Dict, Optional


class SemanticMemory:
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.memory_file = os.path.join(self.data_dir, "semantic_memory.json")
        self.entries = self._load()

    def _load(self) -> list:
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return []

    def _save(self):
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(self.entries[-1000:], f, ensure_ascii=False, indent=1)

    def _tokenize(self, text: str) -> List[str]:
        stop_words = {"el", "la", "los", "las", "un", "una", "de", "del", "en", "que", "es", "se", "no",
                       "por", "con", "para", "como", "más", "pero", "su", "al", "lo", "este", "esta",
                       "hay", "fue", "ser", "son", "está", "están", "te", "tu", "yo", "me", "mi",
                       "qué", "cómo", "quién", "dónde", "cuándo", "cuánto", "cuál", "a", "e", "o", "u",
                       "y", "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
                       "have", "has", "had", "do", "does", "did", "will", "would", "could", "should",
                       "may", "might", "can", "shall", "to", "of", "in", "for", "on", "with", "at",
                       "by", "from", "as", "into", "about", "like", "through", "after", "over"}
        words = re.findall(r'\w+', text.lower())
        return [w for w in words if w not in stop_words and len(w) > 2]

    def _compute_similarity(self, query_tokens: List[str], entry_tokens: List[str]) -> float:
        if not query_tokens or not entry_tokens:
            return 0.0
        query_counter = Counter(query_tokens)
        entry_counter = Counter(entry_tokens)
        intersection = set(query_counter.keys()) & set(entry_counter.keys())
        if not intersection:
            return 0.0
        score = sum(query_counter[w] * entry_counter[w] for w in intersection)
        norm = (sum(v**2 for v in query_counter.values()) ** 0.5) * (sum(v**2 for v in entry_counter.values()) ** 0.5)
        return score / norm if norm > 0 else 0.0

    def add_entry(self, content: str, metadata: Dict = None):
        tokens = self._tokenize(content)
        self.entries.append({
            "content": content,
            "tokens": tokens,
            "metadata": metadata or {}
        })
        self._save()

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        query_tokens = self._tokenize(query)
        scored = []
        for entry in self.entries:
            sim = self._compute_similarity(query_tokens, entry.get("tokens", []))
            if sim > 0.05:
                scored.append((sim, entry))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [{"content": e["content"], "score": s, "metadata": e.get("metadata", {})}
                for s, e in scored[:limit]]

    def get_context_for_query(self, query: str) -> str:
        results = self.search(query, limit=3)
        if not results:
            return ""
        context = "Información relevante de conversaciones anteriores:\n"
        for r in results:
            context += f"- {r['content'][:300]}\n"
        return context

    def add_conversation_memory(self, user_msg: str, ai_response: str):
        important = len(user_msg) > 15 and any(w in user_msg.lower() for w in [
            "me llamo", "mi nombre", "soy", "prefiero", "me gusta", "odio",
            "siempre", "nunca", "importante", "recuerda", "anota", "guardo"
        ])
        if important:
            self.add_entry(f"Usuario: {user_msg[:200]}", {"type": "user_fact"})
        if len(ai_response) > 50:
            self.add_entry(f"JARVIS respondió: {ai_response[:200]}", {"type": "ai_response"})


semantic_memory = SemanticMemory()
