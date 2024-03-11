"""
Tic Tac Toe Player
"""

import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    countX = countO = 0
    for i in board:
        for j in i:
            if j==X: countX+=1
            elif j==O: countO+=1
    if countX==0: return X
    elif countX>countO: return O
    elif countO==countX: return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = set()
    for i in range(3):
        for j in range(3):
            if board[i][j]==EMPTY: 
                actions.add((i,j))
    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    if action not in actions(board):
        raise Exception("Invalid Action!")
    
    new_board = [row[:] for row in board]
    new_board[action[0]][action[1]] = player(board)
    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Horizontal Winners
    for i in board:
        if i[0]==i[1]==i[2] and i[0] != EMPTY:
            return i[0]
    
    # Vertical Winners
    for i in range(3):
        if board[0][i]==board[1][i]==board[2][i] and board[0][i] != EMPTY:
            return board[0][i]
    
    #Diagonal Winners 
    if board[0][0]==board[1][1]==board[2][2] and board[0][0] != EMPTY:
        return board[0][0]
    elif board[2][0]==board[1][1]==board[0][2] and board[2][0] != EMPTY:
        return board[2][0]


    # Otherwise, return none
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None: return True

    for row in board:
        if EMPTY in row: return False

    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    winning_player = winner(board)
    if winning_player==X: return 1
    elif winning_player==O: return -1
    else: return 0

def minValue(board):
    if terminal(board): return utility(board)
    v=float("inf")

    for action in actions(board):
        v=min(v,maxValue(result(board, action)))
    return v

def maxValue(board):
    if terminal(board): return utility(board)
    v=float("-inf")

    for action in actions(board):
        v=max(v,minValue(result(board, action)))
    return v

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board): return None

    # Maximising player
    if player(board) == X:
        bestAction = None
        bestValue = float("-inf")
        for action in actions(board):
            v = minValue(result(board, action))
            if v>bestValue:
                bestAction = action   
                bestValue = v  

    # Minimising player
    else:
        bestAction = None
        bestValue = float("inf")
        for action in actions(board):
            v = maxValue(result(board, action))
            if v<bestValue:
                bestAction = action   
                bestValue = v  

    return bestAction

