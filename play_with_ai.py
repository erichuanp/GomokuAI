import tkinter as tk
from gomoku.game import Gomoku
from gomoku.ai import QLearningAI


class GomokuGUI:
    def __init__(self, master, size=15):
        self.master = master
        self.size = size
        self.game = Gomoku(size)
        self.ai = QLearningAI(self.game)
        self.cell_size = 40
        self.canvas = tk.Canvas(master, width=self.size * self.cell_size, height=self.size * self.cell_size)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.human_move)
        self.draw_board()
        self.master.bind("<s>", self.reset_game)
        self.ai_turn = False  # Determine whose turn it is, False means human's turn
        self.human_player = None  # 0 for black, 1 for white
        self.ask_human_color()

    def draw_board(self, win_cells=None):
        self.canvas.delete("all")
        for i in range(self.size):
            for j in range(self.size):
                x0, y0 = i * self.cell_size, j * self.cell_size
                x1, y1 = x0 + self.cell_size, y0 + self.cell_size
                self.canvas.create_rectangle(x0, y0, x1, y1, fill="white")
                if self.game.board[i][j] == 1:
                    color = "black"
                    outline_color = "red" if win_cells and (i, j) in win_cells else color
                    self.canvas.create_oval(x0 + 5, y0 + 5, x1 - 5, y1 - 5, fill=color, outline=outline_color)
                elif self.game.board[i][j] == 2:
                    color = "white"
                    outline_color = "red" if win_cells and (i, j) in win_cells else "black"
                    self.canvas.create_oval(x0 + 5, y0 + 5, x1 - 5, y1 - 5, fill=color, outline=outline_color)

        # 标注每个棋子的手数
        for (x, y), step in self.ai.moves:
            if self.game.board[x][y] != 0:
                text_color = "white" if self.game.board[x][y] == 1 else "black"
                self.canvas.create_text(
                    (x * self.cell_size + self.cell_size // 2, y * self.cell_size + self.cell_size // 2),
                    text=str(step), fill=text_color)
        self.master.update()

    def human_move(self, event):
        if self.ai_turn:
            return

        x, y = event.x // self.cell_size, event.y // self.cell_size
        if self.game.board[x][y] == 0:
            result = self.game.make_move(x, y)
            self.draw_board()
            if result != 0:
                print("You win!")
                self.highlight_winning_cells(x, y)
                return

            self.ai_turn = True
            self.master.after(500, self.ai_move)

    def ai_move(self):
        x, y = self.ai.get_action()
        result = self.game.make_move(x, y)
        self.draw_board()
        if result != 0:
            print("AI wins!")
            self.highlight_winning_cells(x, y)
            return

        self.ai_turn = False

    def highlight_winning_cells(self, x, y):
        win_cells = self.get_winning_cells(x, y)
        self.draw_board(win_cells)
        self.master.after(2000, self.reset_game)

    def get_winning_cells(self, x, y):
        win_cells = [(x, y)]
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dx, dy in directions:
            count = 1
            temp_cells = [(x, y)]
            for i in range(1, 5):
                nx, ny = x + i * dx, y + i * dy
                if 0 <= nx < self.size and 0 <= ny < self.size and self.game.board[nx][ny] == self.game.current_player:
                    temp_cells.append((nx, ny))
                    count += 1
                else:
                    break
            for i in range(1, 5):
                nx, ny = x - i * dx, y - i * dy
                if 0 <= nx < self.size and 0 <= ny < self.size and self.game.board[nx][ny] == self.game.current_player:
                    temp_cells.append((nx, ny))
                    count += 1
                else:
                    break
            if count >= 5:
                win_cells = temp_cells
                break
        return win_cells

    def reset_game(self, event=None):
        self.game.reset()
        self.ai.reset_step_count()
        self.ai_turn = False
        self.draw_board()

    def ask_human_color(self):
        color = input("Choose your color: 0 for Black, 1 for White: ")
        self.human_player = int(color)
        if self.human_player == 1:
            self.ai_turn = True
            self.master.after(500, self.ai_move)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Gomoku: Play with AI")
    app = GomokuGUI(root)
    root.mainloop()
