import os,sys,random,time
from datetime import datetime
import tkinter as tk
from tkinter import *
class Player(object):
    allsquares = [(x, y) for x in range(8) for y in range(8)]
    dullmoves = 0
    def __init__(self, colour, nature, name):
        self.colour   = colour
        self.nature   = nature
        self.name     = name
        self.can_castle_long_this_turn  = False
        self.can_castle_short_this_turn = False
        self.playedturns = 0
    def __str__(self):
        if self.nature is 'AI':
            return self.name+' ('+self.nature+')'+' as '+self.colour
        else:
            return self.name+' as '+self.colour
    def set_opponent(self, opponent):
        self.opponent = opponent
    def getpieces(self, board):
        return [pos for pos in board if board[pos].colour is self.colour]
    def potentialtargets(self, playerspieces):
        return [pos for pos in self.allsquares if pos not in playerspieces]
    def kingpos(self, board):
        for mine in self.getpieces(board):
            if board[mine].piecename is 'k':
                return mine
    def validmoves(self, board):
        self.set_castling_flags(board)
        mypieces=self.getpieces(board)
        for mine in mypieces:
            for target in self.potentialtargets(mypieces):
                if self.canmoveto(board, mine, target):
                    if not self.makesuscheck(mine, target, board):
                        yield (mine, target)
    def set_castling_flags(self, board):
        kingpos = self.kingpos(board)
        if self.king_can_castle(board, kingpos):
            if self.rook_can_castle_long(board, kingpos):
                self.can_castle_long_this_turn = True
            else:
                self.can_castle_long_this_turn = False
            if self.rook_can_castle_short(board, kingpos):
                self.can_castle_short_this_turn = True
            else:
                self.can_castle_short_this_turn = False
        else:
            self.can_castle_long_this_turn = False
            self.can_castle_short_this_turn = False
    def king_can_castle(self, board, kingpos):
        if board[kingpos].nrofmoves is 0 and not self.isincheck(board):
            return True
    def rook_can_castle_long(self, board, kingpos):
        if self.longrook in board and board[self.longrook].nrofmoves is 0:
            if self.hasclearpath(self.longrook, kingpos, board):
                tmptarget = (kingpos[0],kingpos[1]-1)
                if not self.makesuscheck(kingpos, tmptarget, board):
                    return True
    def rook_can_castle_short(self, board, kingpos):
        if self.shortrook in board and board[self.shortrook].nrofmoves is 0:
            if self.hasclearpath(self.shortrook, kingpos, board):
                tmptarget = (kingpos[0],kingpos[1]+1)
                if not self.makesuscheck(kingpos, tmptarget, board):
                    return True
    def getposition(self, move):
        startcol  = int(ord(move[0].lower())-97)
        startrow  = int(move[1])-1
        targetcol = int(ord(move[2].lower())-97)
        targetrow = int(move[3])-1
        start     = (startrow, startcol)
        target    = (targetrow, targetcol)
        return start, target
    def reacheddraw(self, board):
        if not list(self.validmoves(board)) and not self.isincheck(board):
            return True
        if len(list(self.getpieces(board))) == \
           len(list(self.opponent.getpieces(board))) == 1:
            return True
        if Player.dullmoves/2 == 50:
            if self.nature is 'AI':
                return True
            else:
                if input("Call a draw? (yes/no) : ") in ['yes','y','Yes']:
                    return True
    def ischeckmate(self, board):
        if not list(self.validmoves(board)) and self.isincheck(board):
            return True
    def turn(self, board):
        global inCheck
        turnstring = "\n%s's turn," % self.name
        warning = " *** Your King is in check *** "
        if self.isincheck(board):
            inCheck = True
            turnstring = turnstring + warning
        else:
            isCheck = False
        return turnstring
    def getmove(self, board):
        global firstClick,secondClick,globalself,globalboard,lastFirstClick,lastSecondClick
        globalself = self
        globalboard = board
        #print("Getting move")
        if firstClick != [] and secondClick != []:
            move = firstClick[0]+str(firstClick[1]+1) + secondClick[0]+str(secondClick[1]+1)
            #print(move)
            #print("Got the move boiz")
            lastFirstClick = firstClick
            lastSecondClick = secondClick
            firstClick = []
            secondClick = [] # help
            start, target = self.getposition(move)
            
            #print("Getting the self.getpos")
            if (start, target) in self.validmoves(board):
                #print("Returinig")
                return start, target
            else:
                #print("Error causing move")
                raise IndexError
    def makesuscheck(self, start, target, board):
        # Make temporary move to test for check
        self.domove(board, start, target)
        retval = self.isincheck(board)
        
        # Undo temporary move
        self.unmove(board, start, target)
        return retval
    def isincheck(self, board):
        kingpos = self.kingpos(board)
        for enemy in self.opponent.getpieces(board):
            if self.opponent.canmoveto(board, enemy, kingpos):
                return True
    def domove(self, board, start, target):
        self.savedtargetpiece = None
        if target in board:
            self.savedtargetpiece = board[target]
        board[target] = board[start]
        board[target].position = target
        del board[start]
        board[target].nrofmoves += 1
        if board[target].piecename is 'p' and not self.savedtargetpiece:
            if abs(target[0]-start[0]) == 2:
                board[target].turn_moved_twosquares = self.playedturns
            elif abs(target[1]-start[1]) == abs(target[0]-start[0]) == 1:
                # Pawn has done en passant, remove the victim
                if self.colour is 'white':
                    passant_victim = (target[0]-1, target[1])
                else:
                    passant_victim = (target[0]+1, target[1])
                self.savedpawn = board[passant_victim]
                del board[passant_victim]
        if board[target].piecename is 'k':
            if target[1]-start[1] == -2:
                # King is castling long, move longrook
                self.domove(board, self.longrook, self.longrook_target)
            elif target[1]-start[1] == 2:
                # King is castling short, move shortrook
                self.domove(board, self.shortrook, self.shortrook_target)
        
    def unmove(self, board, start, target):
        board[start] = board[target]
        board[start].position = start
        if self.savedtargetpiece:
            board[target] = self.savedtargetpiece
        else:
            del board[target]
        board[start].nrofmoves -= 1
        if board[start].piecename is 'p' and not self.savedtargetpiece:
            if abs(target[0]-start[0]) == 2:
                del board[start].turn_moved_twosquares
            elif abs(target[1]-start[1]) == abs(target[0]-start[0]) == 1:
                # We have moved back en passant Pawn, restore captured Pawn
                if self.colour is 'white':
                    formerpos_passant_victim = (target[0]-1, target[1])
                else:
                    formerpos_passant_victim = (target[0]+1, target[1])
                board[formerpos_passant_victim] = self.savedpawn
        if board[start].piecename is 'k':
            if target[1]-start[1] == -2:
                # King's castling long has been unmoved, move back longrook
                self.unmove(board, self.longrook, self.longrook_target)
            elif target[1]-start[1] == 2:
                # King's castling short has been unmoved, move back shortrook
                self.unmove(board, self.shortrook, self.shortrook_target)
    def pawnpromotion(self, board, target):
        if self.nature is 'AI':
            # See if Knight makes opponent checkmate
            board[target].promote('kn')
            if self.opponent.ischeckmate(board):
                return
            else:
                promoteto = 'q'
                
        else:
            promoteto = 'q'

        board[target].promote(promoteto)
    def hasclearpath(self, start, target, board):
        startcol, startrow = start[1], start[0]
        targetcol, targetrow = target[1], target[0]
        if abs(startrow - targetrow) <= 1 and abs(startcol - targetcol) <= 1:
            # The base case
            return True
        else:
            if targetrow > startrow and targetcol == startcol:
                # Straight down
                tmpstart = (startrow+1,startcol)
            elif targetrow < startrow and targetcol == startcol:
                # Straiht up
                tmpstart = (startrow-1,startcol)
            elif targetrow == startrow and targetcol > startcol:
                # Straight right
                tmpstart = (startrow,startcol+1)
            elif targetrow == startrow and targetcol < startcol:
                # Straight left
                tmpstart = (startrow,startcol-1)
            elif targetrow > startrow and targetcol > startcol:
                # Diagonal down right
                tmpstart = (startrow+1,startcol+1)
            elif targetrow > startrow and targetcol < startcol:
                # Diagonal down left
                tmpstart = (startrow+1,startcol-1)
            elif targetrow < startrow and targetcol > startcol:
                # Diagonal up right
                tmpstart = (startrow-1,startcol+1)
            elif targetrow < startrow and targetcol < startcol:
                # Diagonal up left
                tmpstart = (startrow-1,startcol-1)
            # If no pieces in the way, test next square
            if tmpstart in board:
                return False
            else:
                return self.hasclearpath(tmpstart, target, board)
    def canmoveto(self, board, start, target):
        startpiece = board[start].piecename.upper()
        if startpiece == 'R' and not self.check_rook(start, target):
            return False
        elif startpiece == 'KN' and not self.check_knight(start, target):
            return False
        elif startpiece == 'P' and not self.check_pawn(start, target, board):
            return False
        elif startpiece == 'B' and not self.check_bishop(start, target):
            return False
        elif startpiece == 'Q' and not self.check_queen(start, target):
            return False
        elif startpiece == 'K' and not self.check_king(start, target):
            return False
        # Only the 'Knight' may jump over pieces
        if startpiece in 'RPBQK':
            if not self.hasclearpath(start, target, board):
                return False
        return True
    def check_rook(self, start, target):
        # Check for straight lines of movement(start/target on same axis)
        if start[0] == target[0] or start[1] == target[1]:
            return True
    def check_knight(self, start, target):
        # 'Knight' may move 2+1 in any direction and jump over pieces
        if abs(target[0]-start[0]) == 2 and abs(target[1]-start[1]) == 1:
            return True
        elif abs(target[0]-start[0]) == 1 and abs(target[1]-start[1]) == 2:
            return True
    def check_pawn(self, start, target, board):
        # Disable backwards and sideways movement
        if 'white' in self.colour and target[0] < start[0]:
            return False
        elif 'black' in self.colour and target[0] > start[0]:
            return False
        if start[0] == target[0]:
            return False
        if target in board:
            # Only attack if one square diagonaly away
            if abs(target[1]-start[1]) == abs(target[0]-start[0]) == 1:
                return True
        else:
            # Make peasants move only one forward (except first move)
            if start[1] == target[1]:
                # Normal one square move
                if abs(target[0]-start[0]) == 1:
                    return True
                # 1st exception to the rule, 2 square move first time
                if board[start].nrofmoves is 0:
                    if abs(target[0]-start[0]) == 2:
                        return True
            # 2nd exception to the rule, en passant
            if start[0] == self.enpassantrow:
                if abs(target[0]-start[0]) == 1:
                    if abs(target[1]-start[1]) == 1:
                        if target[1]-start[1] == -1:
                            passant_victim = (start[0], start[1]-1)
                        elif target[1]-start[1] == 1:
                            passant_victim = (start[0], start[1]+1)
                        if passant_victim in board and \
                        board[passant_victim].colour is not self.colour and \
                        board[passant_victim].piecename is 'p'and \
                        board[passant_victim].nrofmoves == 1 and \
                        board[passant_victim].turn_moved_twosquares == \
                        self.playedturns-1:
                            return True
    def check_bishop(self, start, target):
        # Check for non-horizontal/vertical and linear movement
        if abs(target[1]-start[1]) == abs(target[0]-start[0]):
            return True
    def check_queen(self, start, target):
        # Will be true if move can be done as Rook or Bishop
        if self.check_rook(start, target) or self.check_bishop(start, target):
            return True
    def check_king(self, start, target):
        # King can move one square in any direction
        if abs(target[0]-start[0]) <= 1 and abs(target[1]-start[1]) <= 1:
            return True
        # ..except when castling
        if self.can_castle_short_this_turn:
            if target[1]-start[1] == 2 and start[0] == target[0]:
                return True
        if self.can_castle_long_this_turn:
            if target[1]-start[1] == -2 and start[0] == target[0]:
                return True

