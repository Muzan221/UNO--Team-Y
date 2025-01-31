from tkinter import *
from random import choice
from PIL import Image, ImageTk

col = "lightgoldenrodyellow"

root = Tk()
root.geometry("1500x750")
root.resizable(False, False)
root.wm_attributes('-transparentcolor', "orange")
root.configure(bg=col)
root.title("Uno")

folder = "Uno_cards"

images = {
    "Red": ImageTk.PhotoImage(Image.open(f"{folder}/Red.png").convert("RGBA").rotate(45)),
    "Green": ImageTk.PhotoImage(Image.open(f"{folder}/Green.png").convert("RGBA").rotate(45)),
    "Yellow": ImageTk.PhotoImage(Image.open(f"{folder}/Yellow.png").convert("RGBA").rotate(45)),
    "Blue": ImageTk.PhotoImage(Image.open(f"{folder}/Blue.png").convert("RGBA").rotate(45)),
    "Deck": ImageTk.PhotoImage(file=f"{folder}/Deck.png"),
    "UNO": ImageTk.PhotoImage(file=f"{folder}/Logo.png"), 
    "UNO_Button": ImageTk.PhotoImage(file=f"{folder}/UnoButton.png"),
    "Start": ImageTk.PhotoImage(file=f"{folder}/startButton.png")
    }

bgCols = {
    "Red": "#802019",
    "Purple": "#48406A",
    "Green": "#23863F",
    "Blue": "#40686A"
    }


mainBg = bgCols["Purple"]
cards = ["Wild", "Wild_Draw", "Skip", "Draw", "Reverse"] + [str(n) for n in range(10)]

canvas = Canvas(root, width=1126, height=700, bg=mainBg)
canvas.place(relx=0.225,rely=0.5, anchor="w")
            
colourPicker = {"Red": canvas.create_image(int(canvas["width"])/2+250, int(canvas["height"])/2-100,image=images["Red"], state="hidden"),
                "Yellow": canvas.create_image(int(canvas["width"])/2+180, int(canvas["height"])/2-30,image=images["Yellow"], state="hidden"), 
                "Blue": canvas.create_image(int(canvas["width"])/2+320, int(canvas["height"])/2-30,image=images["Blue"], state="hidden"), 
                "Green": canvas.create_image(int(canvas["width"])/2+250, int(canvas["height"])/2+40,image=images["Green"], state="hidden") 
                }

