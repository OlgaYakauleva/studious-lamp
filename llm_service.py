import requests
import os

class LLMService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.kb_path = "knowledge_base.txt"

    def _get_knowledge(self):
        """Читает базу знаний из файла"""
        try:
            if os.path.exists(self.kb_path):
                with open(self.kb_path, 'r', encoding='utf-8') as f:
                    return f.read()
            return ""
        except Exception:
            return ""

    def ask(self, prompt):
        if not self.api_key:
            return "Ошибка: API ключ OpenRouter не найден."

        knowledge = self._get_knowledge()
        system_content = "Ты - AI помощник PROFftech. Используй следующие знания при ответе, если они уместны:\n" + knowledge
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "google/gemini-2.0-flash-001",
            "messages": [
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt}
            ]
        }

        try:
            response = requests.post(self.url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            return f"Ошибка при обращении к LLM: {e}"
