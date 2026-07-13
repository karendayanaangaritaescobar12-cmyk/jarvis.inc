import json
import os
import datetime
from typing import List, Dict, Optional


class ChatStore:
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.history_file = os.path.join(self.data_dir, "chat_history.json")
        self.summary_file = os.path.join(self.data_dir, "summaries.json")
        self.history = self._load()
        self.summaries = self._load_summaries()

    def _load(self) -> list:
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return []

    def _save(self):
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(self.history[-500:], f, ensure_ascii=False, indent=1)

    def _load_summaries(self) -> list:
        if os.path.exists(self.summary_file):
            try:
                with open(self.summary_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return []

    def _save_summaries(self):
        with open(self.summary_file, "w", encoding="utf-8") as f:
            json.dump(self.summaries[-50:], f, ensure_ascii=False, indent=1)

    def add_message(self, role: str, content: str):
        self.history.append({
            "role": role,
            "content": content,
            "time": datetime.datetime.now().isoformat()
        })
        self._save()

    def get_context(self, limit: int = 50) -> List[Dict]:
        msgs = self.history[-limit:]
        return [{"role": m["role"], "content": m["content"]} for m in msgs]

    def get_all(self) -> List[Dict]:
        return self.history

    def add_summary(self, summary: str, msg_range: str):
        self.summaries.append({
            "summary": summary,
            "range": msg_range,
            "time": datetime.datetime.now().isoformat()
        })
        self._save_summaries()

    def get_summaries(self) -> List[Dict]:
        return self.summaries

    def get_recent_without_summary(self, count: int = 50) -> List[Dict]:
        if not self.summaries:
            return self.get_context(count)
        last_summary = self.summaries[-1]
        last_time = last_summary.get("time", "")
        recent = [m for m in self.history if m.get("time", "") > last_time]
        return [{"role": m["role"], "content": m["content"]} for m in recent[-count:]]

    def clear(self):
        self.history.clear()
        self._save()

    def search(self, query: str, limit: int = 10) -> List[Dict]:
        query_lower = query.lower()
        results = []
        for m in reversed(self.history):
            if query_lower in m.get("content", "").lower():
                results.append(m)
                if len(results) >= limit:
                    break
        return list(reversed(results))

    def get_stats(self) -> Dict:
        user_msgs = sum(1 for m in self.history if m["role"] == "user")
        ai_msgs = sum(1 for m in self.history if m["role"] == "assistant")
        return {
            "total": len(self.history),
            "user_messages": user_msgs,
            "ai_messages": ai_msgs,
            "summaries": len(self.summaries)
        }


chat_store = ChatStore()
