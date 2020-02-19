# Twitch plays chess
Python program to allow twitch chat to play on lichess using chat commands (working on aug 2019)

Program should work fine in both normal games and puzzles

## Setup

* Paste your twitch irc_token in the file TwitchChatController.py
* Config so the bot starts loged in on lichess when u open mozilla (otherwise u have to log in as soon as mozilla opens when u execute main.py)
        Open firefox normally, go to lichess.org and log in
        Go to "C:/Users/<USER>/AppData/Roaming/Mozilla/Firefox/Profiles"
        One of the folders should containt info about firefox session (cookies and such)
        In this proyect folder "config.txt" in the line that follows "folder of mozilla firefox profile"
        Paste the name of that folder
        * IF WHEN EXECUTING main.py U DONT SEE THIS ERROR "ARCHIVO DE SESION DE FIREFOX NO ENCONTRADO, EL BOT NO ESTARÁ LOGEADO",
		  BUT AUTOLOGIN IS STILL NOT WORKING, WE SHOULD GO TO FIREFOX->OPTIONS->PRIVACY AND SECURITY
          HISTORY (and near "clean history when firefox is closed") press button "configuration..."
          and uncheck all options, and repeat the config process
* Start streaming your screen on twitch
* Start main.py


## ToDo ##
- 	basar la posicion de tablero en la casilla helper, o tal vez en el container del propio tablero
	asi podremos modificar el tamaño de las filas y los ranks antes del primer movimiento
	
- 	desplazar un pelin hacia la derecha los menus a la izq del tablero (para que los numeros de las filas se vean mejor)

- 	hacer que twitch controller envio mensajes sin ctx (usando el channel y get_channel)