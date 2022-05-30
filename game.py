# Game class stores the information on the tic-tac-toe game
# it is passed through pickle to the client and server
class Game:
    def __init__(self):
        self.ready = 0
        self.player = [False,False]
        self.wins = [0, 0]
        self.ties = 0
        self.board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.turn = 1
        self.winner = -1

    # def play(self, player, move):
    #     self.moves[player] = move
    #     if player == 0:
    #         self.p1Went = True
    #     else:
    #         self.p2Went = True

    def valid_move(self, tup):
        if self.board[tup[0]][tup[1]] == 0:
            return True
        else:
            return False

    def connected(self):
        return self.ready

    def bothWent(self):
        return self.p1Went and self.p2Went

    # Implement tic-tac-toe logic
    def check_winner(self):
        self.winner = -1
        winnerlist = []
        countZero = 0
        # Check for vertical
        winnerlist.append(self.logicTest((0, 0), (1, 0), (2, 0)))
        winnerlist.append(self.logicTest((0, 1), (1, 1), (2, 1)))
        winnerlist.append(self.logicTest((0, 2), (1, 2), (2, 2)))

        # Check for horizontal
        winnerlist.append(self.logicTest((0, 0), (0, 1), (0, 2)))
        winnerlist.append(self.logicTest((1, 0), (1, 1), (1, 2)))
        winnerlist.append(self.logicTest((2, 0), (2, 1), (2, 2)))

        # Check for diagonal
        winnerlist.append(self.logicTest((0, 0), (1, 1), (2, 2)))
        winnerlist.append(self.logicTest((0, 2), (1, 1), (2, 0)))

        for i in winnerlist:
            if i == 1:
                self.winner = 1
                break
            if i == 2:
                self.winner = 2
        for i in self.board:
            for j in i:
                if j == 0:
                    countZero += 1

        if countZero == 0 and self.winner == -1:
            self.winner = 0

    def logicTest(self, tup1, tup2, tup3):
        if self.board[tup1[0]][tup1[1]] == self.board[tup2[0]][tup2[1]] == self.board[tup3[0]][tup3[1]] == 1:
            return 1
        elif self.board[tup1[0]][tup1[1]] == self.board[tup2[0]][tup2[1]] == self.board[tup3[0]][tup3[1]] == 2:
            return 2
        else:
            return -1

    def resetWent(self):
        self.p1Went = False
        self.p2Went = False

    def set_board(self, tup):
        # check even or odd to determine the player
        count = 0
        for x in self.board:
            for i in x:
                if i != 0:
                    count += 1
        player = 2
        if count % 2 == 0:
            player = 1
        self.board[tup[0]][tup[1]] = player