def AIMove(self,board):
    #qwerty
    #print(list(self.validmoves(board)))
    move = random.choice(list(self.validmoves(board)))
    #print(move)
    return move

    
class Piece(object):
    def __init__(self, piecename, position, player):
        self.colour    = player.colour
        self.nature    = player.nature
        self.piecename = piecename
        self.position  = position
        self.nrofmoves = 0
    def __str__(self):
        if self.colour is 'white':
            if self.piecename is 'p':
                return 'WP'
            else:
                return self.piecename.upper()
        else:
            return self.piecename
    def canbepromoted(self):
        if str(self.position[0]) in '07':
            return True
    def promote(self, to):
        self.piecename = to.lower()
class Game(object):
    def __init__(self, playera, playerb):
        self.board = dict()
        for player in [playera, playerb]:
            if player.colour is 'white':
                brow, frow = 0, 1
                player.enpassantrow = 4
            else:
                brow, frow = 7, 6
                player.enpassantrow = 3
            player.longrook  = (brow, 0)
            player.longrook_target = \
            (player.longrook[0], player.longrook[1]+3)
            
            player.shortrook = (brow, 7)
            player.shortrook_target = \
            (player.shortrook[0], player.shortrook[1]-2)
            
            [self.board.setdefault((frow,x), Piece('p', (frow,x), player)) \
            for x in range(8)]
            [self.board.setdefault((brow,x), Piece('r', (brow,x), player)) \
            for x in [0,7]]
            [self.board.setdefault((brow,x), Piece('kn',(brow,x), player)) \
            for x in [1,6]]
            [self.board.setdefault((brow,x), Piece('b', (brow,x), player)) \
            for x in [2,5]]
            self.board.setdefault((brow,3),  Piece('q', (brow,3), player))
            self.board.setdefault((brow,4),  Piece('k', (brow,4), player))
    def printboard(self):
        #print(globalplayerself)
        renderPieces(self)
    def refreshscreen(self, player):
        if player.colour is 'white':
            playera, playerb = player, player.opponent
        else:
            playera, playerb = player.opponent, player
        #os.system('clear')
        #print ("   Now playing: %s vs %s" % (playera, playerb))
        self.printboard()
    def run(self, player): # qwerty
        global globalgameself,globalplayera,globalplayerb,cplayer,titletext,winner,invalidMove
        globalgameself = self
        self.refreshscreen(player)
        while True:
            try:
                global turnstarttime,player1Time,player2Time
                start, target = player.getmove(self.board)
                if str(cplayer)[7] == "1":

                    player1Time -= ((time.time()-turnstarttime))
                    if player1Time <= 0:
                        player1Time = "LOSE"
                        winner = "Black Wins!\nWhite is out of time"
                else:
                    player2Time -=((time.time()-turnstarttime))
                    if player2Time <= 0:
                        player2Time = "LOSE"
                        winner = "White Wins!\nBlack is out of time"
                turnstarttime = time.time()
                invalidMove = False


            except (IndexError, ValueError):
                global invalidMove
                invalidMove = True
                self.refreshscreen(player)
                holder = globalplayera
                globalplayera = globalplayerb
                globalplayerb = holder
                cplayer = cplayer.opponent
                titletext.set("       PyChess            \n\n"+str("INVALID MOVE")+"\n\n\n\n")
                mywindow.update()
                time.sleep(0.2)
            except TypeError:
                # No start, target if user exit
                    break
            else:
                if target in self.board or self.board[start].piecename is 'p':
                    Player.dullmoves = 0
                else:
                    Player.dullmoves += 1
                player.domove(self.board, start, target)
                player.playedturns += 1
                # Check if there is a Pawn up for promotion
                if self.board[target].piecename is 'p':
                    if self.board[target].canbepromoted():
                        player.pawnpromotion(self.board, target)
                player = player.opponent
                if player.reacheddraw(self.board):
                    return 1, player
                elif player.ischeckmate(self.board):
                    return 2, player
                else:
                    self.refreshscreen(player)
    def end(self, player, result):
        looser = player.name
        winner = player.opponent.name
        if result == 1:
            endstring = "\n%s and %s reached a draw." % (winner, looser)
        elif result == 2:
            endstring = "\n%s put %s in checkmate." % (winner, looser)
        #os.system('clear')
        #print("Check Mate")
        self.printboard()
        return endstring
