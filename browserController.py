# import libraries
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
#from selenium.webdriver.firefox.options import Options
from pynput.mouse import Button, Controller
import time
import random
import os

#almacena las coordenadas de la posición del tablero en la pantalla del PC
boardStartX = -1
boardStartY = -1
squareSize = 0

mouse = Controller()

inMatchOrInPuzzle = False #false match, true puzzle

class BrowserController:    
    
    def initWeb(firefoxProfileFolder):
        global driver
        
        #PARA QUE EL BOT COMIENZE LOGEADO EN LICHESS
        # Abrimos el navegador con normalidad, vamos a lichess.org y nos logeamos
        # Ahora iremos a C:/Users/<USUARIO>/AppData/Roaming/Mozilla/Firefox/Profiles
        # Una de las carpetas contendra la informacion de la sesion de firefox (cookies y demas)
        # En el fichero config.txt, en la linea que sigue a "folder of mozilla firefox profile"
        # Pondremos el nombre de la carpeta
        # * SI NO SALTA EL ERROR DE QUE NO NOS LOGEAREMOS AL INCIAR LA APP, 
        #   PERO AUN ASI NO NOS LOGEAMOS, EN FIREFOX->OPCIONES->PRIVACIDAD Y SEGURIDAD
        #   HISTORIAL (al lado de "limpiar el historial cuando firefox se cierre") pulsamos el boton configuracion...
        #   y desmarcamos todas las casillas
        
        try:
            fp = webdriver.FirefoxProfile(os.getenv('APPDATA') + '/Mozilla/Firefox/Profiles/' + firefoxProfileFolder)        
            driver = webdriver.Firefox(fp)
        except Exception as e:
            print("ARCHIVO DE SESION DE FIREFOX NO ENCONTRADO, EL BOT NO ESTARÁ LOGEADO")
            print(e)
            driver = webdriver.Firefox()
        
        #PARA QUE EL NAVEGADOR NO SE MUESTRE
        #options = Options()
        #options.headless = True
        #driver = webdriver.Firefox(firefox_options=options)
        
        #driver = webdriver.Firefox()
        urlpage = 'https://lichess.org'
        # get web page
        driver.get(urlpage) 
        
        # Resize the window to the screen width/height
        driver.set_window_size(1440, 1040)
        # Move the window to position x/y
        driver.set_window_position(0, 0)

    #aumenta el tamaño de los indicadores de filas y rangos en los bordes del tablero
    #como usamos estos para obtener la posición del tablero en la pantalla, los aumentaremos solo despues de calcularla
    def bigFilesAndRanksNumbers():
        global driver
        script = "document.getElementsByClassName('files')[0].style.fontSize = '2em';" 
        driver.execute_script(script)
        script = "document.getElementsByClassName('files')[0].style.bottom = '-35px';" 
        driver.execute_script(script)
        script = "document.getElementsByClassName('ranks')[0].style.fontSize = '2em';" 
        driver.execute_script(script)
        try:
            script = "document.getElementsByClassName('puzzle__history')[0].style.marginTop = '30px';" 
            driver.execute_script(script)
        except:
            return 
     
    #calcula la posición y tamaño del tablero en la pantalla (el navegador debe estar en las coordenadas 0,0 de la pantalla)
    def loadBoardPosition():
        global squareSize
        global boardStartX
        global boardStartY  
        global driver
        global inMatchOrInPuzzle       
        
        barraSuperior = driver.execute_script('return window.outerHeight - window.innerHeight;')
                            
        if(inMatchOrInPuzzle):
            cgContainerXpath = "/html/body/div[1]/main/div[1]/div[1]/div/cg-helper/cg-container/"
        else:
            cgContainerXpath = "/html/body/div[1]/main/div[1]/div/cg-helper/cg-container/"
                  
        files = driver.find_elements_by_xpath(cgContainerXpath + 'coords[2]')
        ranks = driver.find_elements_by_xpath(cgContainerXpath + 'coords[1]')
        
        
        script = "return window.pageYOffset;" 
        scrollOffset = driver.execute_script(script)
            
        for f in files:
            boardStartX = f.location['x']
            boardStartY = f.location['y'] + barraSuperior - scrollOffset   
            
        for r in ranks:            
            squareSize = (r.location['x']-boardStartX)/8            
            
        boardStartX = boardStartX + squareSize/2
        boardStartY = boardStartY - squareSize/2
    
    #actualmente no se está utilizando
    def aceptarDesafios():
        btn = driver.find_elements_by_xpath('/html/body/header/div[2]/div[2]/div/div/div/div[2]/form/button')
        for b in btn:
            b.click()
           
    #intenta hacer un click en new opponent (en el caso de que no exista (contra stockfish por ejemplo), lo intenta en rematch)
    def newGame():       
        try:
            #try to click new opponent
            btn = driver.find_element_by_xpath('/html/body/div[1]/main/div[1]/div[6]/div/a')
            if(btn.get_attribute("innerText")=='NEW OPPONENT'): 
                btn.click()
            else:
                print(5/0)
        except:
            try:
                #try to click rematch
                btn = driver.find_element_by_xpath('/html/body/div[1]/main/div[1]/div[6]/div/button')
                if(btn.get_attribute("innerText")=='REMATCH'): 
                    btn.click()                
            except:
                print("ERROR: Button not found: new opponent or rematch")
    
    #comprueba que estamos en una partida que un este en marca
    #o en un puzle (en el caso de los puzles, se detectara si se ha acabado por los iconos X y V que salen en la tabla de movimientos) 
    #lee y devuelve los movimientos de la partida en juego
    def readState():    
        global inMatchOrInPuzzle
        global driver
        # find elements by xpath        
        data = []
        
        try:
            playing = driver.find_element_by_xpath('/html/body/div[1]/main/aside/div/section/div[1]/div/div')
            if(not "Playing" in playing.text and not "Jugando" in playing.text):
                return [-1]
            else:   
                inMatchOrInPuzzle = True
                movesXpath = "/html/body/div/main/div[1]/div/div[2]/m2"
                orientationXpath = "/html/body/div[1]/main/div[1]/div[1]/div/cg-helper/cg-container/coords[1]"
        except: #si no se encuentra el elemento playing, la linea superior da error, es que no estamos en partida
            try:            
                puzzle = driver.find_element_by_xpath('/html/body/div[1]/main/aside/div[1]/div[1]/div/a')
                if(not "Puzzle" in puzzle.text):
                    return [-1] #esto en realidad no deberia pasar, porque en el elemento puzzle SIEMPRE aparece la palabra puzzle
                else:
                    inMatchOrInPuzzle = False
                    movesXpath = "/html/body/div[1]/main/div[2]/div[2]/div[2]/move"
                    orientationXpath = "/html/body/div[1]/main/div[1]/div/cg-helper/cg-container/coords[1]"
            except: #si no se encuentra el elemento puzzle, es que no estamos en puzzle
                return [-1]
            
        #vamos a ver si las blancas o las negras estan abajo
        #lo dejo como elements y no element porque si no hay ninguno asi no hace falta meterlo en try except
        orientation = driver.find_elements_by_xpath(orientationXpath)
        for o in orientation:
            #si las blancas estan abajo, el valor es "ranks" si las negras estan abajo "ranks black"
            data.append(o.get_attribute("className")=='ranks') 
        
        #vamos a coger la tabla de movimientos
        moves = driver.find_elements_by_xpath(movesXpath)
        
        contadorRetry = 0
        
        movesArray = []
        for m in moves:                
            try:
                mtext = m.text
                #en los puzzles, a veces los movimientos de la tabla van acompañados de estos "iconos" segun hayamos movido bien o mal
                #puzle fallado, vamos a darle a ver la solución, y despues al siguiente puzle
                if("fail" in m.get_attribute("class")):
                    time.sleep(1)
                    driver.find_element_by_xpath("/html/body/div[1]/main/div[2]/div[3]/div[2]/a").click()
                    time.sleep(3)
                    driver.find_element_by_xpath("/html/body/div[1]/main/div[2]/div[3]/a").click()
                    return [-1]
                
                #puzle completado, esperamos 1 poco y le damos a ir al siguiente puzle
                if("win" in m.get_attribute("class")):
                    time.sleep(3)
                    driver.find_element_by_xpath("/html/body/div[1]/main/div[2]/div[3]/a").click()
                    return[-1] #devolvemos no estar en partida para que nos busque la siguiente partida en la proxima iteracion del bucle principal
                
                
                ### PUZLE PARA PRUEBAS CON RETRY https://lichess.org/training/36728
                #en caso de que el movimiento vaya acompañado del icono de good o retry
                #movimiento correcto (good) (aun quedan mas movimientos en el puzle) quitamos los caracteres raros del movimiento
                #movimiento aceptable (retry) pero no el buscado, quitamos los caracteres raros del movimiento
                if("\n" in mtext): 
                    mtext = mtext[:-2]
                #el retry tiene 2 caracteres raros en vez de uno, por lo que aun quedaria el \n
                if("\n" in mtext): 
                    #vamos a contar los retrys, pues se quedan en la tabla, y afectaran al modo de calcular a quien le toca mover
                    contadorRetry = contadorRetry +1
                else:
                    movesArray.append(mtext)
            except Exception as e:
                print(e)
        
        data.append((len(moves)-contadorRetry)%2==0)
        data.append(movesArray)
        return data
    
    #recibe las coordenadas de un movimiento (a2a4), y hace que el raton lo procese
    def movePiece(moveData,dragMouseDelay): 
        global mouse
        global boardStartX
        global boardStartY
        global squareSize 
        
        global driver
        #para las tablas
        if(moveData[1]==-2):
            try:
                btn = driver.find_element_by_xpath('/html/body/div[1]/main/div[1]/div[6]/div/button[2]')
                btn.click()
            except:
                return
            return
        #para rendirse
        if(moveData[1]==-1):
            try:
                btn = driver.find_element_by_xpath('/html/body/div[1]/main/div[1]/div[6]/div/button[3]')
                btn.click() 
            except:
                return
            return
        
        #si la posición del tablero aun no esta cargada, la cargamos
        if(boardStartX==-1):
            BrowserController.loadBoardPosition()       
        
        BrowserController.bigFilesAndRanksNumbers()
        
        #calculamos las coordenadas en la pantalla en función de las casillas    
        currentX = int(boardStartX + (moveData[0]*squareSize) + (random.randint(0, int(squareSize/4))-squareSize/8))
        currentY = int(boardStartY - (moveData[1]*squareSize) + (random.randint(0, int(squareSize/4))-squareSize/8))
        mouse.position = (currentX, currentY)
        mouse.press(Button.left)
        #mouse.click(Button.left, 1)
        targetX = int(boardStartX + (moveData[2]*squareSize) + (random.randint(0, int(squareSize/4))-squareSize/8))
        targetY = int(boardStartY - (moveData[3]*squareSize) + (random.randint(0, int(squareSize/4))-squareSize/8))
        i=0
        while(currentX!=targetX or currentY!=targetY):
            i=i+1
            if(i%dragMouseDelay==0):
                time.sleep(0.001)
            if(currentX!=targetX and currentY!=targetY):
                a = random.randint(0, 100)
                if(a<50):
                    if(currentX<targetX):
                        currentX = currentX+1
                    else:
                        currentX = currentX-1
                else:
                    if(currentY<targetY):
                        currentY = currentY+1
                    else:
                        currentY = currentY-1
            else:
                if(currentX!=targetX):
                    if(currentX<targetX):
                        currentX = currentX+1
                    else:
                        currentX = currentX-1
                else:
                    if(currentY<targetY):
                        currentY = currentY+1
                    else:
                        currentY = currentY-1
            mouse.position = (currentX,currentY)
        #mouse.click(Button.left, 1)
        mouse.release(Button.left)
        #si el movimiento es una coronación, hacemos un click un pelin mas tarde (solo coronación a reina implementada por el momento)
        if(len(moveData)==5):
            time.sleep(0.1)
            mouse.click(Button.left, 1)