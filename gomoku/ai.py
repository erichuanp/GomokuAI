import random
import numpy as np

class QLearningAI:
    def __init__(self, game, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.game = game
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.q_table = {}
        self.score = 0
        self.last_action = None
        self.last_state = None
        self.step_count = 0
        self.moves = []  # 记录每一步的位置和手数
        self.strategies = []  # 记录每一步使用的策略

    def get_state(self):
        return str(self.game.board)

    def get_q_value(self, state, action):
        return self.q_table.get((state, action), 0)

    def update_q_value(self, reward):
        if self.last_state is not None and self.last_action is not None:
            next_state = self.get_state()
            best_next_action = max([(self.get_q_value(next_state, a), a) for a in self.get_possible_actions()], default=(0, None))[1]
            td_target = reward + self.gamma * self.get_q_value(next_state, best_next_action)
            td_error = td_target - self.get_q_value(self.last_state, self.last_action)
            self.q_table[(self.last_state, self.last_action)] = self.get_q_value(self.last_state, self.last_action) + self.alpha * td_error

    def get_possible_actions(self):
        return [(x, y) for x in range(self.game.size) for y in range(self.game.size) if self.game.board[x][y] == 0]

    def match_pattern(self, x, y, dx, dy, pattern, player):
        size = self.game.size
        board = self.game.board
        for i in range(len(pattern)):
            nx, ny = x + i * dx, y + i * dy
            if nx < 0 or ny < 0 or nx >= size or ny >= size:
                return False
            if pattern[i] == '/' and board[nx][ny] != 0:
                return False
            if pattern[i] == '+' and board[nx][ny] != player:
                return False
            if pattern[i] == '-' and board[nx][ny] != 3 - player:
                return False
        return True

    def find_pattern(self, pattern, player):
        size = self.game.size
        for x in range(size):
            for y in range(size):
                for dx, dy in [(1, 0), (0, 1), (1, 1), (1, -1)]:
                    if self.match_pattern(x, y, dx, dy, pattern, player):
                        for i in range(len(pattern)):
                            nx, ny = x + i * dx, y + i * dy
                            if pattern[i] == '/':
                                return (nx, ny)
        return None

    def basic_strategy(self):
        board = self.game.board
        size = self.game.size
        current_player = self.game.current_player
        opponent = 3 - current_player

        # 1. 黑棋开局下中心
        if current_player == 1 and np.sum(board) == 0:
            return (size // 2, size // 2), "strategy 1: Place in the center"

        # 2. 白棋下在离黑棋不远的地方
        if current_player == 2 and np.sum(board) == 1:
            for x in range(size):
                for y in range(size):
                    if board[x][y] == 1:
                        for dx in [-1, 0, 1]:
                            for dy in [-1, 0, 1]:
                                nx, ny = x + dx, y + dy
                                if 0 <= nx < size and 0 <= ny < size and board[nx][ny] == 0:
                                    return (nx, ny), "strategy 2: Place near the first black stone"

        # 3. 防御对手的假胜棋
        for pattern in ["++++", "+++/+", "+/++/", "/+++/"]:
            action = self.find_pattern(pattern, opponent)
            if action:
                return action, f"strategy 3: Block opponent's假胜棋 {pattern}"

        # 4. 防御对手的胜棋
        for pattern in ["++++/", "+++/+/", "++/++/", "+/+++/"]:
            action = self.find_pattern(pattern, opponent)
            if action:
                return action, f"strategy 4: Block opponent's胜棋 {pattern}"

        # 5. 黑棋和白棋凑伏棋结构
        for pattern in ["++/", "+/+"]:
            action = self.find_pattern(pattern, current_player)
            if action:
                return action, f"strategy 5: Create伏棋 with {pattern}"

        # 6. 黑棋和白棋防御对手伏棋或自己凑伏棋
        for pattern in ["++/", "+/+"]:
            action = self.find_pattern(pattern, opponent)
            if action:
                return action, f"strategy 6: Block opponent's伏棋 {pattern}"
        for pattern in ["++/", "+/+"]:
            action = self.find_pattern(pattern, current_player)
            if action:
                return action, f"strategy 6: Create伏棋 with {pattern}"

        # 7. 黑棋和白棋尽量凑攻棋
        for pattern in ["+++/"]:
            action = self.find_pattern(pattern, current_player)
            if action:
                return action, f"strategy 7: Create攻棋 with {pattern}"

        # 8. 防御对手攻棋
        for pattern in ["+++/"]:
            action = self.find_pattern(pattern, opponent)
            if action:
                return action, f"strategy 8: Block opponent's攻棋 {pattern}"

        # 9. 尽量凑成胜棋
        for pattern in ["++++/"]:
            action = self.find_pattern(pattern, current_player)
            if action:
                return action, f"strategy 9: Create胜棋 with {pattern}"

        return None, None

    def get_action(self):
        state = self.get_state()
        action, strategy = self.basic_strategy()
        if not action:
            action = random.choice(self.get_possible_actions())
        reward = 0  # Placeholder reward

        # Update Q-value for the last action
        self.update_q_value(reward)
        # Record the current state and action for the next update
        self.last_state = state
        self.last_action = action
        self.step_count += 1
        self.moves.append((action, self.step_count))
        self.strategies.append((self.step_count, strategy))
        player_color = "Black" if self.game.current_player == 1 else "White"
        if strategy:
            print(f"{player_color} used {strategy} at step {self.step_count}")
        return action

    def reset_step_count(self):
        self.step_count = 0
        self.moves = []  # 重置记录每一步的位置和手数
        self.strategies = []  # 重置记录每一步使用的策略
