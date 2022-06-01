# history class is to store the match history

class History:
    def __init__(self):
        self.win = 0
        self.loss = 0
        self.tie = 0

    def add_win(self):
        self.win += 1

    def add_loss(self):
        self.loss += 1

    def add_tie(self):
        self.tie += 1
