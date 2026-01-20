import json
import os

class StorageService:
    def __init__(self, file_path="data.json"):
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump({"project_info": {}, "school_info": {}, "interactions": []}, f, ensure_ascii=False, indent=2)

    def load_data(self):
        with open(self.file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_data(self, data):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_interaction(self, user_name, user_text, bot_response):
        data = self.load_data()
        if "interactions" not in data:
            data["interactions"] = []
        
        data["interactions"].append({
            "user": user_name,
            "text": user_text,
            "response": bot_response
        })
        
        # Keep only last 100 interactions for performance
        if len(data["interactions"]) > 100:
            data["interactions"] = data["interactions"][-100:]
            
        self.save_data(data)

    def get_knowledge_summary(self):
        data = self.load_data()
        knowledge = []
        
        if "project_info" in data:
            knowledge.append(f"Проект: {data['project_info'].get('name')}")
            knowledge.append(f"Миссия: {data['project_info'].get('mission')}")

        if "school_info" in data:
            school = data["school_info"]
            knowledge.append(f"Школа: {school.get('name')}")
            knowledge.append(f"Описание: {school.get('description')}")
            
            if "courses" in school:
                knowledge.append("Курсы:")
                for course in school["courses"]:
                    knowledge.append(f"- {course['name']}: {course['price']}")
                    
            if "locations" in school:
                knowledge.append("Адреса:")
                for loc in school["locations"]:
                    knowledge.append(f"- {loc['city']}, {loc['address']}")
                    
        return "\n".join(knowledge)
