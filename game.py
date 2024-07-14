import json
import copy  
import math  
import logging

logging.basicConfig(format='%(levelname)s - %(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',
                    level=logging.INFO)

# Mapping from histories (str) to probability distribution over actions
strategy_dict_x = {}
strategy_dict_o = {}


class History:
    def __init__(self, history=None):
        """
        # self.history : Eg: [0, 4, 2, 5]
            keeps track of sequence of actions played since the beginning of the game.
            Each action is an integer between 0-8 representing the square in which the move will be played as shown
            below.
              ___ ___ ____
             |_0_|_1_|_2_|
             |_3_|_4_|_5_|
             |_6_|_7_|_8_|

        # self.board
            empty squares are represented using '0' and occupied squares are either 'x' or 'o'.
            Eg: ['x', '0', 'x', '0', 'o', 'o', '0', '0', '0']
            for board
              ___ ___ ____
             |_x_|___|_x_|
             |___|_o_|_o_|
             |___|___|___|

        # self.player: 'x' or 'o'
            Player whose turn it is at the current history/board

        :param history: list keeps track of sequence of actions played since the beginning of the game.
        """
        if history is not None:
            self.history = history
            self.board = self.get_board()
        else:
            self.history = []
            self.board = ['0', '0', '0', '0', '0', '0', '0', '0', '0']
        self.player = self.current_player()

    def current_player(self):
        """ Player function
        Get player whose turn it is at the current history/board
        :return: 'x' or 'o' or None
        """
        total_num_moves = len(self.history)
        if total_num_moves < 9:
            if total_num_moves % 2 == 0:
                return 'x'
            else:
                return 'o'
        else:
            return None

    def get_board(self):
        """ Play out the current self.history and get the board corresponding to the history in self.board.

        :return: list Eg: ['x', '0', 'x', '0', 'o', 'o', '0', '0', '0']
        """
        board = ['0', '0', '0', '0', '0', '0', '0', '0', '0']
        for i in range(len(self.history)):
            if i % 2 == 0:
                board[self.history[i]] = 'x'
            else:
                board[self.history[i]] = 'o'
        return board

    def is_win(self):
        # check if the board position is a win for either players
        board = self.board
        if board[0] == board[1] == board[2] != '0':
            return True
        if board[3] == board[4] == board[5] != '0':
            return True
        if board[6] == board[7] == board[8] != '0':
            return True
        if board[0] == board[3] == board[6] != '0':
            return True
        if board[1] == board[4] == board[7] != '0':
            return True
        if board[2] == board[5] == board[8] != '0':
            return True
        if board[0] == board[4] == board[8] != '0':
            return True
        if board[2] == board[4] == board[6] != '0':
            return True
        return False

    def is_draw(self):
        # check if the board position is a draw
        board = self.board
        if '0' not in board:
            if not self.is_win():
                return True
        return False

    def get_valid_actions(self):
        # get the empty squares from the board
        valid_actions = []
        for i in range(9):
            if self.board[i] == '0':
                valid_actions.append(i)
        return valid_actions

    def is_terminal_history(self):
        # check if the history is a terminal history
        if self.is_win() or self.is_draw():
            return True

    def get_utility_given_terminal_history(self):
        if self.is_win():
            if self.player == 'x':
                return 10
            else:
                return -10
        else:
            return 0

    def update_history(self, action):
        hist = copy.deepcopy(self.history)
        hist.append(action)
        self.history = hist


def backward_induction(history_obj):
    """
    :param history_obj: Histroy class object
    :return: best achievable utility (float) for th current history_obj
    """
    global strategy_dict_x, strategy_dict_o
    if history_obj.is_terminal_history():
        return history_obj.get_utility_given_terminal_history()
    else:
        if history_obj.player == 'x':
            best_utility = math.inf
            best_action = None
            for action in history_obj.get_valid_actions():
                history_obj.update_history(action)
                history_obj.board = history_obj.get_board()
                history_obj.player = 'o'
                utility = backward_induction(history_obj)
                if utility < best_utility:
                    best_utility = utility
                    best_action = action
                history_obj.history.pop()
            history_str = "".join([str(x) for x in history_obj.history])
            if history_str not in strategy_dict_x:
                strategy_dict_x[history_str] = {}
            for i in range(9):
                if i == best_action:
                    strategy_dict_x[history_str][str(i)] = 1
                else:
                    strategy_dict_x[history_str][str(i)] = 0
            return best_utility
        else:
            best_utility = -math.inf
            best_action = None
            for action in history_obj.get_valid_actions():
                history_obj.update_history(action)
                history_obj.board = history_obj.get_board()
                history_obj.player = 'x'
                utility = backward_induction(history_obj)
                if utility > best_utility:
                    best_utility = utility
                    best_action = action
                history_obj.history.pop()
            history_str = "".join([str(x) for x in history_obj.history])
            if history_str not in strategy_dict_o:
                strategy_dict_o[history_str] = {}
            for i in range(9):
                if i == best_action:
                    strategy_dict_o[history_str][str(i)] = 1
                else:
                    strategy_dict_o[history_str][str(i)] = 0
            return best_utility

def solve_tictactoe():
    backward_induction(History())
    with open('./policy_x.json', 'w') as f:
        json.dump(strategy_dict_x, f)
    with open('./policy_o.json', 'w') as f:
        json.dump(strategy_dict_o, f)
    return strategy_dict_x, strategy_dict_o


if __name__ == "__main__":
    logging.info("Start")
    solve_tictactoe()
    logging.info("End")
