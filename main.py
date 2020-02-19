import os
import threading
import time
import asyncio

#LichessAccount
#username: TwitchPlaysChessNuta
#pass: XXXXXXXXXXXXXXXXXXXXXX
#email: nutarum@gmail.com

#https://www.twitch.tv/popout/nutarum/chat?popout=

from browserController import BrowserController
from TwitchChatController import TwitchChatController
from chessController import ChessController
from utils import Utils

conf = Utils.loadConfig()
BrowserController.initWeb(conf[1])

twitchChatBot = TwitchChatController(BrowserController)



async def start():
    global twitchChatBot
    while(1==1):
        #leemos el estado del navegador
        state = BrowserController.readState()
        if(state[0]==-1): #si no estamos en partida (ni en puzzle)
            os.system('cls')  # on windows 
            print("Not in a game, to start a new game type !start")
            time.sleep(2)
        else: #si estamos en partida, o en puzle
            #pedimos el siguiente movimiento a chesscontroler
            moveData = await ChessController.updateBoardState(state,twitchChatBot)            
            #si es un movimiento correcto, lo ejecutamos (podria ser none, por ejemplo si no es nuestro turno para mover)
            if(moveData != None and (len(moveData)==4 or len(moveData)==5)):
                BrowserController.movePiece(moveData,int(conf[0]))
                time.sleep(2)
        time.sleep(1)
            

#comenzamos 2 hilos, uno para twitch chat controler
thread1 = threading.Thread(target = twitchChatBot.twitchChatBotRun, args = ())
thread1.start()

#Y uno segundo con el bucle superior, para leer el estado del navegador y actual segun el mismo
asyncio.run(start())
