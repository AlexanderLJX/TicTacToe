import threading

import pygame
import socket
from button import Button
from game import Game
import pickle
from random import randrange
from history import History
from copy import copy


class TicTacToe:
    def __init__(self):
        pygame.font.init()

        self.width = 600
        self.height = 600
        self.win = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Client")
        self.port = 5555

        # initialize buttons
        # Create button objects
        self.createButton = Button("New", 200, 200, (0, 0, 0))
        self.joinButton = Button("Join", 200, 350, (255, 0, 0))
        self.historyButton = Button("History", 200, 500, (0, 255, 0))
        self.acceptButton = Button("I'm ready!", 200, 500, (0, 0, 0))
        self.declineButton = Button("Decline", 200, 300, (255, 0, 0))
        self.backButton = Button("Back", 200, 500, (0, 0, 0))
        self.readyButton = Button("Ready", 200, 400, (255, 0, 0))
        # enterButton for the ip address
        self.enterButton = Button("Enter", 200, 350, (255, 0, 0))
        self.rematchButton = Button("Rematch!", 200, 350, (0, 0, 0))

        self.goToMenu = False

        # load history
        self.history = History()
        try:
            with open("data.pickle", "rb") as f:
                self.history = pickle.load(f)
        except Exception as ex:
            print("Error during unpickling object (Possibly unsupported):", ex)

        # ip address text box
        self.input_rect = pygame.Rect(200, 200, 140, 32)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        self.ipAddr = ip

        self.game = Game()
        self.ready = False
        self.user_text = ""
        self.winLoseText = ""
        self.playerNumber = -1
        self.opponentNumber = -1
        self.isServer = False
        self.sendGame = False
        self.sendReady = False
        self.sendReset = False
        self.sendClose = False
        self.connectionEstablished = False
        # ip address text box active
        self.active = False
        # ready flag for the initial ready handshake
        self.readyFlag = False
        self.moveFlag = False
        self.newScreenFlag = False
        self.gameEndFlag = False
        self.resetFlag = False
        # end the networking thread
        self.endThread = False
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

    def reset_variables(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        self.ipAddr = ip

        self.game = Game()
        self.ready = False
        self.user_text = ""
        self.winLoseText = ""
        self.playerNumber = -1
        self.opponentNumber = -1
        self.isServer = False
        self.sendGame = False
        self.sendReady = False
        self.sendReset = False
        self.sendClose = False
        self.connectionEstablished = False
        # ip address text box active
        self.active = False
        # ready flag for the initial ready handshake
        self.readyFlag = False
        self.moveFlag = False
        self.newScreenFlag = False
        self.gameEndFlag = False
        self.resetFlag = False
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

    def draw_waiting(self):
        # it will set background color of screen
        self.win.fill((255, 255, 255))
        if not self.readyFlag:
            font = pygame.font.SysFont("comicsans", 40)
            text = font.render("Click ready to start", 1, (255, 0, 0))
            self.win.blit(text, (100, 50))
            # Draw buttons
            self.readyButton.draw(self.win)
        else:
            # ready button disappear change to you are ready
            font = pygame.font.SysFont("comicsans", 40)
            text = font.render("Waiting for Opponent", 1, (255, 0, 0), True)
            self.win.blit(text, (self.width / 2 - text.get_width() / 2, self.height / 2 - text.get_height() / 2))

        pygame.display.update()

    def draw_waiting_rematch(self):
        # it will set background color of screen
        self.win.fill((255, 255, 255))
        # ready button disappear change to you are ready
        font = pygame.font.SysFont("comicsans", 40)
        text = font.render("Waiting for Opponent", 1, (255, 0, 0), True)
        self.win.blit(text, (self.width / 2 - text.get_width() / 2, self.height / 2 - text.get_height() / 2))

        pygame.display.update()

    # check_events sets flags in the buttonClicked dictionary
    def check_events(self):
        # To prevent mis-clicks when entering the new screen
        if self.newScreenFlag:
            self.newScreenFlag = False
            # pygame.time.delay(500)
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
                if self.readyFlag and self.game.turn == self.playerNumber:
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
                # end screen button
                # newButton
                if self.rematchButton.click(event.pos):
                    self.buttonClicked["rematchButton"] = True

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

    def draw_base(self):
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

    def draw_board(self):
        self.draw_base()

        # If there is a winner
        self.game.check_winner()
        if self.game.winner != -1:
            self.draw_base()
            pygame.time.delay(500)

            font = pygame.font.SysFont("comicsans", 90)
            if self.game.winner == self.playerNumber:
                text = font.render("You Win!", 1, (255, 0, 0))
                self.winLoseText = "You Win"
                self.history.add_win()
            elif self.game.winner == self.opponentNumber:
                text = font.render("You Lost...", 1, (255, 0, 0))
                self.winLoseText = "You lost"
                self.history.add_loss()
            elif self.game.winner == 0:
                text = font.render("Tie Game!", 1, (255, 0, 0))
                self.winLoseText = "It's a Tie"
                self.history.add_tie()
            # save history
            try:
                with open("data.pickle", "wb") as f:
                    pickle.dump(self.history, f, protocol=pickle.HIGHEST_PROTOCOL)
            except Exception as ex:
                print("Error during pickling object (Possibly unsupported):", ex)

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
            self.goToMenu = False
            clock = pygame.time.Clock()
            clock.tick(60)
            self.check_events()
            if self.buttonClicked["createButton"]:
                self.newScreenFlag = True
                print("creating new thread 195")
                # self.host_game(self.ipAddr, self.port)
                threading.Thread(target=self.host_game, args=(self.ipAddr, self.port)).start()
                while True:
                    # into the waiting screen
                    self.check_events()
                    if not self.connectionEstablished:
                        self.create_screen()
                        if self.buttonClicked["backButton"]:
                            # return to the main menu: reset the whole thing
                            self.reset_variables()
                            self.endThread = True
                            self.goToMenu = True
                            self.user_text = self.ipAddr
                            threading.Thread(target=self.connect_to_game, args=(self.port,)).start()
                            break
                    else:
                        break
                    if self.goToMenu:
                        break
                if self.goToMenu:
                    continue
                self.enter_game()
                if self.goToMenu:
                    continue
            if self.buttonClicked["joinButton"]:
                self.newScreenFlag = True
                while True:
                    self.join_screen()
                    self.check_events()
                    if self.buttonClicked["enterButton"] and self.user_text != "":
                        self.newScreenFlag = True
                        print("creating new thread 211")
                        # self.connect_to_game(self.port)
                        threading.Thread(target=self.connect_to_game, args=(self.port,)).start()
                        break
                    if self.buttonClicked["backButton"]:
                        # return to the main menu: reset the whole thing
                        self.reset_variables()
                        self.goToMenu = True
                        break
                if self.goToMenu:
                    continue
                while True:
                    # into the waiting screen
                    self.check_events()
                    if not self.connectionEstablished:
                        self.connecting_screen()
                    else:
                        break
                self.enter_game()
                if self.goToMenu:
                    continue

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

            # Draw buttons
            self.createButton.draw(self.win)
            self.joinButton.draw(self.win)
            self.historyButton.draw(self.win)

            pygame.display.update()

    def enter_game(self):
        while True:
            if self.goToMenu:
                break
            # Inside game lobby
            self.check_events()  # this must stay at the loop of the loop
            # if both players clicked reset
            if self.game.ready == 0:
                self.readyFlag = False
                self.resetFlag = False
                self.moveFlag = False
            if self.resetFlag:
                # if this player clicked reset, go into waiting screen
                self.draw_waiting_rematch()
                continue
            # check if game ended, then show the end screen
            if self.game.gameEnd:
                self.end_screen()
                if self.buttonClicked["rematchButton"] and self.resetFlag == False:
                    print("rematch button clicked")
                    # restart the game with the same connection
                    self.sendReset = True
                    self.resetFlag = True
                    self.readyFlag = False
                if self.buttonClicked["backButton"]:
                    # return to the main menu: reset the whole thing
                    if not self.isServer:
                        self.endThread = True
                    self.sendClose = True
                    self.goToMenu = True
                continue

            # if ready button is already pressed, skip the codes
            if not self.readyFlag:
                if self.buttonClicked["readyButton"]:
                    self.newScreenFlag = True
                    self.game.ready += 1
                    self.readyFlag = True
                    self.sendReady = True
            # if either player is not ready
            if self.game.ready < 2:
                self.draw_waiting()
            else:
                self.draw_board()
                self.game_logic()

    def game_logic(self):
        # game logic
        if self.playerNumber == self.game.turn and self.moveFlag:
            self.moveFlag = False
            if self.game.valid_move(self.lastMove):
                self.game.set_board(self.lastMove)
                self.sendGame = True
            else:
                print("Invalid move!")

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

        font = pygame.font.SysFont("comicsans", 40)
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

        font = pygame.font.SysFont("comicsans", 40)
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
        text = font.render("History", 1, (255, 0, 0))
        self.win.blit(text, (100, 50))

        # Wins
        font = pygame.font.SysFont("comicsans", 30)
        text = font.render("Wins : " + str(self.history.win), 1, (255, 0, 0))
        self.win.blit(text, (150, 200))
        # Loss
        font = pygame.font.SysFont("comicsans", 30)
        text = font.render("Losses : " + str(self.history.loss), 1, (255, 0, 0))
        self.win.blit(text, (150, 300))
        # Wins
        font = pygame.font.SysFont("comicsans", 30)
        text = font.render("Ties : " + str(self.history.tie), 1, (255, 0, 0))
        self.win.blit(text, (150, 400))

        # Draw buttons
        self.backButton.draw(self.win)

        pygame.display.update()

    # Displays win or lose, allows player to rematch, or back to main menu
    def end_screen(self):
        # it will set background color of screen
        self.win.fill((255, 255, 255))

        font = pygame.font.SysFont("comicsans", 60)
        text = font.render(self.winLoseText, 1, (255, 0, 0))
        self.win.blit(text, (100, 50))

        # Draw buttons
        self.backButton.draw(self.win)
        self.rematchButton.draw(self.win)

        pygame.display.update()

    def host_game(self, host, port):
        self.isServer = True

        # # the problem is that if you start out as the second player the other player won't know
        # if self.playerNumber == 2:
        #     self.sendGame = True
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen()

        while not self.connectionEstablished:
            try:
                client, addr = server.accept()
                self.connectionEstablished = True
            except:
                self.connectionEstablished = False
        # close the server since you only want one client to connect
        server.close()
        # print("creating new thread 379")
        # threading.Thread(target=self.handle_server_connection, args=(client,)).start()
        self.handle_server_connection(client)
        print("server thread ended")

    def connect_to_game(self, port):
        self.isServer = False
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((self.user_text, port))
            self.connectionEstablished = True
        except:
            self.connectionEstablished = False

        # print("creating new thread 393")
        # threading.Thread(target=self.handle_client_connection, args=(client,)).start()
        self.handle_client_connection(client)
        print("client thread ended")

    def handle_server_connection(self, conn):
        # listening in while loop for the other client that sends back the game object
        # the client can send get ready or reset
        while True:
            if self.game.gameStart:
                self.game.gameStart = False
                # set player numbers because you are the server
                self.playerNumber = randrange(2) + 1
                if self.playerNumber == 1:
                    self.opponentNumber = 2
                    self.game.opponentIsPlayer = 2
                else:
                    self.opponentNumber = 1
                    self.game.opponentIsPlayer = 1
            if self.endThread:
                self.endThread = False
                break
            data = conn.recv(512).decode()
            if not data:
                print("if not data")
                break
            else:
                if data == "get":
                    pass
                elif data == "ready":
                    # set game opponent ready true
                    self.game.ready += 1
                elif data == "reset":
                    # set game opponent reset true
                    newGame = copy(self.game)
                    newGame.reset += 1
                    self.game.reset += 1
                    conn.sendall(pickle.dumps(newGame))
                    continue
                elif data == "close":
                    # set game opponent reset true
                    self.game.close = True
                else:
                    # load the tuple object
                    # need to validate input?
                    self.game.set_board(tuple(map(int, data.split(","))))
                    # increment turn
                    if self.game.turn == 1:
                        self.game.turn = 2
                    else:
                        self.game.turn = 1
                if self.sendReset:
                    print("send reset")
                    self.sendReset = False
                    newGame = copy(self.game)
                    newGame.reset += 1
                    self.game.reset += 1
                    conn.sendall(pickle.dumps(newGame))
                    continue
                if self.sendClose:
                    print("send close")
                    self.sendClose = False
                    self.game.close = True
                # check if game closed
                if self.game.close:
                    print("game closed")
                    break
                if self.game.reset > 1:
                    print("game reset")
                    self.game = Game()
                if self.sendGame:
                    self.sendGame = False
                    # switch the game turn
                    if self.game.turn == 1:
                        self.game.turn = 2
                    else:
                        self.game.turn = 1
                conn.sendall(pickle.dumps(self.game))
        print("Lost connection host")
        conn.close()
        self.reset_variables()
        self.goToMenu = True

        # changes to object is made locally
        # server validates whether the changes made by the client is legal else return invalid

    def handle_client_connection(self, conn):
        # constantly send and wait to receive from the server
        # if game object equal None send 'get' to the server
        while True:
            if self.endThread:
                self.endThread = False
                break
            if self.sendReady:
                self.sendReady = False
                try:
                    conn.send(str.encode("ready"))
                except socket.error as e:
                    print(e)
            elif self.sendReset:
                self.sendReset = False
                try:
                    conn.send(str.encode("reset"))
                except socket.error as e:
                    print(e)
            elif self.sendClose:
                print("send close")
                self.sendClose = False
                try:
                    conn.send(str.encode("close"))
                except socket.error as e:
                    print(e)
            elif self.sendGame:
                self.sendGame = False
                try:
                    conn.send(str.encode(str(self.lastMove[0]) + "," + str(self.lastMove[1])))
                except socket.error as e:
                    print(e)
            else:
                try:
                    conn.send(str.encode("get"))
                except socket.error as e:
                    print(e)
            try:
                data = pickle.loads(conn.recv(2048 * 2))
            except:
                break
            self.game = data
            # You have received from the other client
            if self.game.opponentIsPlayer == 1:
                self.playerNumber = 1
                self.opponentNumber = 2
            else:
                self.playerNumber = 2
                self.opponentNumber = 1
        print("Lost connection client")
        conn.close()
        self.reset_variables()
        self.goToMenu = True

tic = TicTacToe()
tic.menu_screen()