def newgame():
    global globalplayera,globalplayerb
    #playera, playerb = getplayers()
    playera = Player('white', 'human', "Player 1")
    playerb = Player('black', 'human', "Player 2")
    globalplayera = playera
    globalplayerb = playerb
    playera.set_opponent(playerb)
    playerb.set_opponent(playera)
    game = Game(playera, playerb)
    # WHITE starts
    player = playera
    try:
        result, player = game.run(player)
    except TypeError:
        # No result if user exit
        pass
    else:
        print (game.end(player, result))
        input("\n\nPress any key to continue")
def setxy(event):
    """This updates every mouse movement to keep the mouse coords accurate """
    global mousex,mousey
    mousex = event.x
    mousey = event.y


def makeBackGroundImage(BGFile="Chess Board"):
    photo = tk.PhotoImage(file=str(BGFile) + ".gif")
    label = tk.Label(image=photo)
    label.image = photo
    try:
        mycanvas.create_image(256,256,image=photo)
    except:

        mycanvas3.create_image(858/2,536/2,image=photo)

def drawPiece(piece,gridPos,canvas):
    global imagelist
    imagepos = 25
    piece = str(piece)
    if piece == piece.lower():
        piece = "B" + piece.upper()
    for i in range(len(imagelist)):
        if imagelist[i] == piece:
            imagepos = i+1
    randomx = random.randint(0,0)
    randomy = random.randint(0,0) # drunk
    if imagepos < 25:
        canvas.create_image((gridPos[1]*64)+32+randomx,((7-gridPos[0])*64)+32+randomy,image=imagelist[imagepos])
        #pass
    else:
        canvas.create_image((gridPos[1]*64)+32,((7-gridPos[0])*64)+32,image=imagelist[25])

            
    #mywindow.update()
    #time.sleep(1)