class Card():
    def __init__(self, name, displayName, colour, cardType, worth):      
        self.name = name
        self.colour = colour
        self.cardType = cardType
        self.worth = worth
        self.animating = True
        self.up = False
        self.displayName = displayName
        self.time = 100
        #print(name, colour, cardType)
        self.rawImage = Image.open(f"{folder}/{name}.png").convert("RGBA")
        self.backRaw = Image.open(f"{folder}/Back.png").convert("RGBA")
        self.storedImage = ImageTk.PhotoImage(self.rawImage)
        self.main = canvas.create_image(int(canvas["width"])/2+self.storedImage.width(), int(canvas["height"])/2, image=self.storedImage, state="hidden")

    def disable(self):
        canvas.tag_unbind(self.main, "<1>")
        
    def RightToCentre(self): 
        self.backImage = ImageTk.PhotoImage(self.backRaw.rotate(90, expand=True))
        canvas.itemconfig(self.main, image=self.backImage)
        self.disable()

    def LeftToCentre(self):
        self.backImage = ImageTk.PhotoImage(self.backRaw.rotate(-90, expand=True))
        canvas.itemconfig(self.main, image=self.backImage)
        self.disable()

    def Reverse(self):
        self.backImage = ImageTk.PhotoImage(self.backRaw.rotate(180))
        canvas.itemconfig(self.main, image=self.backImage)
        self.disable()

    def Normal(self):
        canvas.itemconfig(self.main, image=self.storedImage)
        canvas.tag_bind(self.main, "<1>", self.attemptCardUsage)

    def animateUp(self):
        if self.animating: return
        self.animating = True
        base = canvas.coords(self.main)
        animateWidgetMovement(self.main, base[0], base[1]-self.storedImage.height()/2, self.time)
        root.after(self.time, self.toggleUp, True)

    def animateDown(self):
        if self.animating: return
        self.animating = True
        base = canvas.coords(self.main)
        animateWidgetMovement(self.main, base[0], base[1]+self.storedImage.height()/2, self.time)
        root.after(self.time, self.toggleUp, False)

    def toggleUp(self, val):
        self.up = val
        self.animating = False
        
        
    def isUsable(self):
        if not game.started:
            game.log.output("Game has not started yet!")
            return False
        elif self.name.find("Wild") > -1 or self.colour == game.deck.lastCardUsed.colour or self.cardType == game.deck.lastCardUsed.cardType:
            return True
        
    def attemptCardUsage(self, event):
        if self.isUsable() and game.turnNumber == 0 and not game.pickingColour:
            self.use(game.user)

    def use(self, player):
        game.log.output(f"{player.name} played {self.displayName}")
        for i, cardObj in enumerate(player.hand):
            if cardObj == self:
                player.hand.pop(i)
                player.visualiseHand(len(player.hand))
                break
        game.deck.updateLastUsed(self)
        if len(player.hand) == 1 :
            if game.uno:
                game.log.output(f"{player.name}: UNO!")
            else:
                game.log.output(f"{player.name} HaHa! failed to say UNO! Drawing 2 cards as punishment.")
                player.draw(2)
        incrementTurn = True
        if self.cardType == "Reverse":
            if game.playerCount == 2:
                game.skipNext = True
            else:
                game.increment *= -1
        elif self.cardType == "Skip":
            game.skipNext = True
        elif self.cardType == "Draw":
            game.skipNext = True
            game.turnList[game.simplifyTurnNumber(False, game.increment)].draw(2)
        elif self.cardType == "Wild":
            if self.name == "Wild_Draw":
                legal = True
                for cardObj in player.hand:
                    if cardObj.colour == game.deck.usedPile[-1].colour and cardObj.cardType != "Wild": # Illegal!!
                        legal = False
                        break
                if legal:
                    game.skipNext = True                   
                    game.turnList[game.simplifyTurnNumber(False, game.increment)].draw(4)
                else:
                    game.log.output("Illegal Wild Draw 4 played. User will draw 4 cards as punishment")
                    player.draw(4)
            if player == game.user and len(player.hand) > 0:
                game.pickingColour = True
                toggleColourPicker("normal")
            incrementTurn = False

        if len(player.hand) == 0:
            totalScore = 0
            for plr in game.players:
                for cardObj in plr.hand:
                    totalScore += cardObj.worth
                    game.deck.cards.append(cardObj)
                plr.hand = []
            game.log.output(f"{player.name} won, scoring {totalScore} points!")
            if player == game.user:
                game.log.output("Congratulations!")
            else:
                game.log.output("Better luck next time!")
                
            game.deck.cards += game.deck.usedPile
            game.deck.usedPile = []
            game.deck.cards.append(game.deck.lastCardUsed)
            game.deck.lastCardUsed = None

            for cardObj in game.deck.cards:
                canvas.itemconfig(cardObj.main, state="hidden")
                canvas.coords(cardObj.main,int(canvas["width"])/2+self.storedImage.width(), int(canvas["height"])/2) 

            game.deck.main.place_forget()
            
            canvas.itemconfig(game.unoButton, state="hidden")
            
            game.displayTitleScreen(True)
            
        elif incrementTurn:
            game.incTurn()


