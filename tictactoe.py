import threading

import pygame
import socket
from button import Button
from game import Game
import pickle
from random import randrange


class TicTacToe:
    def __init__(self):
        pygame.font.init()

        self.width = 600
        self.height = 600
        self.win = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Client")
        self.ready = False
        self.port = 5555

        # initialize buttons
        # Create button objects
        self.createButton = Button("New", 200, 200, (0, 0, 0))
        self.joinButton = Button("Join", 200, 350, (255, 0, 0))
        self.historyButton = Button("History", 200, 500, (0, 255, 0))
        self.game = Game()
        self.hostname = socket.gethostname()
        self.ipAddr = socket.gethostbyname(self.hostname)
        self.acceptButton = Button("I'm ready!", 200, 500, (0, 0, 0))
        self.declineButton = Button("Decline", 200, 300, (255, 0, 0))
        self.backButton = Button("Back", 250, 500, (0, 0, 0))
        self.readyButton = Button("Ready", 250, 500, (255, 0, 0))
        # enterButton for the ip address
        self.enterButton = Button("Enter", 250, 400, (255, 0, 0))
        # ip address text box
        self.input_rect = pygame.Rect(200, 200, 140, 32)
        self.user_text = ""
        self.playerNumber = -1
        self.opponentNumber = -1
        self.sendGame = False
        self.connectionEstablished = False
        # ip address text box active
        self.active = False
        # ready flag for the initial ready handshake
        self.readyFlag = False
        self.receivedFlag = False
        self.moveFlag = False
        self.newScreenFlag = False
        self.lastMove = [0, 0]
        self.buttonClicked = {"createButton": False,
                              "joinButton": False,
                              "historyButton": False,
                              "backButton": False,
                              "acceptButton": False,
                              "declineButton": False,
                              "ipaddressButton": False,
                              "readyButton": False,
                              "rematchButton": False,
                              "enterButton": False,
                              }
        self.playerNumber = randrange(2)
        self.game.player[self.playerNumber - 1] = True
        if self.playerNumber == 1:
            self.opponentNumber = 2
        else:
            self.opponentNumber = 1

    def draw_waiting(self):
        # it will set background color of screen
        self.win.fill((255, 255, 255))
        if not self.readyFlag:
            font = pygame.font.SysFont("comicsans", 60)
            text = font.render("Click ready to start", 1, (255, 0, 0))
            self.win.blit(text, (100, 50))
            # Draw buttons
            self.readyButton.draw(self.win)
        else:
            # ready button disappear change to you are ready
            font = pygame.font.SysFont("comicsans", 60)
            text = font.render("Waiting for Opponent", 1, (255, 0, 0), True)
            self.win.blit(text, (self.width / 2 - text.get_width() / 2, self.height / 2 - text.get_height() / 2))

        pygame.display.update()

    # check_events sets flags in the buttonClicked dictionary
    def check_events(self):
        print(self.buttonClicked)
        # Reset all flags in buttonClicked to False
        for key, value in self.buttonClicked.items():
            self.buttonClicked[key] = False
        # Check if ready button is clicked
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.user_text = self.user_text[:-1]
                else:
                    self.user_text += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.game.turn == self.playerNumber:
                    self.user_click()
                    self.moveFlag = True
                # ip address text box
                clicked = False
                if self.input_rect.collidepoint(event.pos):
                    self.active = True
                else:
                    self.active = False
                # ready screen buttons
                # newButton
                if self.acceptButton.click(event.pos):
                    self.buttonClicked["acceptButton"] = True
                # newButton
                if self.declineButton.click(event.pos):
                    self.buttonClicked["declineButton"] = True
                # main menu buttons
                # newButton
                if self.createButton.click(event.pos):
                    self.buttonClicked["createButton"] = True
                # newButton
                if self.joinButton.click(event.pos):
                    self.buttonClicked["joinButton"] = True
                # newButton
                if self.historyButton.click(event.pos):
                    self.buttonClicked["historyButton"] = True
                # create screen buttons
                # newButton
                if self.backButton.click(event.pos):
                    self.buttonClicked["backButton"] = True
                # waiting screen buttons
                # newButton
                if self.readyButton.click(event.pos):
                    self.buttonClicked["readyButton"] = True
                # join screen buttons
                # newButton
                if self.enterButton.click(event.pos):
                    self.buttonClicked["enterButton"] = True

    def user_click(self):
        # get coordinates of mouse click
        x, y = pygame.mouse.get_pos()
        # get column of mouse click (1-3)
        col = -1
        if (x < self.width / 3):
            col = 0
        elif (x < self.width / 3 * 2):
            col = 1
        elif (x < self.width):
            col = 2
        # get row of mouse click (1-3)
        row = -1
        if (y < self.height / 3):
            row = 0
        elif (y < self.height / 3 * 2):
            row = 1
        elif (y < self.height):
            row = 2
        self.lastMove = [col, row]

    def draw_board(self):
        # Normal board
        self.win.fill((128, 128, 128))
        font = pygame.font.SysFont("comicsans", 60)
        if self.game.turn == self.playerNumber:
            text = font.render("Your Turn", 1, (0, 255, 255))
            self.win.blit(text, (100, 200))
        else:
            text = font.render("Opponent's Turn", 1, (0, 255, 255))
            self.win.blit(text, (80, 200))

        # draw the tictactoe hexes
        pygame.draw.line(self.win, (0, 0, 0), (self.width / 3, 0), (self.width / 3, self.height), 7)
        pygame.draw.line(self.win, (0, 0, 0), (self.width / 3 * 2, 0), (self.width / 3 * 2, self.height), 7)

        # drawing horizontal lines
        pygame.draw.line(self.win, (0, 0, 0), (0, self.height / 3), (self.width, self.height / 3), 7)
        pygame.draw.line(self.win, (0, 0, 0), (0, self.height / 3 * 2), (self.width, self.height / 3 * 2), 7)

        # draw X and O s
        for i in range(3):
            for j in range(3):
                if self.game.board[i][j] == 1:
                    text = font.render("O", 1, (0, 255, 255))
                    self.win.blit(text, ((self.width / 3) * (i + 0.5), (self.height / 3) * (j + 0.5)))
                elif self.game.board[i][j] == 2:
                    text = font.render("X", 1, (0, 255, 255))
                    self.win.blit(text, ((self.width / 3) * (i + 0.5), (self.height / 3) * (j + 0.5)))

        pygame.display.update()

        # If there is a winner
        self.game.check_winner()
        if self.game.winner != -1:
            pygame.time.delay(500)

            font = pygame.font.SysFont("comicsans", 90)
            if self.game.winner == self.playerNumber:
                text = font.render("You Won!", 1, (255, 0, 0))
            elif self.game.winner == self.opponentNumber:
                text = font.render("You Lost...", 1, (255, 0, 0))
            else:
                text = font.render("Tie Game!", 1, (255, 0, 0))

            self.win.blit(text, (self.width / 2 - text.get_width() / 2, self.height / 2 - text.get_height() / 2))
            pygame.display.update()
            pygame.time.delay(2000)

    # def check_connection(self, conn):
    #     try:
    #         game = conn.send("get")
    #         return True
    #     except:
    #         run = False
    #         print("Couldn't get game")
    #         return False

    def menu_screen(self):
        while True:
            clock = pygame.time.Clock()
            clock.tick(60)
            self.check_events()
            if self.buttonClicked["createButton"]:
                self.newScreenFlag = True
                print("creating new thread 195")
                threading.Thread(target=self.host_game, args=(self.ipAddr, self.port)).start()
                while True:
                    # into the waiting screen
                    self.check_events()
                    if not self.connectionEstablished:
                        self.create_screen()
                    else:
                        break
                self.enter_game()
            if self.buttonClicked["joinButton"]:
                self.newScreenFlag = True
                while True:
                    self.join_screen()
                    self.check_events()
                    if self.buttonClicked["enterButton"] and self.user_text != "":
                        self.newScreenFlag = True
                        print("creating new thread 211")
                        threading.Thread(target=self.connect_to_game, args=(self.port,)).start()
                        break
                while True:
                    # into the waiting screen
                    self.check_events()
                    if not self.connectionEstablished:
                        self.connecting_screen()
                    else:
                        break
                self.enter_game()

            if self.buttonClicked["historyButton"]:
                self.newScreenFlag = True
                while True:
                    self.check_events()
                    self.history_screen()
                    if self.buttonClicked["backButton"]:
                        break

            # it will set background color of screen
            self.win.fill((255, 255, 255))

            font = pygame.font.SysFont("comicsans", 60)
            text = font.render("Main Menu", 1, (255, 0, 0))
            self.win.blit(text, (150, 50))

            # # Draw buttons
            self.createButton.draw(self.win)
            self.joinButton.draw(self.win)
            self.historyButton.draw(self.win)

            pygame.display.update()

    def enter_game(self):
        while True:
            # Inside game lobby
            self.check_events()
            # if ready button is already pressed, skip the codes
            if not self.readyFlag:
                if self.buttonClicked["readyButton"]:
                    self.newScreenFlag = True
                    self.game.ready += 1
                    self.readyFlag = True
            # if either player is not ready
            if self.game.ready < 2:
                self.draw_waiting()
                continue
            self.draw_board()

    def connecting_screen(self):
        # it will set background color of screen
        self.win.fill((255, 255, 255))
        # ready button disappear change to you are ready
        font = pygame.font.SysFont("comicsans", 60)
        text = font.render("Waiting for Connection", 1, (255, 0, 0), True)
        self.win.blit(text, (self.width / 2 - text.get_width() / 2, self.height / 2 - text.get_height() / 2))

        pygame.display.update()

    # Create screen displays the ip address
    def create_screen(self):
        # it will set background color of screen
        self.win.fill((255, 255, 255))

        font = pygame.font.SysFont("comicsans", 60)
        text = font.render("Waiting for player...", 1, (255, 0, 0))
        self.win.blit(text, (100, 50))

        # Draw IP address
        font = pygame.font.SysFont("comicsans", 30)
        text = font.render("Your IP : " + self.ipAddr, 1, (255, 0, 0))
        self.win.blit(text, (150, 200))

        # Draw buttons
        self.backButton.draw(self.win)

        pygame.display.update()

    def join_screen(self):
        # it will set background color of screen
        self.win.fill((255, 255, 255))

        font = pygame.font.SysFont("comicsans", 60)
        text = font.render("Enter ip address:", 1, (255, 0, 0))
        self.win.blit(text, (100, 50))

        # Draw IP address text box
        base_font = pygame.font.Font(None, 32)

        color_active = pygame.Color('lightskyblue3')
        color_passive = pygame.Color('chartreuse4')
        color = color_passive
        if self.active:
            color = color_active
        else:
            color = color_passive
        pygame.draw.rect(self.win, color, self.input_rect)
        text_surface = base_font.render(self.user_text, True, (255, 255, 255))
        self.win.blit(text_surface, (self.input_rect.x + 5, self.input_rect.y + 5))
        self.input_rect.w = max(100, text_surface.get_width() + 10)

        # Draw buttons
        self.backButton.draw(self.win)
        self.enterButton.draw(self.win)

        pygame.display.update()

    def history_screen(self):
        # it will set background color of screen
        self.win.fill((255, 255, 255))

        font = pygame.font.SysFont("comicsans", 60)
        text = font.render("Waiting for player...", 1, (255, 0, 0))
        self.win.blit(text, (100, 50))

        # Draw IP address
        font = pygame.font.SysFont("comicsans", 30)
        text = font.render("Your IP : " + self.ipAddr, 1, (255, 0, 0))
        self.win.blit(text, (150, 200))

        # Draw buttons
        self.backButton.draw(self.win)

        pygame.display.update()

    # Displays win or lose, allows player to rematch, or back to main menu
    def end_screen(self):
        while True:
            # Define Buttons
            rematchButton = Button("Rematch!", 200, 500, (0, 0, 0))
            menuButton = Button("Main Menu", 200, 300, (255, 0, 0))
            # Check Button clicks
            for event in pygame.event.get():

                # if user types QUIT then the screen will close
                if event.type == pygame.QUIT:
                    pygame.quit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if rematchButton.click():
                        # Check if both players click rematch
                        # Change button text to accepted
                        pass
                    if menuButton.click():
                        # Decline the game for both players, return both to the main menu
                        pass
            # Draw buttons

            pass

    def host_game(self, host, port):
        # # the problem is that if you start out as the second player the other player won't know
        # if self.playerNumber == 2:
        #     self.sendGame = True
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen()

        try:
            client, addr = server.accept()
            self.connectionEstablished = True
        except:
            self.connectionEstablished = False
        print("creating new thread 379")
        threading.Thread(target=self.handle_connection, args=(client,)).start()
        # close the server since you only want one client to connect
        server.close()

    def connect_to_game(self, port):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                client.connect((self.user_text, port))
                self.connectionEstablished = True
                break
            except:
                self.connectionEstablished = False
        print("creating new thread 393")
        threading.Thread(target=self.handle_connection, args=(client,)).start()

    def handle_connection(self, conn):
        print("creating new thread 397")
        threading.Thread(target=self.background_recv, args=(conn,)).start()
        while True:
            if self.readyFlag:
                if self.game.player[0] == False and self.game.player[1] == False:
                    # You are the one to decide and send the player numbers
                    self.game.player[self.playerNumber - 1] = True
                    print(self.game.player)
                else:
                    # You have received from the other client
                    if not self.game.player[0]:
                        self.game.player[0] = True
                        self.playerNumber = 1
                        self.opponentNumber = 2
                    else:
                        self.game.player[0] = False
                        self.playerNumber = 2
                        self.opponentNumber = 1
                conn.sendall(pickle.dumps(self.game))
                break
        while True:
            # if game.turn is current player turn allow the edit of the game object
            if self.playerNumber == self.game.turn:
                # move flag means player entered an action
                if not self.moveFlag:
                    continue
                self.moveFlag = False
                if self.game.valid_move(self.lastMove):
                    self.game.set_board(self.lastMove)
                    # switch the game turn
                    if self.game.turn == 1:
                        self.game.turn = 2
                    else:
                        self.game.turn = 1
                    conn.sendall(pickle.dumps(self.game))
                else:
                    print("Invalid move!")
            else:
                # if sendGame is true send the game object to the client
                if self.sendGame:
                    self.sendGame = False
                    conn.sendall(pickle.dumps(self.game))
                # receive data from the opponent
                data = pickle.loads(conn.recv(2048 * 2))
                if not data:
                    break
                else:
                    self.game = data
                    # set player number - derived from turn
                    # if self.playerNumber == -1:
                    #     self.playerNumber = self.game.turn
                    #     if self.playerNumber == 1:
                    #         self.opponentNumber = 2
                    #     else:
                    #         self.opponentNumber = 1

        conn.close()

    # This receive method can either receive ready = 2 and player=1,1 OR receive ready = 1 and player=0,1
    def background_recv(self, conn):
        # receive data from the opponent
        data = pickle.loads(conn.recv(2048 * 2))
        if not data:
            return
        else:
            self.receivedFlag = True
            print("data received")
            self.game = data
            # if returned is half empty set: configure your playerNumber accordingly
            if self.game.ready == 1:
                if not self.game.player[0]:
                    self.playerNumber = 1
                else:
                    self.playerNumber = 2
                if self.playerNumber == 1:
                    self.opponentNumber = 2
                else:
                    self.opponentNumber = 1
        print("background thread ended")


tic = TicTacToe()
tic.menu_screen()