def loadpieces():
    l = []
    for i in (["R","KN","B","Q","K","WP","p","r","kn","b","q","k","PastSquare"]):
        if i == i.lower():
            i = "B" + i.upper()
        photo = tk.PhotoImage(file=(str(i)+".gif"))
        if i != ("PastSquare"):
            photo = photo.subsample(5,5)
        label = tk.Label(image=photo)
        label.image = photo
        l.append(i)
        l.append(photo)
    return l
        
def drawgreendots(self):
    moves = list(Player.validmoves(globalself,globalboard))
    piecemoves = []
    localfirstClick = [["a","b","c","d","e","f","g","h"].index(firstClick[0]),firstClick[1]]
    ##print(firstClick)
    for i in range(len(moves)):
        if moves[i][0][0] == localfirstClick[1] and moves[i][0][1] == localfirstClick[0]:
            piecemoves.append(moves[i])   
    for row in range(8):
        for column in range(8):
            for item in piecemoves:
                if (row,column) == item[1]:
                    if (row,column) in globalboard:
                        mycanvas.create_oval((column)*64+27,(7-row)*64+27,(column)*64+37,(7-row)*64+37,fill="red")
                    else:
                        mycanvas.create_oval((column)*64+27,(7-row)*64+27,(column)*64+37,(7-row)*64+37,fill="green")