class Deck():
    def __init__(self):
        self.cards = []
        self.usedPile = []
        self.lastCardUsed = None
        for colour in ["Yellow", "Red", "Green", "Blue"]:
            for cardType in cards:
                name = f"{colour}_{cardType}"
                displayName = f"{colour} {cardType}"
                times = 1
                if len(cardType) == 1: 
                    worth = int(cardType)
                    if cardType != "0":
                        times = 2
                elif cardType.find("Wild") > -1: 
                    worth = 50
                    name = cardType
                    cardType = "Wild"
                    if name == "Wild_Draw":
                        displayName = "Wild Draw 4"
                    else:
                        displayName = "Wild Card"
                else: 
                    worth = 20
                    times = 2
                self.cards.append(Card(name, displayName, colour, cardType, worth))
                if times == 2:
                    self.cards.append(Card(name, displayName, colour, cardType, worth))

        self.cardHeight = self.cards[0].storedImage.height() + 2
        self.cardWidth = self.cards[0].storedImage.width() + 2
        self.main = Label(canvas, image=images["Deck"], bg=mainBg)
        self.main.bind("<1>", self.drawAttempted)

    def shuffle(self):
        try:
            from random import shuffle
            shuffle(self.cards)
            game.log.output(f"Deck successfully shuffled! {len(self.cards)} cards remaining!")
        except Exception as e:
            game.log.output(f"Failed to shuffle deck:\n\n {e}", error=True)

    def drawAttempted(self, event):
        if game.turnNumber == 0 and game.started: 
            game.user.draw()
            if not game.user.hand[-1].isUsable():
                game.incTurn()

    def createUsedPile(self):
        self.lastCardUsed = game.deck.cards[0]
        finalX = int(canvas["width"])/2 - self.cardWidth//1.5
        time = 200
        animateWidgetMovement(self.lastCardUsed.main, finalX, int(canvas["height"])/2, time)
        root.after(int(time), self.checkUsedPile, time)

    def checkUsedPile(self, time):
        if self.lastCardUsed.name == "Wild_Draw":
            game.log.output("Wild Draw 4 was first in the discard pile. Reshuffling to pick a new card!")
            finalX = int(canvas["width"])/2 + self.cardWidth
            animateWidgetMovement(self.lastCardUsed.main, finalX, int(canvas["height"])/2, time/3*2)
            self.shuffle()
            root.after(int(time/3*2), self.createUsedPile)
        else:
            del self.cards[0]
            if self.lastCardUsed.name == "Wild":
                game.pickingColour = True
                toggleColourPicker("normal")
            else:
                game.started = True
                for cardObj in game.user.hand:
                    cardObj.animating = False
                    
            if self.lastCardUsed.name == "Skip": # Skip player 1's turn
                game.turnNumber = 1
                game.log.output(f"{game.user.name} had their turn skipped")
            elif self.lastCardUsed.name == "Draw": # Player 1 draws 2 and loses turn
                game.user.draw(2)
                game.log.output(f"{game.user.name} had their turn skipped")
                game.turnNumber = 1
            elif self.lastCardUsed.name == "Reverse": # Reverse order and skip player's turn
                game.log.output("Direction of play reversed!")
                game.turnNumber = game.playerCount-1
                game.increment = -1
                

    def updateLastUsed(self, card):
        self.usedPile.append(self.lastCardUsed)
        # Hide prior last card
        root.after(250, canvas.coords, self.lastCardUsed.main, -1*self.cardWidth, -1*self.cardHeight)
        # Update and show new last card
        self.lastCardUsed = card
        card.animating = True
        animateWidgetMovement(card.main, int(canvas["width"])/2 - self.cardWidth//1.5, int(canvas["height"])/2, 250)
        canvas.itemconfig(card.main, image=card.storedImage)

    def remakeDeck(self): # Shuffle used pile into deck
        self.cards = self.usedPile
        self.usedPile = []
        self.shuffle()
        # Place cards under deck
        for cardObj in self.cards:
            canvas.coords(cardObj.main, int(canvas["width"])/2+self.cardWidth, int(canvas["height"])/2)
        
class Player():
    def __init__(self, name, playerNumber, colour):    
        self.name = name
        self.hand = []
        self.num = playerNumber
        self.colour = colour
        self.turn = self.num == 1 
        game.log.main.tag_configure(f"PlayerNum{self.num}", foreground=self.colour)
        # Set up anchor positions for cards
        height = game.deck.cardHeight
        width = game.deck.cardWidth
        if self.num == 1: # Bottom
            self.xVal = int(canvas["width"])/2 + width/2
            self.yVal = int(canvas["height"]) - height/2 - 10
        elif self.num == 2: # Top
            self.xVal = int(canvas["width"])/2 + width/2
            self.yVal = 10 + height/2
        elif self.num == 4: # Left
            self.xVal = 10 + height/2
            self.yVal = int(canvas["height"])/2 + width/2
        else: # Right
            self.xVal = int(canvas["width"])- height/2 - 10 
            self.yVal = int(canvas["height"])/2 + width/2
        self.draw(7, bulk=True)
        
    def visualiseHand(self, handSize, time=200): # Visualisation
        if self.num <= 2:
            xVal = self.xVal - (handSize * game.deck.cardWidth / 2)
            xInc = game.deck.cardWidth
            yVal = self.yVal
            yInc = 0
        else: # Left or right. Alter y-axis per card
            xVal = self.xVal
            xInc = 0
            yVal = self.yVal - (handSize * game.deck.cardWidth /2)
            yInc = game.deck.cardWidth
        for i in range(handSize):
            self.hand[i].animating = True
            animateWidgetMovement(self.hand[i].main, xVal+(i*xInc), yVal+(i*yInc), time)
            root.after(time, self.hand[i].toggleUp, False)

    def draw(self, amount=1, bulk=False):
        time = 100
        try:
            for i in range(amount):
                if len(game.deck.cards) == 0:
                    game.log.output("Deck out of cards. Shuffling used pile into deck!")
                    game.deck.remakeDeck()
                self.hand.append(game.deck.cards.pop(0))
                canvas.itemconfig(self.hand[-1].main, state="normal")
                if self.num == 1: # Bottom
                    self.hand[-1].Normal() 
                elif self.num == 2: # Top
                    self.hand[-1].Reverse()
                elif self.num == 4: # Left
                    self.hand[-1].LeftToCentre()
                else: # Right
                    self.hand[-1].RightToCentre()
                if not bulk:
                    delay = 300*i
                else:
                    delay = time*(i+(self.num-1)*amount)
                root.after(delay, self.visualiseHand, len(self.hand), time)
            if amount == 1:
                game.log.output(f"{self.name} drew 1 card")
            elif amount > 0:
                game.log.output(f"{self.name} drew {amount} cards")
            if bulk and self.num == game.playerCount:
                root.after(delay+time, game.deck.createUsedPile)
        except Exception as e:
            game.log.output(f"{self.name} failed to draw {amount} total cards \n\n {e}", error=True)

    def botPlay(self):
        usableCards = []
        colours = []
        wild4Present = False
        wild4Allowed = True
        delay = 0
        for cardObj in self.hand:
            if cardObj.isUsable():
                usableCards.append(cardObj)
                if cardObj.name == "Wild_Draw":
                    wild4Present = True
            if cardObj.cardType != "Wild":
                colours.append(cardObj.colour)

        if len(usableCards) == 0:
            self.draw()
            if self.hand[-1].isUsable():
                usableCards.append(self.hand[-1])
                delay = 300 
        elif wild4Present and game.deck.lastCardUsed.colour in colours:
            wild4Allowed = False

        if len(usableCards) > 0:
            card = choice(usableCards)
            while card.name == "Wild_Draw" and not wild4Allowed:
                card = choice(usableCards)
            root.after(delay, self.botUse, card, colours) 
        else: 
            game.incTurn()
            
    def botUse(self, card, colours):
        if len(self.hand) == 2 and not game.uno: # Need to "say" UNO
            game.toggleUno()
        card.use(self)
        if card.name.find("Wild") > -1 and len(self.hand) > 0:
            if len(colours) > 0:
                game.changeWildColour(None, colours)
            else:
                game.changeWildColour(None)
        
        
class CustomText(Text):
    def __init__(self, *args, **kwargs):
        Text.__init__(self, *args, **kwargs)

    def highlight_pattern(self, pattern, tag, start="1.0", end="end", regexp=False):
        self.mark_set("matchStart", self.index(start))
        self.mark_set("matchEnd", self.index(start))
        self.mark_set("searchLimit", self.index(end))

        count = IntVar()
        while True:
            index = self.search(pattern, "matchEnd", "searchLimit", count=count, regexp=regexp)
            if index == "": break
            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
            self.tag_add(tag, "matchStart", "matchEnd")
        
class Log():
    def __init__(self):
        widthVal = 301
        heightVal = 612
        self.frame = Frame(root, width=widthVal, height=heightVal, bg=col)
        self.frame.place(x=10, rely=0.5, anchor="w")
        self.main = CustomText(self.frame, width=33, height=32, state="disabled", wrap=WORD, bg="grey", fg="white", font=("ArialBold", 13))
        self.main.place(x=0,y=0)
        self.main.tag_configure("error", background="yellow", foreground = "red")
        self.lastLineAppearedTwice = False 

    def output(self, msg, error=False):
        self.main["state"] = "normal"
        if self.main.get("end-2l", "end-2l lineend").find(msg) > -1:
            if not self.lastLineAppearedTwice: 
                self.main.insert("end-2l lineend", " x2")
            else: 
                lastLine = self.main.get("end-2l", "end-2l lineend")
                number = lastLine[::-1][:lastLine[::-1].find("x")][::-1]
                self.main.delete(f"end-{len(number)+2}c", "end-2l lineend")
                self.main.insert("end-2l lineend", str(int(number)+1))
            self.lastLineAppearedTwice = True
        else:
            self.lastLineAppearedTwice = False
            self.main.insert(END, "- " + str(msg) + "\n")
            for plr in game.players: 
                self.main.highlight_pattern(plr.name, f"PlayerNum{plr.num}", start="end-2l")
            if error: 
                self.main.highlight_pattern(self.main.get("end-4l", "end-2l lineend"), "error", start="end-4l")
                self.main.insert("end-4l+2c", "ERROR: ")
        self.main["state"] = "disabled"
        self.main.see("end") 

    def update(self):
        for plr in game.players:
            self.main.highlight_pattern(plr.name, f"PlayerNum{plr.num}")

class Game():    
    def __init__(self):
        self.players = []
        self.started = False
        self.skipNext = False
        self.uno = False
        self.pickingColour = False
        self.playerCount = 2
        self.turnList = []
        self.turnNumber = 0
        self.increment = 1
        self.botDelay = 1000
        self.firstGame = True

        # Title screen widgets
        width = int(canvas["width"])
        height = int(canvas["height"])
        
        self.title = canvas.create_image(width/2, height/3, image=images["UNO"])
        self.playButton = canvas.create_image(width/2, height//1.4, image=images["Start"])
        canvas.tag_bind(self.playButton, "<1>", self.hideTitleScreen)

        # Choosing player count screen widgets
        self.playerCountLabel = canvas.create_text(width/2 , height/5, text="Choose player count of ", font=("Arial", 50), fill="white", state="hidden")

        self.player2Background = canvas.create_image(width/3, height/2, image=images["Red"], state="hidden")
        self.player3Background = canvas.create_image(width/2, height/2, image=images["Green"], state="hidden")
        self.player4Background = canvas.create_image(width/3*2, height/2, image=images["Blue"], state="hidden")

        self.player2Label = canvas.create_text(width/3, height/2, text="2", state="hidden", font=("Arial", 50))
        self.player3Label = canvas.create_text(width/2, height/2, text="3", state="hidden", font=("Arial", 50))
        self.player4Label = canvas.create_text(width/3*2, height/2, text="4", state="hidden", font=("Arial", 50))

        self.playerCountWidgets = {
            "label": self.playerCountLabel,
            "2bg": self.player2Background, "3bg": self.player3Background, "4bg": self.player4Background,
            "2label": self.player2Label, "3label": self.player3Label, "4label": self.player4Label
            }
        
        for k, widget in self.playerCountWidgets.items():
            if k != "label":
                canvas.tag_bind(widget, "<1>", self.playerCountButtonClicked)


    def playerCountButtonClicked(self, event):
        for k, widget in self.playerCountWidgets.items():
            if widget == canvas.find_withtag(CURRENT)[0]:
                self.real_init(int(k[0]))
        
    def real_init(self, playerCount):
        # Hide widgets related to choosing player count
        for k, widget in self.playerCountWidgets.items():
            canvas.itemconfig(widget, state="hidden")
            
        # Place & shuffle deck
        self.deck.main.place(relx=0.5, rely=0.5, anchor="w")
        self.deck.shuffle()
        
        for cardObj in self.deck.cards:
            canvas.itemconfig(cardObj.main, state="normal")
            canvas.coords(cardObj.main,int(canvas["width"])/2+self.deck.cardWidth, int(canvas["height"])/2) 
            canvas.itemconfig(cardObj.main, image=cardObj.storedImage)
        # Clear log
        self.log.main.delete(1.0, "END")
        
        # Create players
        self.playerCount = playerCount
        playerHighlights = ["red3","CadetBlue3", "DarkGoldenRod2", "plum3"]
        self.user = Player("Player1", 1, playerHighlights[0])
        self.players.append(self.user)
        for i in range(1, self.playerCount):
            self.players.append(Player(f"Computer{i}", i+1, playerHighlights[i]))
        self.log.update()

        if self.playerCount == 2:
            self.turnList = self.players
        else:
            self.turnList = [self.user, self.players[2], self.players[1]]
            self.players[2].name, self.players[1].name = self.players[1].name, self.players[2].name
            self.players[2].colour, self.players[1].colour = self.players[1].colour, self.players[2].colour
            if self.playerCount == 4:
                self.turnList.append(self.players[3])
                
        # Show uno button
        canvas.itemconfig(self.unoButton, state="normal")
        # Bind motion
        canvas.bind("<Motion>", motion)

    def toggleUno(self, event=None):
        self.uno = not self.uno
        if self.uno:
            self.log.output(f"Uno Called on")
        else:
            self.log.output("Uno Called off")
        
    def incTurn(self):
        # next "player"'s turn
        self.turnNumber += self.increment
        self.uno = False
        # Allow turn skips
        if self.skipNext:
            # Simplify turn number
            self.simplifyTurnNumber()
            # Skip turn
            self.log.output(f"{self.turnList[self.turnNumber].name} had their turn skipped!")
            self.turnNumber += self.increment
            self.skipNext = False
        # Simplify turn number
        self.simplifyTurnNumber()
        # Let computer play turn
        game.log.output(f"{self.turnList[self.turnNumber].name}'s turn!")
        if self.turnNumber != 0:
            root.after(self.botDelay, self.turnList[self.turnNumber].botPlay)

    def simplifyTurnNumber(self,  alter=True, offset=0):
        num = self.turnNumber + offset
        while num >= self.playerCount:
                num -= self.playerCount
        # For negative increments, make sure it's at least zero
        while num < 0:
            num += self.playerCount
        if alter:
            self.turnNumber = num
        else:
            return num
            
    def changeWildColour(self, event, colours=["Red", "Green", "Blue", "Yellow"]):
        toggleColourPicker("hidden")
        colour = ""
        if event: 
            for key, obj in colourPicker.items():
                if canvas.find_withtag(CURRENT)[0] == obj:
                    colour = key
        else: 
            colour = choice(colours)
        self.deck.lastCardUsed.colour = colour
        game.log.output(f"{self.turnList[self.turnNumber].name} has picked the colour {colour}")
        game.pickingColour = False
        if event and not game.started:
            game.started = True
            for cardObj in game.user.hand:
                cardObj.animating = False
        else:
            self.incTurn()

    def displayTitleScreen(self, restart=False):
        if restart:
            # Reset Variables
            game.started = False
            self.skipNext = False
            self.uno = False
            self.pickingColour = False
            self.turnList = []
            self.turnNumber = 0
            self.increment = 1
            self.firstGame = False
            canvas.unbind("<Motion>")
            # Empty player list
            for i in game.players:
                del game.players[0]
            game.players = []
        else:
            self.log = Log()
            self.deck = Deck()
            # Create uno button
            self.unoButton = canvas.create_image(int(canvas["width"])/2+self.deck.cardWidth, int(canvas["height"])/2+1.25*(self.deck.cardHeight), image=images["UNO_Button"], state="hidden")
            canvas.tag_bind(self.unoButton, "<1>", self.toggleUno)

        # Display title screen
        canvas.itemconfig(self.playButton, state="normal")
        canvas.itemconfig(self.title, state="normal")

    def hideTitleScreen(self, event):
        # Hide title screen
        canvas.itemconfig(self.playButton, state="hidden")
        canvas.itemconfig(self.title, state="hidden")

        for k, widget in self.playerCountWidgets.items():
            canvas.itemconfig(widget, state="normal")

        

def animateWidgetMovement(label, finalX, finalY, time):
    baseX = canvas.coords(label)[0]
    baseY = canvas.coords(label)[1]
    deltaX = finalX-baseX
    deltaY = finalY-baseY
        
    duration = int(time)
    for i in range(1, duration + 1):
        root.after(int(i*(time/duration)), canvas.coords, label, baseX+i*(deltaX/duration), baseY+i*(deltaY/duration))

    root.after(duration, canvas.coords, label, finalX, finalY) 
    
def motion(event):
    if not game.started: return
    item = canvas.find_withtag(CURRENT)
    for cardObj in game.user.hand:
        if len(item) > 0 and cardObj.main == item[0]:
            if not cardObj.up:
                cardObj.animateUp()
        elif cardObj.up:
            cardObj.animateDown()

def toggleColourPicker(newState):
    for k, obj in colourPicker.items():
        canvas.itemconfigure(obj, state=newState)
        
game = Game()
game.displayTitleScreen()

for k, obj in colourPicker.items():
    canvas.tag_bind(obj,"<1>", game.changeWildColour)

root.mainloop()
