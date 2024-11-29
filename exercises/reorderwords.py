from base_exercise import BaseExercise

import re
import random
from typing import List

import streamlit as st
from streamlit_sortables import sort_items


class ReorderWordsExercise(BaseExercise):
	"""Упражнение на восстановление порядка слов с уровнями сложности"""
	def __init__(self, poems: List[str]):
		super().__init__()
		self.poems = poems
		self.original_structure = []  # Исходная структура текста
		self.shuffled_structure = []  # Перемешанная структура текста
		self.current_strophe_index = 0  # Индекс текущей строфы
		self.strophes_completed = 0  # Количество завершённых строф на уровне

	def prepare_task(self):
		"""Подготовка задания в зависимости от уровня"""
		self.original_structure = []
		self.shuffled_structure = []

		# Если строфы закончились на текущем уровне
		if self.current_strophe_index >= len(self.poems):
			self.current_strophe_index = 0
			self.strophes_completed = 0
			self._level_up()  # Переключаем уровень

		# Получаем строфы для текущего задания
		if self.level_type < 4:
			strophe = self.poems[self.current_strophe_index]
			self.current_strophe_index += 1
		else:
			strophe = "\n".join(self.poems[:2])  # Для уровня 4+ берём первые 2 строфы

		if self.level_type == 1:
			# Уровень 1: сортировка слов в строках одной строфы
			lines = [line.strip() for line in strophe.split('\n') if line.strip()]
			for line in lines:
				words = re.findall(r'[а-яА-ЯёЁ]+', line)
				self.original_structure.append(words)
				shuffled_words = words[:]
				random.shuffle(shuffled_words)
				self.shuffled_structure.append(shuffled_words)

		elif self.level_type == 2:
			# Уровень 2: перемешивание строк и сортировка слов
			lines = [line.strip() for line in strophe.split('\n') if line.strip()]
			random.shuffle(lines)
			for line in lines:
				words = re.findall(r'[а-яА-ЯёЁ]+', line)
				self.original_structure.append(words)
				shuffled_words = words[:]
				random.shuffle(shuffled_words)
				self.shuffled_structure.append(shuffled_words)

		elif self.level_type == 3:
			# Уровень 3: все слова одной строфы в одной куче
			words = re.findall(r'[а-яА-ЯёЁ]+', strophe)
			self.original_structure = words
			shuffled_words = words[:]
			random.shuffle(shuffled_words)
			self.shuffled_structure = shuffled_words

		elif self.level_type == 4:
			# Уровень 4: строки из нескольких строф
			lines = [line.strip() for line in strophe.split('\n') if line.strip()]
			for line in lines:
				words = re.findall(r'[а-яА-ЯёЁ]+', line)
				self.original_structure.append(words)
				shuffled_words = words[:]
				random.shuffle(shuffled_words)
				self.shuffled_structure.append(shuffled_words)

		elif self.level_type == 5:
			# Уровень 5: все слова из нескольких строф в одной куче
			words = re.findall(r'[а-яА-ЯёЁ]+', strophe)
			self.original_structure = words
			shuffled_words = words[:]
			random.shuffle(shuffled_words)
			self.shuffled_structure = shuffled_words

	def check_answer(self, user_reordered):
		"""Проверка ответа на уровне"""
		if self.level_type in [1, 2, 4]:
			# Проверяем каждую строку
			for user_line, original_line in zip(user_reordered, self.original_structure):
				if user_line != original_line:
					return False
		elif self.level_type in [3, 5]:
			# Проверяем все слова
			if user_reordered != self.original_structure:
				return False
		return True

	def _level_up(self):
		"""Переход на следующий уровень"""
		self.level_up()
		self.level_type = min(5, self.level_type + 1)
		self.current_strophe_index = 0
		self.strophes_completed = 0
		print(f"Переход на уровень {self.level_type}")

	def render(self):
		"""Рендеринг упражнения с уровнями"""
		st.write("### Уровень:", self.level)

		if st.button("Создать новое задание") or not self.shuffled_structure:
			self.prepare_task()

		user_reordered = []

		if self.level_type in [1, 2, 4]:
			# Отображение строк
			for idx, shuffled_words in enumerate(self.shuffled_structure):
				st.write(f"Строка {idx + 1}:")
				reordered = sort_items(shuffled_words)
				user_reordered.append(reordered)
		elif self.level_type in [3, 5]:
			# Отображение общего списка слов
			st.write("Слова:")
			user_reordered = sort_items(self.shuffled_structure)

		if st.button("Проверить ответ"):
			is_correct = self.check_answer(user_reordered)
			self.update_progress(is_correct)

			if is_correct:
				st.success("Правильно! Строфа завершена.")
				self.strophes_completed += 1

				# Если все строфы завершены
				if self.strophes_completed == len(self.poems) and self.level_type < 3:
					st.success("Вы завершили все строфы на текущем уровне! Переход на следующий уровень.")
					self.level_up()
				elif self.strophes_completed >= 3 and self.level_type >= 3:
					st.success("Вы завершили 3 строфы подряд без ошибок! Переход на следующий уровень.")
					self.level_up()

				self.prepare_task()
			else:
				st.error("Неправильно. Попробуйте еще раз.")
				if self.lives == 0:
					st.warning("Жизни закончились! Вы откатываетесь на предыдущий уровень.")
					self.level = max(1, self.level - 1)
					self.level_type = self.level
					self.lives = 2  # Восстановление жизней
				st.warning(f"Осталось жизней: {self.lives}")

		# Визуализация прогресса
		st.write("### История активности:")
		activity_display = "".join(
			"<span style='color: green;'>🟩</span>" if status == "success" 
			else "<span style='color: red;'>🟥</span>"
			for status in self.activity_history
		)
		st.write(f"### Жизни: {'❤️ ' * self.lives}{'🖤 ' * (2 - self.lives)}")
		st.markdown(activity_display, unsafe_allow_html=True)
