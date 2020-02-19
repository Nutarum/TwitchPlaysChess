import numpy as np
import random
import chess
import time

board = chess.Board()

class ChessController: 
    #reinicia el estado del tablero
    def clearBoard():        
        global board        
        board = chess.Board()
    
   
    async def updateBoardState(data,twitchChatBot):
        global board  
        ChessController.clearBoard()  
        print(data)
        #si el estado del tablero no tiene el formato esperado (el formato deberia ser, [bool,bool,list(str)]
        if(len(data)<3):
            return None
        global orientation
        global turn
        orientation = data[0]
        turn = data[1]
        moves = data[2]
        #recreamos la partida segun los movimientos recibidos
        for m in moves:  
            board.push_san(m)
            
        #si es nuestro turno pedimos a twitch chat el proximo movimiento
        if(orientation==turn):            
            return ChessController.realizarMovimiento(await twitchChatBot.selectMove(board))
        else:
            return None
    
    #transforma un movimiento en formato "d2d4" coordenadas del tablero en el navegador "4244" o "5254" segun esten abajo blancas o negras    
    def realizarMovimiento(selectedMove):    
        if(selectedMove=="resign"):
            return [-1,-1,-1,-1]
        if(selectedMove=="draw"):
            return [-1,-2,-1,-2]
            
        global orientation
        
        moveData = []
        startX = int(ord(selectedMove[0])-ord('a'))       
        startY = int(selectedMove[1])-1         
        endX = int(ord(selectedMove[2])-ord('a'))        
        endY = int(selectedMove[3])-1  
        
        if(orientation==False):
            startX = 7-startX
            endX = 7-endX
            startY = 7-startY
            endY = 7-endY
            
        moveData.append(startX)
        moveData.append(startY)
        moveData.append(endX)
        moveData.append(endY)
        if(len(selectedMove)>4): #si mide mas de 4 es que estamos coronando        
            moveData.append(int(selectedMove[4]))
        return moveData