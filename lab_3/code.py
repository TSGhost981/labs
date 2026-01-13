import tkinter as tk
from tkinter import messagebox
import random


class Minesweeper:
    def __init__(self, root):
        self.root = root
        self.root.title("Minesweeper")

        # Игровые параметры
        self.rows = 10
        self.cols = 10
        self.mines = 15
        self.colors = ["", "blue", "green", "red", "darkblue", "darkred", "cyan", "black", "gray"]

        self.first_move = True
        self.game_active = True
        self.flags = 0

        self.create_interface()
        self.reset_game()

    def create_interface(self):
        """Создание интерфейса игры"""
        # Верхняя панель
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        self.mine_counter = tk.Label(top_frame, text=f"Mines: {self.mines}",
                                     font=("Arial", 12, "bold"), fg="darkred")
        self.mine_counter.pack(side=tk.LEFT, padx=20)

        self.reset_btn = tk.Button(top_frame, text="🔄", font=("Arial", 14),
                                   command=self.reset_game, bg="lightblue")
        self.reset_btn.pack(side=tk.LEFT, padx=20)

        self.flag_counter = tk.Label(top_frame, text=f"Flags: 0",
                                     font=("Arial", 12, "bold"), fg="darkblue")
        self.flag_counter.pack(side=tk.LEFT, padx=20)

        # Игровое поле
        self.board_frame = tk.Frame(self.root)
        self.board_frame.pack()

        self.tiles = []
        for i in range(self.rows):
            row = []
            for j in range(self.cols):
                tile = tk.Button(self.board_frame, width=3, height=1, font=("Arial", 10),
                                 bg="lightgray", relief="raised")
                tile.grid(row=i, column=j, padx=1, pady=1)

                # Привязка событий
                tile.bind("<Button-1>", lambda e, r=i, c=j: self.uncover(r, c))
                tile.bind("<Button-3>", lambda e, r=i, c=j: self.mark(r, c))

                row.append(tile)
            self.tiles.append(row)

    def reset_game(self):
        """Сброс игры"""
        self.first_move = True
        self.game_active = True
        self.flags = 0
        self.reset_btn.config(text="😊")

        # Обновление счетчиков
        self.mine_counter.config(text=f"Mines: {self.mines}")
        self.flag_counter.config(text=f"Flags: {self.flags}")

        # Инициализация игровых данных
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.opened = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.marked = [[False for _ in range(self.cols)] for _ in range(self.rows)]

        # Сброс внешнего вида кнопок
        for i in range(self.rows):
            for j in range(self.cols):
                self.tiles[i][j].config(text="", bg="lightgray", relief="raised",
                                        state="normal", fg="black")

    def place_mines(self, safe_row, safe_col):
        """Размещение мин"""
        placed = 0
        while placed < self.mines:
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)

            # Не ставить мину в начальную клетку и рядом
            if (r == safe_row and c == safe_col) or \
                    abs(r - safe_row) <= 1 and abs(c - safe_col) <= 1:
                continue

            if self.board[r][c] != -1:
                self.board[r][c] = -1
                placed += 1

                # Обновление чисел вокруг мины
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols:
                            if self.board[nr][nc] != -1:
                                self.board[nr][nc] += 1

    def uncover(self, r, c):
        """Открытие клетки"""
        if not self.game_active or self.marked[r][c]:
            return

        if self.first_move:
            self.place_mines(r, c)
            self.first_move = False

        # Попали на мину
        if self.board[r][c] == -1:
            self.game_over(False)
            return

        # Открытие клетки
        self.reveal(r, c)

        # Проверка победы
        if self.check_win():
            self.game_over(True)

    def reveal(self, r, c):
        """Рекурсивное открытие клеток"""
        if (r < 0 or r >= self.rows or c < 0 or c >= self.cols or
                self.opened[r][c] or self.marked[r][c]):
            return

        self.opened[r][c] = True
        value = self.board[r][c]

        # Обновление отображения
        self.tiles[r][c].config(relief="sunken", bg="white")

        if value > 0:
            color = self.colors[value] if value < len(self.colors) else "black"
            self.tiles[r][c].config(text=str(value), fg=color)

        # Если пустая клетка - открываем соседей
        if value == 0:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    self.reveal(r + dr, c + dc)

    def mark(self, r, c):
        """Установка/снятие флажка"""
        if not self.game_active or self.opened[r][c]:
            return

        if self.marked[r][c]:
            self.marked[r][c] = False
            self.flags -= 1
            self.tiles[r][c].config(text="", bg="lightgray")
        else:
            self.marked[r][c] = True
            self.flags += 1
            self.tiles[r][c].config(text="⚑", fg="red", bg="lightyellow")

        self.flag_counter.config(text=f"Flags: {self.flags}")

    def check_win(self):
        """Проверка выигрышных условий"""
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] != -1 and not self.opened[i][j]:
                    return False
        return True

    def game_over(self, won):
        """Обработка конца игры"""
        self.game_active = False

        if won:
            self.reset_btn.config(text="😎")
            messagebox.showinfo("Победа!", "Все мины обезврежены!")
        else:
            self.reset_btn.config(text="💀")
            self.show_all_mines()
            messagebox.showinfo("Поражение", "Вы подорвались на мине!")

    def show_all_mines(self):
        """Показать все мины"""
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] == -1:
                    self.tiles[i][j].config(text="💣", bg="orange", fg="black")
                elif self.marked[i][j] and self.board[i][j] != -1:
                    self.tiles[i][j].config(text="❌", bg="pink")


def main():
    window = tk.Tk()
    game = Minesweeper(window)
    window.mainloop()


if __name__ == "__main__":
    main()