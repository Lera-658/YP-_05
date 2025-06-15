import sys
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel,
                             QPushButton, QVBoxLayout, QStackedWidget, QDialog,
                             QHBoxLayout, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, QRect, QUrl
from PyQt6.QtGui import QPainter, QColor, QFont, QPalette
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
import math
import time

# CSS стили для интерфейса
STYLE_SHEET = """
QMainWindow {
    background-color: #2c3e50;
}
QLabel {
    color: #ecf0f1;
}
QPushButton {
    font-size: 16px;
}
QPushButton:hover {
    background-color: #2980b9;
}
QPushButton:pressed {
    background-color: #1f6aa5;
}
QDialog {
    background-color: #2c3e50;
}
"""


class GameOverDialog(QDialog):
    """Диалоговое окно окончания игры"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Игра окончена")
        self.setFixedSize(300, 150)
        self.setStyleSheet(STYLE_SHEET)
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса диалогового окна"""
        layout = QVBoxLayout()

        # Сообщение о конце игры
        message = QLabel("Игра окончена!")
        message.setFont(QFont('Arial', 20))
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message)

        # Разметка для кнопок
        button_layout = QHBoxLayout()

        # Кнопка перезапуска
        restart_button = QPushButton("Начать заново")
        restart_button.setFont(QFont('Arial', 14))
        restart_button.clicked.connect(self.accept)
        button_layout.addWidget(restart_button)

        # Кнопка выхода
        exit_button = QPushButton("Выход")
        exit_button.setFont(QFont('Arial', 14))
        exit_button.clicked.connect(self.reject)
        button_layout.addWidget(exit_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)


class MainMenu(QWidget):
    """Главное меню игры"""

    def __init__(self, game_window):
        super().__init__()
        self.game_window = game_window
        self.setStyleSheet(STYLE_SHEET)
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса главного меню"""
        layout = QVBoxLayout()

        # Заголовок
        title = QLabel("Змейка")
        title.setFont(QFont('Arial', 32))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Кнопка начала игры
        play_button = QPushButton("Играть")
        play_button.setFont(QFont('Arial', 16))
        play_button.setFixedSize(200, 50)
        play_button.clicked.connect(self.start_game)
        layout.addWidget(play_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Кнопка правил
        rules_button = QPushButton("Правила")
        rules_button.setFont(QFont('Arial', 16))
        rules_button.setFixedSize(200, 50)
        rules_button.clicked.connect(self.show_rules)
        layout.addWidget(rules_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def start_game(self):
        """Запуск игры"""
        self.game_window.start_game()

    def show_rules(self):
        """Показать правила"""
        self.game_window.show_rules()


class RulesWindow(QWidget):
    """Окно с правилами игры"""

    def __init__(self, game_window):
        super().__init__()
        self.game_window = game_window
        self.setStyleSheet(STYLE_SHEET)
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса окна правил"""
        layout = QVBoxLayout()

        # Заголовок
        title = QLabel("Правила игры")
        title.setFont(QFont('Arial', 24))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Текст правил
        rules_text = QLabel(
            "Цель игры — набрать как можно больше очков за счёт\n"
            "увеличения длины змейки. При поглощении специального\n"
            "объекта на игровом экране длина змейки увеличивается на один блок.\n"
            "Змейка может двигаться влево, вправо, вверх или вниз. Не может \n"
            "двигаться за пределы экрана, при столкновении с границами \n"
            "игра заканчивается.\n"
            "Игра заканчивается, когда змейка врезается сама в себя. Ещё \n"
            "игра заканчивается, когда пользователь закрывает окно. \n"
            "Удачи!"
        )
        rules_text.setFont(QFont('Arial', 14))
        rules_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(rules_text)

        # Кнопка возврата
        back_button = QPushButton("Вернуться в меню")
        back_button.setFont(QFont('Arial', 16))
        back_button.setFixedSize(200, 50)
        back_button.clicked.connect(self.go_back)
        layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def go_back(self):
        """Возврат в главное меню"""
        self.game_window.show_main_menu()


