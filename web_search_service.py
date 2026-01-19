from duckduckgo_search import DDGS

class WebSearchService:
    def __init__(self):
        pass

    def search(self, query, max_results=5):
        """Выполняет поиск в DuckDuckGo и возвращает строку с результатами"""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                
            if not results:
                return "Поиск не дал результатов."
            
            formatted_results = []
            for i, r in enumerate(results, 1):
                title = r.get('title', 'Без названия')
                link = r.get('href', 'Нет ссылки')
                body = r.get('body', 'Нет описания')
                formatted_results.append(f"{i}. {title}\nURL: {link}\nОписание: {body}\n")
            
            return "\n".join(formatted_results)
        except Exception as e:
            return f"Ошибка при веб-поиске: {e}"

if __name__ == "__main__":
    searcher = WebSearchService()
    try:
        # Используем безопасный вывод для Windows консоли
        res = searcher.search("кулинарные курсы cook.ee таллин")
        print(res.encode('utf-8', errors='replace').decode('cp1251', errors='replace'))
    except Exception as e:
        print(f"Ошибка при тесте: {e}")
