from storage_service import StorageService
import os
import requests

class LLMService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.storage = StorageService()

    def ask(self, prompt, user_context=None):
        if not self.api_key:
            return "Ошибка: API ключ OpenRouter не найден."

        # Получаем знания из JSON через сервис
        knowledge = self.storage.get_knowledge_summary()
        system_content = "Ты - AI помощник PROFftech. Используй эти знания при ответе:\n" + knowledge
        
        if user_context:
            system_content += f"\n\nКонтекст пользователя: {user_context}"

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
