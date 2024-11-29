# file: poetry_trainer.py

import streamlit as st
from enum import Enum

from exercises import GapFillingExercise, ReorderWordsExercise, SequenceExercise
from utils import load_poems


class ExerciseType(Enum):
	GAP_FILLING = "Заполнение пропусков"
	SEQUENCE = "Восстановление последовательности"
	WORD_ORDER = "Восстановление порядка слов"


def main():
	st.title("Тренажер стихотворений")

	names = ["gap_exercise", "sequence_exercise", "reorder_exercise"]
	
	# Инициализация состояния
	if any(name not in st.session_state for name in names):
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
		st.session_state.gap_exercise.render()
	elif exercise_type == ExerciseType.SEQUENCE.value:
		st.session_state.sequence_exercise.render()
	elif exercise_type == ExerciseType.WORD_ORDER.value:
		st.session_state.reorder_exercise.render()


if __name__ == "__main__":
	main()