class SnakeGame(QMainWindow):
    """Основной класс игры 'Змейка'"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Змейка")
        self.setFixedSize(1280, 720)
        self.setStyleSheet(STYLE_SHEET)

        # Константы игры
        self.CELL_SIZE = 20  # Размер одной клетки
        self.PADDING = 40  # Отступ от краев
        self.GRID_WIDTH = 60  # Ширина игрового поля в клетках
        self.GRID_HEIGHT = 32  # Высота игрового поля в клетках
        self.GAME_SPEED = 100  # Скорость игры (мс)

        # Создаем стек виджетов для разных экранов
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Создаем главное меню
        self.main_menu = MainMenu(self)
        self.stacked_widget.addWidget(self.main_menu)

        # Создаем окно правил
        self.rules_window = RulesWindow(self)
        self.stacked_widget.addWidget(self.rules_window)

        # Создаем игровой виджет
        self.game_widget = QWidget()
        self.game_widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.stacked_widget.addWidget(self.game_widget)

        # Настройка метки счета
        self.score_label = QLabel(self.game_widget)
        self.score_label.setFont(QFont('Arial', 16))
        self.score_label.setGeometry(self.PADDING, self.PADDING - 40, 200, 30)

        # Настройка управления музыкой
        self.setup_music_control()

        # Инициализация состояния игры
        self.init_game()

        # Показываем главное меню при запуске
        self.show_main_menu()

    def setup_music_control(self):
        """Настройка управления музыкой"""
        # Кнопка музыки
        self.music_button = QPushButton("Музыка: ВКЛ", self.game_widget)
        self.music_button.setFont(QFont('Arial', 12))
        self.music_button.setGeometry(self.width() - 150, 10, 120, 30)
        self.music_button.clicked.connect(self.toggle_music)

        # Настройка плеера
        self.music_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.music_player.setAudioOutput(self.audio_output)
        self.music_player.setSource(QUrl.fromLocalFile("music.mp3"))
        self.audio_output.setVolume(0.5)
        self.music_player.play()
        self.music_on = True

    def toggle_music(self):
        """Включение/выключение музыки"""
        if self.music_on:
            self.music_player.pause()
            self.music_button.setText("Музыка: ВЫКЛ")
        else:
            self.music_player.play()
            self.music_button.setText("Музыка: ВКЛ")
        self.music_on = not self.music_on

    def init_game(self):
        """Инициализация состояния игры"""
        # Создаем стены
        self.walls = []
        # Верхняя и нижняя стены
        for x in range(self.GRID_WIDTH):
            self.walls.append((x, 0))
            self.walls.append((x, self.GRID_HEIGHT - 1))
        # Левая и правая стены
        for y in range(self.GRID_HEIGHT):
            self.walls.append((0, y))
            self.walls.append((self.GRID_WIDTH - 1, y))

        # Состояние игры
        self.snake = [(5, 5), (4, 5), (3, 5)]  # Начальная позиция змейки
        self.direction = Qt.Key.Key_Right  # Начальное направление
        self.food = self.generate_food()  # Генерация еды
        self.score = 0  # Счет
        self.game_over = False  # Флаг окончания игры

        # Настройка игрового таймера
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game)

    def show_main_menu(self):
        """Показать главное меню"""
        self.stacked_widget.setCurrentWidget(self.main_menu)

    def show_rules(self):
        """Показать правила"""
        self.stacked_widget.setCurrentWidget(self.rules_window)

    def start_game(self):
        """Начать новую игру"""
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
        self.init_game()
        self.stacked_widget.setCurrentWidget(self.game_widget)
        self.game_widget.setFocus()
        self.timer.start(self.GAME_SPEED)
        self.update_score()

    def generate_food(self):
        """Генерация новой еды на поле"""
        while True:
            x = random.randint(1, self.GRID_WIDTH - 2)
            y = random.randint(1, self.GRID_HEIGHT - 2)
            if (x, y) not in self.snake and (x, y) not in self.walls:
                return (x, y)

    def update_score(self):
        """Обновление счета на экране"""
        self.score_label.setText(f"Счёт: {self.score}")

    def handle_game_over(self):
        """Обработка окончания игры"""
        dialog = GameOverDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.start_game()
        else:
            self.close()

    def update_game(self):
        """Обновление состояния игры"""
        if self.game_over:
            return

        # Получаем текущую позицию головы
        head_x, head_y = self.snake[0]

        # Вычисляем новую позицию головы в зависимости от направления
        if self.direction == Qt.Key.Key_Left:
            head_x -= 1
        elif self.direction == Qt.Key.Key_Right:
            head_x += 1
        elif self.direction == Qt.Key.Key_Up:
            head_y -= 1
        elif self.direction == Qt.Key.Key_Down:
            head_y += 1

        # Проверка столкновений со стенами или собой
        if ((head_x, head_y) in self.walls or
                (head_x, head_y) in self.snake):
            self.game_over = True
            self.timer.stop()
            self.handle_game_over()
            return

        # Двигаем змейку
        self.snake.insert(0, (head_x, head_y))

        # Проверка съедания еды
        if (head_x, head_y) == self.food:
            self.score += 1
            self.update_score()
            self.food = self.generate_food()
        else:
            self.snake.pop()

        self.update()

    def keyPressEvent(self, event):
        """Обработка нажатий клавиш"""
        if self.stacked_widget.currentWidget() != self.game_widget:
            return

        if self.game_over:
            return

        # Запрет разворота на 180 градусов
        if event.key() == Qt.Key.Key_Left and self.direction != Qt.Key.Key_Right:
            self.direction = Qt.Key.Key_Left
        elif event.key() == Qt.Key.Key_Right and self.direction != Qt.Key.Key_Left:
            self.direction = Qt.Key.Key_Right
        elif event.key() == Qt.Key.Key_Up and self.direction != Qt.Key.Key_Down:
            self.direction = Qt.Key.Key_Up
        elif event.key() == Qt.Key.Key_Down and self.direction != Qt.Key.Key_Up:
            self.direction = Qt.Key.Key_Down

    def paintEvent(self, event):
        """Отрисовка игрового поля"""
        if self.stacked_widget.currentWidget() != self.game_widget:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # Включаем сглаживание
        
        # Рисуем темный фон
        painter.fillRect(0, 0, self.width(), self.height(), QColor(44, 62, 80))
        
        # Рисуем фон игрового поля
        game_area = QRect(
            self.PADDING,
            self.PADDING,
            self.GRID_WIDTH * self.CELL_SIZE,
            self.GRID_HEIGHT * self.CELL_SIZE
        )
        painter.fillRect(game_area, QColor(52, 73, 94))
        
        # Рисуем стены
        for wall in self.walls:
            x, y = wall
            painter.fillRect(
                self.PADDING + x * self.CELL_SIZE,
                self.PADDING + y * self.CELL_SIZE,
                self.CELL_SIZE - 1,
                self.CELL_SIZE - 1,
                QColor(149, 165, 166)
            )
        
        # Рисуем змейку
        for i, segment in enumerate(self.snake):
            x, y = segment
            center_x = self.PADDING + x * self.CELL_SIZE + self.CELL_SIZE // 2
            center_y = self.PADDING + y * self.CELL_SIZE + self.CELL_SIZE // 2
            
            if i == 0:  # Голова змейки
                # Определяем направление головы
                if len(self.snake) > 1:
                    next_x, next_y = self.snake[1]
                    if x < next_x:  # Движение влево
                        angle = 180
                    elif x > next_x:  # Движение вправо
                        angle = 0
                    elif y < next_y:  # Движение вверх
                        angle = 270
                    else:  # Движение вниз
                        angle = 90
                else:
                    angle = 0
                
                # Рисуем голову
                painter.save()
                painter.translate(center_x, center_y)
                painter.rotate(angle)
                
                # Основная часть головы
                head_color = QColor(46, 204, 113)
                painter.setBrush(head_color)
                painter.setPen(Qt.PenStyle.NoPen)
                
                # Рисуем овальную голову
                painter.drawEllipse(-self.CELL_SIZE//2, -self.CELL_SIZE//2, 
                                  self.CELL_SIZE, self.CELL_SIZE)
                
                # Рисуем глаза
                eye_color = QColor(255, 255, 255)
                painter.setBrush(eye_color)
                painter.drawEllipse(self.CELL_SIZE//4, -self.CELL_SIZE//4, 
                                  self.CELL_SIZE//4, self.CELL_SIZE//4)
                painter.drawEllipse(self.CELL_SIZE//4, self.CELL_SIZE//8, 
                                  self.CELL_SIZE//4, self.CELL_SIZE//4)
                
                # Рисуем зрачки
                pupil_color = QColor(0, 0, 0)
                painter.setBrush(pupil_color)
                painter.drawEllipse(self.CELL_SIZE//3, -self.CELL_SIZE//4, 
                                  self.CELL_SIZE//8, self.CELL_SIZE//8)
                painter.drawEllipse(self.CELL_SIZE//3, self.CELL_SIZE//8, 
                                  self.CELL_SIZE//8, self.CELL_SIZE//8)
                
                painter.restore()
            else:  # Тело змейки
                # Создаем градиентный цвет в зависимости от позиции в змейке
                color_value = max(0, 255 - (i * 5))
                body_color = QColor(46, 204, 113, color_value)
                
                # Рисуем сегмент тела
                painter.setBrush(body_color)
                painter.setPen(Qt.PenStyle.NoPen)
                
                # Определяем форму сегмента в зависимости от соседних сегментов
                if i < len(self.snake) - 1:
                    next_x, next_y = self.snake[i + 1]
                    prev_x, prev_y = self.snake[i - 1]
                    
                    # Если сегмент находится на повороте
                    if (x != next_x and y != next_y) or (x != prev_x and y != prev_y):
                        # Рисуем закругленный угол
                        painter.drawRoundedRect(
                            self.PADDING + x * self.CELL_SIZE,
                            self.PADDING + y * self.CELL_SIZE,
                            self.CELL_SIZE - 1,
                            self.CELL_SIZE - 1,
                            self.CELL_SIZE // 2,
                            self.CELL_SIZE // 2
                        )
                    else:
                        # Рисуем обычный сегмент
                        painter.drawRoundedRect(
                            self.PADDING + x * self.CELL_SIZE,
                            self.PADDING + y * self.CELL_SIZE,
                            self.CELL_SIZE - 1,
                            self.CELL_SIZE - 1,
                            self.CELL_SIZE // 3,
                            self.CELL_SIZE // 3
                        )
                else:
                    # Хвост
                    painter.drawRoundedRect(
                        self.PADDING + x * self.CELL_SIZE,
                        self.PADDING + y * self.CELL_SIZE,
                        self.CELL_SIZE - 1,
                        self.CELL_SIZE - 1,
                        self.CELL_SIZE // 2,
                        self.CELL_SIZE // 2
                    )
        
        # Рисуем еду с пульсирующим эффектом
        food_x, food_y = self.food
        pulse = abs(math.sin(time.time() * 5)) * 0.3 + 0.7  # Эффект пульсации
        
        # Рисуем яблоко
        painter.setBrush(QColor(231, 76, 60, int(255 * pulse)))
        painter.setPen(Qt.PenStyle.NoPen)
        
        # Основная часть яблока
        painter.drawEllipse(
            self.PADDING + food_x * self.CELL_SIZE,
            self.PADDING + food_y * self.CELL_SIZE,
            self.CELL_SIZE - 1,
            self.CELL_SIZE - 1
        )
        
        # Рисуем листик
        painter.setBrush(QColor(46, 204, 113))
        painter.drawEllipse(
            self.PADDING + food_x * self.CELL_SIZE + self.CELL_SIZE//2,
            self.PADDING + food_y * self.CELL_SIZE - self.CELL_SIZE//4,
            self.CELL_SIZE//2,
            self.CELL_SIZE//2
        )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = SnakeGame()
    game.show()
    sys.exit(app.exec())