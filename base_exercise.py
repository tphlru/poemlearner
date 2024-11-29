# file: base_exercise.py

class BaseExercise:
    """Базовый класс для всех типов упражнений"""
    def __init__(self):
        self.level = 1
        self.lives = 2
        self.consecutive_correct = 0
        self.activity_history = []

    def update_progress(self, is_correct: bool):
        """Обновление прогресса после ответа"""
        if is_correct:
            self.consecutive_correct += 1
            self.activity_history.append("success")
            if self.consecutive_correct == 3:
                self.level_up()
        else:
            self.consecutive_correct = 0
            self.activity_history.append("failure")
            self.lose_life()

    def level_up(self):
        """Переход на следующий уровень"""
        self.level += 1
        self.consecutive_correct = 0
        self.lives = 2

    def lose_life(self):
        """Потеря жизни и возможное понижение уровня"""
        self.lives -= 1
        if self.lives == 0:
            if self.level > 1:
                self.level -= 1
                self.lives = 2
            else:
                self.lives = 2
