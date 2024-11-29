# file: poetry_trainer.py

import streamlit as st
from enum import Enum
from typing import List
import re
import random
import toml
import os
from base_exercise import BaseExercise
from dataclasses import dataclass
from streamlit_sortables import sort_items


class ReorderWordsExercise(BaseExercise):
	"""Упражнение на восстановление порядка слов с уровнями сложности"""
	def __init__(self, poems: List[str]):
		super().__init__()
		self.poems = poems
		self.original_structure = []  # Исходная структура текста
		self.shuffled_structure = []  # Перемешанная структура текста
		self.level_type = 1  # Текущий уровень сложности
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


def render_reorder_exercise(exercise: ReorderWordsExercise):
	"""Рендеринг упражнения с уровнями"""
	st.write("### Уровень:", exercise.level)

	if st.button("Создать новое задание") or not exercise.shuffled_structure:
		exercise.prepare_task()

	user_reordered = []

	if exercise.level_type in [1, 2, 4]:
		# Отображение строк
		for idx, shuffled_words in enumerate(exercise.shuffled_structure):
			st.write(f"Строка {idx + 1}:")
			reordered = sort_items(shuffled_words)
			user_reordered.append(reordered)
	elif exercise.level_type in [3, 5]:
		# Отображение общего списка слов
		st.write("Слова:")
		user_reordered = sort_items(exercise.shuffled_structure)

	if st.button("Проверить ответ"):
		is_correct = exercise.check_answer(user_reordered)
		exercise.update_progress(is_correct)

		if is_correct:
			st.success("Правильно! Строфа завершена.")
			exercise.strophes_completed += 1

			# Если все строфы завершены
			if exercise.strophes_completed == len(exercise.poems) and exercise.level_type < 3:
				st.success("Вы завершили все строфы на текущем уровне! Переход на следующий уровень.")
				exercise.level_up()
			elif exercise.strophes_completed >= 3 and exercise.level_type >= 3:
				st.success("Вы завершили 3 строфы подряд без ошибок! Переход на следующий уровень.")
				exercise.level_up()

			exercise.prepare_task()
		else:
			st.error("Неправильно. Попробуйте еще раз.")
			if exercise.lives == 0:
				st.warning("Жизни закончились! Вы откатываетесь на предыдущий уровень.")
				exercise.level = max(1, exercise.level - 1)
				exercise.level_type = exercise.level
				exercise.lives = 2  # Восстановление жизней
			st.warning(f"Осталось жизней: {exercise.lives}")


class GapFillingExercise(BaseExercise):
	"""Класс для упражнений с заполнением пропусков"""
	def __init__(self, poems: List[str]):
		super().__init__()
		self.poems = poems
		self.current_strophe_index = 0
		self.gaps: List[Gap] = []
		self.text_with_gaps = ""

	def prepare_task(self):
		"""Подготовка задания с сохранением порядка пропусков"""
		current_strophe = self.poems[self.current_strophe_index]
		words = re.findall(r'[а-яА-ЯёЁ]+', current_strophe)
		
		# Выбираем случайные индексы для пропусков
		num_gaps = min(self.level, len(words))
		gap_indices = sorted(random.sample(range(len(words)), num_gaps))
		
		# Создаем пропуски с сохранением позиций
		self.gaps = []
		result_text = current_strophe
		
		# Обрабатываем индексы в обратном порядке, чтобы не сбить позиции
		for idx in reversed(gap_indices):
			word = words[idx]
			# Находим позицию слова в оригинальном тексте
			word_pos = result_text.index(word)
			self.gaps.insert(0, Gap(word, word_pos, word))
			result_text = result_text[:word_pos] + "___" + result_text[word_pos + len(word):]
		
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


def normalize_text(text: str) -> str:
	"""Нормализация текста"""
	cleaned_text = re.sub(r'[^а-яА-ЯёЁ ]', '', text)
	return re.sub(r'\s+', ' ', cleaned_text).strip()


def init_session_state():
	"""Инициализация состояния сессии"""
	if "exercise" not in st.session_state:
		# Загрузка стихов из TOML файла
		poems = load_poems()
		st.session_state.exercise = GapFillingExercise(poems)


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


@dataclass
class Gap:
	"""Класс для хранения информации о пропуске"""
	word: str
	position: int
	original_text: str


class ExerciseType(Enum):
	GAP_FILLING = "Заполнение пропусков"
	SEQUENCE = "Восстановление последовательности"
	WORD_ORDER = "Восстановление порядка слов"


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


