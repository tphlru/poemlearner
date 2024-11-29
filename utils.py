import re
from typing import List
import os
import toml


def normalize_text(text: str) -> str:
	"""Нормализация текста"""
	cleaned_text = re.sub(r'[^а-яА-ЯёЁ ]', '', text)
	return re.sub(r'\s+', ' ', cleaned_text).strip()


def load_poems() -> List[str]:
	"""Загрузка стихов из файла"""
	default_poems = [
		"Мороз и солнце; день чудесный!\nЕще ты дремлешь, друг прелестный —\n"
		"Пора, красавица, проснись:\nОткрой сомкнуты негой взоры.",
		"Под голубыми небесами\nВеликолепными коврами,\nБлестя на солнце, снег лежит;\n"
		"Прозрачный лес один чернеет,\nИ ель сквозь иней зеленеет,\nИ речка подо льдом блестит."
	]
	
	if os.path.exists("poems.toml"):
		with open("poems.toml", "r", encoding="utf-8") as file:
			return toml.load(file).get("poems", default_poems)
	return default_poems


def get_words(text: str) -> List[str]:
	"""Получение слов из текста"""
	w = re.findall(r'\w+', text.lower())
	word_positions = {}
	for word in w:
		# Используем регулярное выражение для поиска целых слов
		pattern = r'\b' + re.escape(word) + r'\b'
		matches = list(re.finditer(pattern, text.lower()))
		if matches:
			word_positions[word] = [match.start() for match in matches]
	return w, word_positions
