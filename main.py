import tkinter as tk
from gomoku.game import Gomoku
from gomoku.ai import QLearningAI


class GomokuGUI:
    def __init__(self, master, size=15):
        self.master = master
        self.size = size
        self.game = Gomoku(size)
        self.ai1 = QLearningAI(self.game, q_table_file="ai1_q_table.pkl")
        self.ai2 = QLearningAI(self.game, q_table_file="ai2_q_table.pkl")
        self.current_ai = self.ai1
        self.cell_size = 40
        self.canvas = tk.Canvas(master, width=self.size * self.cell_size, height=self.size * self.cell_size)
        self.canvas.pack()
        self.draw_board()
        self.master.bind("<s>", self.stop_training)
        self.training = True
        self.play_game()

    def draw_board(self, win_cells=None):
        self.canvas.delete("all")
        for i in range(self.size):
            for j in range(self.size):
                x0, y0 = i * self.cell_size, j * self.cell_size
                x1, y1 = x0 + self.cell_size, y0 + self.cell_size
                self.canvas.create_rectangle(x0, y0, x1, y1, fill="white")
                if self.game.board[i][j] == 1:
                    color = "black"
                    self.canvas.create_oval(x0 + 5, y0 + 5, x1 - 5, y1 - 5, fill=color,
                                            outline="red" if win_cells and (i, j) in win_cells else color)
                elif self.game.board[i][j] == 2:
                    color = "white"
                    self.canvas.create_oval(x0 + 5, y0 + 5, x1 - 5, y1 - 5, fill=color,
                                            outline="red" if win_cells and (i, j) in win_cells else color)

        # 标注每个棋子的手数
        for (x, y), step in self.ai1.moves + self.ai2.moves:
            if self.game.board[x][y] != 0:
                color = "white" if self.game.board[x][y] == 1 else "black"
                self.canvas.create_text(
                    (x * self.cell_size + self.cell_size // 2, y * self.cell_size + self.cell_size // 2),
                    text=str(step), fill=color)
        self.master.update()

    def play_game(self):
        if self.training:
            self.game.reset()
            self.ai1.q_table = self.ai1.load_q_table()
            self.ai2.q_table = self.ai2.load_q_table()
            self.ai1.reset_step_count()
            self.ai2.reset_step_count()
            self.update_board()

    def update_board(self):
        if not self.training:
            return
        x, y = self.current_ai.get_action()
        result = self.game.make_move(x, y)
        self.draw_board()

        # 输出策略信息
        for step, strategy in self.current_ai.strategies:
            print(f"AI {self.game.current_player} used {strategy} at step {step}")

        if result != 0:
            print(f"Player {self.game.current_player} wins!")
            print(f"AI1 Score: {self.ai1.score}, AI2 Score: {self.ai2.score}")
            win_cells = self.get_winning_cells(x, y)
            self.draw_board(win_cells)
            self.ai1.save_q_table()
            self.ai2.save_q_table()
            self.master.after(2000, self.play_game)  # 2秒后开始新游戏
        else:
            self.current_ai = self.ai2 if self.current_ai == self.ai1 else self.ai1
            self.master.after(500, self.update_board)  # 500毫秒后更新棋盘

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

    def stop_training(self, event):
        self.training = False
        print("Training stopped.")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Gomoku")
    app = GomokuGUI(root)
    root.mainloop()