def render_gap_exercise(exercise: GapFillingExercise):
	"""Отображение упражнения с заполнением пропусков"""
	# Выбор строфы
	st.write("### Выберите строфу:")
	selected_strophe = st.selectbox(
		"Выберите строфу для работы:",
		options=range(1, len(exercise.poems) + 1),
		format_func=lambda i: f"Строфа {i}"
	)
	exercise.current_strophe_index = selected_strophe - 1

	# Отображение уровня и задания
	st.write("### Уровень:", exercise.level)
	st.write("Попробуйте заполнить пропуски в следующем тексте:")

	if st.button("Создать новое задание") or not exercise.text_with_gaps:
		exercise.prepare_task()

	st.write(exercise.text_with_gaps.replace("\n", "  \n"))

	# Форма ввода
	with st.form("gap_form", clear_on_submit=False):
		user_answers = []
		for i in range(len(exercise.gaps)):
			user_input = st.text_input(f"Введите слово для пропуска {i + 1}:", key=f"gap_{i}")
			user_answers.append(user_input)

		if st.form_submit_button("Проверить ответы"):
			is_correct = exercise.check_answer(user_answers)
			exercise.update_progress(is_correct)

			if is_correct:
				st.success("Вы правильно заполнили все пропуски!")
				if exercise.consecutive_correct == 3:
					st.success("Вы перешли на следующий уровень!")
				exercise.prepare_task()
			else:
				st.warning("Ошибки в заполнении.")
				st.write("Правильные ответы были:")
				for gap in exercise.gaps:
					st.write(f"— {gap.word}")
				st.warning(f"Осталось жизней: {exercise.lives}")

	# Визуализация прогресса
	st.write("### История активности:")
	activity_display = "".join(
		"<span style='color: green;'>🟩</span>" if status == "success" 
		else "<span style='color: red;'>🟥</span>"
		for status in exercise.activity_history
	)
	st.write(f"### Жизни: {'❤️ ' * exercise.lives}{'🖤 ' * (2 - exercise.lives)}")
	st.markdown(activity_display, unsafe_allow_html=True)


def render_sequence_exercise(exercise: SequenceExercise):
	"""Отображение упражнения с последовательностью"""
	# Выбор строф
	st.write("### Выберите строфы для работы:")
	all_strophes = range(len(exercise.poems))
	selected = st.multiselect(
		"Строфы:",
		options=list(all_strophes),
		default=[0],
		format_func=lambda x: f"Строфа {x + 1}"
	)
	exercise.selected_strophes = selected if selected else [0]

	st.write("### Уровень:", exercise.level)
	
	if st.button("Создать новое задание") or not exercise.sequence_words:
		exercise.prepare_task()

	with st.form("sequence_form"):
		st.write("### Расставьте слова в правильном порядке:")
		user_sequence = []
		
		for i in range(len(exercise.current_sequence)):
			selected = st.selectbox(
				f"Позиция {i + 1}:",
				options=exercise.current_sequence,
				key=f"seq_{i}"
			)
			user_sequence.append(selected)

		if st.form_submit_button("Проверить ответ"):
			is_correct = exercise.check_answer(user_sequence)
			exercise.update_progress(is_correct)

			if is_correct:
				st.success("Правильно! Последовательность восстановлена верно.")
				if exercise.consecutive_correct == 3:
					st.success("Вы перешли на следующий уровень!")
					# Увеличиваем сложность
					new_strophes = min(len(exercise.poems), len(exercise.selected_strophes) + 1)
					exercise.selected_strophes = list(range(new_strophes))
				exercise.prepare_task()
			else:
				st.error("Неправильно. Попробуйте еще раз.")
				st.write("### Исходные строки для справки:")
				for line in exercise.get_original_lines():
					st.write(line)
				st.write("### Правильная последовательность:")
				for i, (word, _, _) in enumerate(exercise.sequence_words, 1):
					st.write(f"{i}. {word}")
				st.warning(f"Осталось жизней: {exercise.lives}")

	st.write("### История активности:")
	activity_display = "".join(
		"<span style='color: green;'>🟩</span>" if status == "success" 
		else "<span style='color: red;'>🟥</span>"
		for status in exercise.activity_history
	)
	st.write(f"### Жизни: {'❤️ ' * exercise.lives}{'🖤 ' * (2 - exercise.lives)}")
	st.markdown(activity_display, unsafe_allow_html=True)


def main():
	st.title("Тренажер стихотворений")
	# Инициализация состояния
	if "gap_exercise" not in st.session_state or "sequence_exercise" not in st.session_state:
		poems = load_poems()
		st.session_state.gap_exercise = GapFillingExercise(poems)
		st.session_state.sequence_exercise = SequenceExercise(poems)
		st.session_state.reorder_exercise = ReorderWordsExercise(poems)

	# Выбор типа упражнения
	exercise_type = st.radio(
		"Выберите тип упражнения:",
		[ExerciseType.GAP_FILLING.value, ExerciseType.SEQUENCE.value, ExerciseType.WORD_ORDER.value]
	)

	if exercise_type == ExerciseType.GAP_FILLING.value:
		render_gap_exercise(st.session_state.gap_exercise)
	elif exercise_type == ExerciseType.SEQUENCE.value:
		render_sequence_exercise(st.session_state.sequence_exercise)
	elif exercise_type == ExerciseType.WORD_ORDER.value:
		render_reorder_exercise(st.session_state.reorder_exercise)


if __name__ == "__main__":
	main()
