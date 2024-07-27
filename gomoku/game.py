class Gomoku:
    def __init__(self, size=15):
        self.size = size
        self.board = [[0 for _ in range(size)] for _ in range(size)]
        self.current_player = 1

    def reset(self):
        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.current_player = 1

    def make_move(self, x, y):
        if self.board[x][y] != 0:
            return False
        self.board[x][y] = self.current_player
        if self.check_win(x, y):
            return self.current_player
        self.current_player = 3 - self.current_player
        return 0

    def check_win(self, x, y):
        def count_stones(dx, dy):
            count = 0
            for i in range(-4, 5):
                nx, ny = x + i * dx, y + i * dy
                if 0 <= nx < self.size and 0 <= ny < self.size and self.board[nx][ny] == self.current_player:
                    count += 1
                    if count == 5:
                        return True
                else:
                    count = 0
            return False

        return (count_stones(1, 0) or count_stones(0, 1) or
                count_stones(1, 1) or count_stones(1, -1))
