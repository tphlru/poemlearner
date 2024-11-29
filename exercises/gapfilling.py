from base_exercise import BaseExercise
from utils import normalize_text, get_words

import random
from typing import List
from dataclasses import dataclass

import streamlit as st


@dataclass
class Gap:
	"""Класс для хранения информации о пропуске"""
	word: str
	position: int
	original_text: str


class GapFillingExercise(BaseExercise):
	"""Класс для упражнений с заполнением пропусков"""
	def __init__(self, poems: List[str]):
		super().__init__()
		self.poems = poems
		self.current_strophe_index = 0
		self.gaps: List[Gap] = []
		self.text_with_gaps = ""

	def prepare_task(self):
		current_strophe = self.poems[self.current_strophe_index]
		words, word_positions = get_words(current_strophe)
		
		# Выбираем случайные индексы для пропусков
		num_gaps = min(self.level, len(word_positions))
		gap_indices = sorted(random.sample(range(len(word_positions)), num_gaps))
		
		# Создаем пропуски с сохранением позиций
		self.gaps = []
		result_text = current_strophe
				
		# Обрабатываем индексы в обратном порядке
		for i, idx in enumerate(reversed(gap_indices)):
			word = words[idx]
			if word in word_positions and word_positions[word]:
				# Берем первую доступную позицию для слова
				word_pos = word_positions[word][0]
				self.gaps.insert(0, Gap(word, word_pos, word))
				result_text = result_text[:word_pos] + f"_({len(self.gaps) - i + 1})_" + result_text[word_pos + len(word):]
				
				# Удаляем использованную позицию
				word_positions[word].pop(0)
		
		self.text_with_gaps = result_text

	def check_answer(self, user_answers: List[str]) -> bool:
		"""Проверка ответов с учетом порядка"""
		if len(user_answers) != len(self.gaps):
			return False
			
		correct = 0
		for user_word, gap in zip(user_answers, self.gaps):
			if normalize_text(user_word).lower().replace("ё", "е") == \
				normalize_text(gap.word).lower().replace("ё", "е"):
				correct += 1
				
		return correct == len(self.gaps)

	def render(self):
		"""Отображение упражнения с заполнением пропусков"""
		# Выбор строфы
		st.write("### Выберите строфу:")
		selected_strophe = st.selectbox(
			"Выберите строфу для работы:",
			options=range(1, len(self.poems) + 1),
			format_func=lambda i: f"Строфа {i}"
		)
		self.current_strophe_index = selected_strophe - 1

		# Отображение уровня и задания
		st.write("### Уровень:", self.level)
		st.write("Попробуйте заполнить пропуски в следующем тексте:")

		if st.button("Создать новое задание") or not self.text_with_gaps:
			self.prepare_task()

		st.write(self.text_with_gaps.replace("\n", "  \n"))

		# Форма ввода
		with st.form("gap_form", clear_on_submit=False):
			user_answers = []
			for i in range(len(self.gaps)):
				user_input = st.text_input(f"Введите слово для пропуска {i + 1}:", key=f"gap_{i}")
				user_answers.append(user_input)

			if st.form_submit_button("Проверить ответы"):
				is_correct = self.check_answer(user_answers)
				self.update_progress(is_correct)

				if is_correct:
					st.success("Вы правильно заполнили все пропуски!")
					if self.consecutive_correct == 3:
						st.success("Вы перешли на следующий уровень!")
					self.prepare_task()
				else:
					st.warning("Ошибки в заполнении.")
					st.write("Правильные ответы были:")
					for gap in self.gaps:
						st.write(f"— {gap.word}")
					st.warning(f"Осталось жизней: {self.lives}")