def checkCircle(self):
    global inCheck
    if inCheck:
        #print("Check thing running")
        inCheck = False
        for row in range(8):
            for column in range(8):
                if (row, column)  in self.board:
                    #print(self.board[row,column],str(cplayer)[16])
                    if str(self.board[row,column]) == ("K") and str(cplayer)[16] == "k":
                        checkCircle1 = mycanvas.create_rectangle((column)*64+2,(7-row)*64+2,(column)*64+62,(7-row)*64+62,fill="red",stipple="gray25",outline="red")
                    if str(self.board[row,column]) == ("k") and str(cplayer)[16] == "e":
                       checkCircle2 = mycanvas.create_rectangle((column)*64+2,(7-row)*64+2,(column)*64+62,(7-row)*64+62,fill="red",stipple="gray25",outline="red")
   
        

def renderPieces(self):
    global globalboard,inCheck,allPieces
    globalboard = self
    mycanvas.delete('all')
    makeBackGroundImage()

    allPieces = ["R","KN","B","Q","K","B","KN","R","WP","WP","WP","WP","WP","WP","WP","WP","p","p","p","p","p","p","p","p","r","kn","b","q","k","b","kn","r"]
    for row in range(8):
        for column in range(8):
            if (row, column)  in self.board:
                try:
                    allPieces.remove(str(self.board[row,column]))
                except:
                    pass
                drawPiece(self.board[row,column],[row,column],mycanvas)
            if len(lastFirstClick) > 0 and len(lastSecondClick) > 0:
                if (row,column) == (["a","b","c","d","e","f","g","h"].index(lastFirstClick[0]),lastFirstClick[1]) or (row,column) == (["a","b","c","d","e","f","g","h"].index(lastSecondClick[0]),lastSecondClick[1]):
                    if invalidMove == False:
                        drawPiece("decent banter",[column,row],mycanvas)





