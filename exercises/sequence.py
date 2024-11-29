from base_exercise import BaseExercise

import re
import random
from typing import List

import streamlit as st


class SequenceExercise(BaseExercise):
	"""Упражнение на восстановление последовательности слов"""
	def __init__(self, poems: List[str]):
		super().__init__()
		self.poems = poems
		self.selected_strophes = [0]
		self.sequence_words = []  # список кортежей (слово, номер_строки, оригинальная_строка)
		self.current_sequence = []  # перемешанные слова для отображения
		
	def prepare_task(self):
		"""Подготовка задания с выбором слов из каждой строки"""
		self.sequence_words = []
		
		for strophe_idx in self.selected_strophes:
			strophe = self.poems[strophe_idx]
			lines = [line.strip() for line in strophe.split('\n') if line.strip()]
			
			for i, line in enumerate(lines):
				words = re.findall(r'[а-яА-ЯёЁ]+', line)
				if words:
					word = random.choice(words)
					self.sequence_words.append((word, i, line))
					
		self.current_sequence = [w[0] for w in self.sequence_words]
		random.shuffle(self.current_sequence)

	def check_answer(self, user_sequence: List[str]) -> bool:
		"""Проверка правильности последовательности"""
		correct_sequence = [w[0] for w in self.sequence_words]
		return user_sequence == correct_sequence

	def get_original_lines(self) -> List[str]:
		"""Получение оригинальных строк"""
		return [w[2] for w in self.sequence_words]
	
	def render(self):
		"""Отображение упражнения с последовательностью"""
		# Выбор строф
		st.write("### Выберите строфы для работы:")
		all_strophes = range(len(self.poems))
		selected = st.multiselect(
			"Строфы:",
			options=list(all_strophes),
			default=[0],
			format_func=lambda x: f"Строфа {x + 1}"
		)
		self.selected_strophes = selected if selected else [0]

		st.write("### Уровень:", self.level)
		
		if st.button("Создать новое задание") or not self.sequence_words:
			self.prepare_task()

		with st.form("sequence_form"):
			st.write("### Расставьте слова в правильном порядке:")
			user_sequence = []
			
			for i in range(len(self.current_sequence)):
				selected = st.selectbox(
					f"Позиция {i + 1}:",
					options=self.current_sequence,
					key=f"seq_{i}"
				)
				user_sequence.append(selected)

			if st.form_submit_button("Проверить ответ"):
				is_correct = self.check_answer(user_sequence)
				self.update_progress(is_correct)

				if is_correct:
					st.success("Правильно! Последовательность восстановлена верно.")
					if self.consecutive_correct == 3:
						st.success("Вы перешли на следующий уровень!")
						# Увеличиваем сложность
						new_strophes = min(len(self.poems), len(self.selected_strophes) + 1)
						self.selected_strophes = list(range(new_strophes))
					self.prepare_task()
				else:
					st.error("Неправильно. Попробуйте еще раз.")
					st.write("### Исходные строки для справки:")
					for line in self.get_original_lines():
						st.write(line)
					st.write("### Правильная последовательность:")
					for i, (word, _, _) in enumerate(self.sequence_words, 1):
						st.write(f"{i}. {word}")
					st.warning(f"Осталось жизней: {self.lives}")

		st.write("### История активности:")
		activity_display = "".join(
			"<span style='color: green;'>🟩</span>" if status == "success" 
			else "<span style='color: red;'>🟥</span>"
			for status in self.activity_history
		)
		st.write(f"### Жизни: {'❤️ ' * self.lives}{'🖤 ' * (2 - self.lives)}")
		st.markdown(activity_display, unsafe_allow_html=True)
