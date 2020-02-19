from twitchio.ext import commands
import sys
import random
import os
import time

browserController = None
channel = None

legalMoves = []
alreadyVoted = []
maxVoted = 0
speedMode = 2
board = None

lastSpeedModeChange = 0
changeSpeedModeCD = 300


class TwitchChatController(commands.Bot):

    def __init__(self,browserControllerParam):
        global browserController
        
        browserController = browserControllerParam
        #the irc_token on the next line is provided by twitch
        super().__init__(irc_token='oauth:xxxxxxxxxxxxxxxxxxxxxxxxxx', client_id='NutarumBot', nick='Nutarum', prefix='!',
                         initial_channels=['nutarum'])
        
        

    # Events don't need decorators when subclassed
    async def event_ready(self):
        global channel
        channel = self.get_channel('nutarum')
        print(f'Ready | {self.nick}')
       

    #cada vez que alguien escribe un mensaje en el chat de twitch
    async def event_message(self, message):
        global legalMoves
        global maxVoted
        global board
        #si el mensaje puede ser un movimiento de ajedrez
        if(len(message.content) < 8): #el maximo movimiento en san mide 7 Nd1xc3+
            #si el mensaje esta escrito por alguien que aun no ha votado
            if(not message.author.name in alreadyVoted):
                #vamos a ver si el mensaje es uno de los posibles movimientos legales
                for i in range (0, len(legalMoves)):
                    sanString = board.san(legalMoves[i][0])
                    if(legalMoves[i][0].uci()==message.content or sanString==message.content or sanString==message.content+'+' or sanString==message.content+'#'):
                        #registramos el nuevo voto
                        alreadyVoted.append(message.author.name)
                        legalMoves[i][1] = legalMoves[i][1] +1 
                        if(legalMoves[i][1]>maxVoted):
                            maxVoted = legalMoves[i][1]
                        self.sortVoteList()
                        self.printVoteList()
                        return
                        
        #pasamos el mensaje al detector de comandos, para que si es un comando lo procese
        await self.handle_commands(message)
        
    #ordenamos la lista de [movimiento,votos] en funcion del parametro votos
    def sortVoteList(self):
        global legalMoves        
        legalMoves.sort(key=lambda x: x[1])
    
    #dibujamos la lista de votos en la consola
    def printVoteList(self):
        global legalMoves
        os.system('cls')  # on windows 
        for i in range (0,len(legalMoves),+1):
            print(legalMoves[i][0].uci()+ " " + str(legalMoves[i][1]))
    

    @commands.command(name='info')
    async def my_command_info(self, ctx):
        await ctx.send(f'Check the panels below the stream to learn how TwitchPlaysChess works.')
                    
    @commands.command(name='fast')
    async def my_command_fast(self, ctx):
        global speedMode        
        global lastSpeedModeChange
        global changeSpeedModeCD
        
        if(speedMode != 0 and lastSpeedModeChange + changeSpeedModeCD < time.time()):        
            lastSpeedModeChange = time.time()
            speedMode = 0       
            await ctx.send(f'Fast mode activated.')    
    
    @commands.command(name='normal')
    async def my_command_normal(self, ctx):
        global speedMode
        global lastSpeedModeChange
        global changeSpeedModeCD
        
        if(speedMode != 1 and lastSpeedModeChange + changeSpeedModeCD < time.time()):        
            lastSpeedModeChange = time.time()
            speedMode = 1
            await ctx.send(f'Normal mode activated.')    
        
    @commands.command(name='slow')
    async def my_command_slow(self, ctx):
        global speedMode
        if(speedMode != 2):
            speedMode = 2
            await ctx.send(f'Slow mode activated.')
    
    @commands.command(name='start')
    async def my_command_start(self, ctx):
        global browserController
        browserController.newGame()      
        
    @commands.command(name='exit')
    async def my_command_exit(self, ctx):  
        if(ctx.author.name=="nutarum"):
            sys.exit()         
    
    #escribe un mensaje en el chat de twitch
    async def sendMessage(self,msg):  
        global channel
        await channel.send(f'{msg}')          
    
    #comienza una votación para elegir movimiento
    async def selectMove(self,boardParam):
        global legalMoves
        global alreadyVoted
        global maxVoted
        global speedMode
        global board
        board = boardParam
        
        #calculamos todos los posibles movimientos legales, y los usamos para formar el array que guarda cada movimiento con su numero de votos
        legalMovesChessLib = board.legal_moves
        legalMoves = []
        for lm in legalMovesChessLib:
            legalMoves.append([lm,0])
        
        #NO DESCOMENTAR ESTA MIERDA QUE AHORA ESTA ROTA
        ###legalMoves.append("draw")
        ###legalMoves.append("resign")
        ###legalMovesVotes.append(-1)
        ###legalMovesVotes.append(-1)
        
        #vaciamos el array de personas que ya han votado    
        alreadyVoted = []  
        maxVoted = 0
        self.printVoteList()
        
        ### --- COMIENZO DE WAITS DURANTE LA FASE DE VOTACION ---
        ### --- COMIENZO DE WAITS DURANTE LA FASE DE VOTACION ---
        ### --- COMIENZO DE WAITS DURANTE LA FASE DE VOTACION ---
        
        #si estamos en el modo slow, comenzamos la cuenta atras al recibir el primer input
        if(speedMode==2):
            while(maxVoted==0):
                time.sleep(1)    
        #si no esta en el modo fast, hacemos la cuenta atras
        if(speedMode>0): 
            await self.sendMessage("> YOU HAVE 20 SECONDS TO VOTE <")
            time.sleep(20)  
        #en cualquier modo, esperaremos hasta que haya al menos 1 voto 
        #(en modo slow ya hemos esperado arriba, asi que nunca parará aquí)
        if(maxVoted==0 and speedMode>0):
            await self.sendMessage("> NO VOTES, NEXT INPUT WILL BE SELECTED <")
        while(maxVoted==0):
            time.sleep(1)    
        
        ### --- FIN DE WAITS DURANTE LA FASE DE VOTACION ---
        ### --- FIN DE WAITS DURANTE LA FASE DE VOTACION ---
        ### --- FIN DE WAITS DURANTE LA FASE DE VOTACION ---
        
        #ya hemos acabado las esperas, y tenemos algun voto, vamos a elegir el movimiento mas votado y devolverlo
        bestMoves = []
        for i in range (0, len(legalMoves)):
            if(legalMoves[i][1]==maxVoted):
                bestMoves.append(legalMoves[i][0])
        selected = random.choice (bestMoves)
        await self.sendMessage("> MOVE SELECTED " + selected.uci() + " (" + str(maxVoted) + " votes) <")
        os.system('cls')  # on windows 
        print("Waiting for opponent to move...")
        return selected.uci()        
    
    def twitchChatBotRun(self):
        self.run()