def mouseclick(event):
    global firstClick,secondClick,turnstarttime
    gridSquare = [mousex//64,7-(mousey//64)]
    if gridSquare[0] not in [0,1,2,3,4,5,6,7]:
        gridSquare = [-1,-1]
    gridSquare[0] = ["a","b","c","d","e","f","g","h"][gridSquare[0]]
    #print(gridSquare)
    if firstClick == []:
        firstClick = gridSquare
        drawgreendots(globalboard)
        return
    if secondClick == []:
        secondClick = gridSquare
        #turnstarttime = time.time()
    

def update():
    global firstClick,secondClick,start,globalplayerself,cplayer,titletext,timesincestart,turntime,inCheck,globalself,mycanvas2,checkMate,winner
    timesincestart = time.strftime('%H:%M:%S', time.gmtime(time.time()-starttime))
    turntime       =  time.strftime('%H:%M:%S', time.gmtime(time.time()-turnstarttime))
    try:
        if cplayer.opponent.isincheck(globalboard):
            inCheck = True
            checkCircle(globalgameself)

    except AttributeError:
        pass

    try:
        if len((list(cplayer.opponent.validmoves(globalboard)))) == 0:
            checkMate = True
            if "white" in str(cplayer.opponent):
                winner = "Black Wins!\nCheck Mate"
            if "black" in str(cplayer.opponent):
                winner = "White Wins!\nCheck Mate"
            print(cplayer.opponent)
        #(list(self.validmoves(board)))
    except AttributeError:
        pass
        
    mywindow.update()
    if cplayer != "Played 1 is white":
        titletext.set("       PyChess            \n\n"+str(cplayer.opponent)+"\n"+str(timesincestart)+(".")+(str(datetime.now().microsecond)[0])+"\n"+str(turntime)+"\n\n"+(str(player1Time)[0:6]+"\t"+(str(player2Time)[0:6]))+("\n" + str(winner) + "\n"))
        whitePieces = []
        blackPieces = []
        individualPieces = ["p","WP","kn","KN","b","B","r","R","q","Q"]
        for i in range(0,len(individualPieces),2):
            if individualPieces[i] in allPieces and individualPieces[i+1] in allPieces:
                allPieces.remove(allPieces[allPieces.index(individualPieces[i])])
                allPieces.remove(allPieces[allPieces.index(individualPieces[i+1])])
        counter = 0
        mycanvas2.delete('all')
        for piece in (allPieces):
            counter += 1
            if piece == piece.lower():
                piece = "B" + piece.upper()
            for i in range(len(imagelist)):
                if imagelist[i] == piece:
                    imagepos = i+1
            mycanvas2.create_image(50+50*counter,50,image=imagelist[imagepos])
    else:
        titletext.set("       PyChess            \n\nPlayer 1 as white\n"+str(timesincestart)+(".")+(str(datetime.now().microsecond)[0])+"\n"+str(turntime)+"\n\n"+(str(timeLimit)+"\t"+str(timeLimit)+"\n\n\n"))
    if firstClick != [] and secondClick != []:
        #print(firstClick,secondClick)
        move = firstClick+secondClick
        if cplayer == "":
            cplayer = globalplayerb
        if cplayer == globalplayera:
            cplayer = globalplayerb
        else: 
            cplayer = globalplayera
        Game.run(globalgameself,cplayer)
    mywindow.after(16,update)

def start():
    global mywindow,timeLimit
    print("Start")
    try:
        timeLimit = int(variable.get())*60
    except:
        timeLimit = 120*60
    mywindow.destroy()
    
timeLimit = 0
mywindow = Tk()
mycanvas3 = tk.Canvas(mywindow,height=536,width=858,bg='white')
mycanvas3.pack()
makeBackGroundImage("BackGround")
variable = StringVar(mywindow)

variable.set("Choose a time") # default value
b = Button(mywindow,text="Start!",command=start)
w = OptionMenu(mywindow, variable, "1","2","3","4","5","6","7","8","9","10","12","14","16","18","20","25","30","40","50","60","90","120")
mycanvas3.create_window(100,300,window=w)
mycanvas3.create_window(250,300,window=b)
#w.pack()

mainloop()


winner = ""
cplayer = "Played 1 is white"
globalgameself = ""
globalself = ""
globalboard = ""
globalplayerself = ""
globalplayera = ""
globalplayerb = ""
firstClick = []
secondClick = []
lastFirstClick = []
lastSecondClick = []
player1Time = timeLimit
player2Time = timeLimit
whitetakenlist = ""
blacktakenlist = ""
timesincestart = 0
starttime = time.time()
turnstarttime = time.time()
turntime = 3
inCheck = False
invalidMove = False
#print("Start == True")
allPieces = []
start = True
checkMate = False
mywindow = tk.Tk()
mywindow.title("PyChess")
mywindow.grid()
imagelist = loadpieces()
mycanvas = tk.Canvas(mywindow,height=512,width=512,bg='white')
mycanvas2 = tk.Canvas(mywindow,height=100,width=512,bg="grey")
rightPane = Frame(mywindow,width=200,height=512,bg="grey")
titletext = StringVar()
titletext2 = StringVar()
title = Label(rightPane,textvariable=titletext,font=("Agency FB Bold",30),bg="grey")
title2 = Label(rightPane,textvariable=titletext2,font=("Agency FB Bold",15),bg="grey",fg="red")
titletext.set("       PyChess            \nPlayer 1 as white"+"\n\n00:00:00\n00:00:00\n\n")


rightPane.grid(row=0,column=2)
title.pack()
title2.pack()
mycanvas2.grid(row=1,column=1)
mycanvas.grid(row=0,column=1)
mywindow.bind('<Motion>', setxy)
mycanvas.bind('<Button-1>', mouseclick)
makeBackGroundImage()



mywindow.update()
newgame()
update()
mywindow.mainloop()

# globals #
mousex = 0
mousey = 0





