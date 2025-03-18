""""
    # Comandos de juedo que manda el servidor
    C-1: Usuario eligio dificultad principiante
    C-2: Usuario eligio dificultad avanzado
    C-3: Cliente pregunta por duracion de la partida

    # Comandos de juego que manda el servidor
    S-5: Listo para recibir tiros y dificultad principiante
    S-6: Listo para recibir tiros y dificultad avanzado
    S-7: Mina pisada
    S-8: Casilla ya liberada
    S-9: Se libero casilla
    S-10: Has ganado
"""

import random 
import socket
import time 

buffer_size = 1024

def imprimir_tablero(tablero):
    size = len(tablero)
    # Imprimir encabezado de columnas
    encabezado_columnas = "   " + " ".join(chr(65 + i) for i in range(size))
    print(encabezado_columnas)
    
    # Imprimir filas con encabezado de filas
    for i in range(size):
        print(f"{i+1:2} " + " ".join(tablero[i]))


def generar_tablero(dificultad):
    size = 0
    if dificultad == "1":
        size, minas = 9, 10
    elif dificultad == "2":
        size, minas = 16, 40
    else:
        print("Digite una opción válida")
        return None, 0, 0
    
    tablero = [["-" for _ in range(size)] for _ in range(size)]
    minas_colocadas = 0

    while minas_colocadas < minas:
        x, y = random.randint(0, size-1), random.randint(0, size-1)
        # Esto evita que se repitan las minas y sean las establecidas
        if tablero[x][y] != "*":
            tablero[x][y] = "*"
            minas_colocadas += 1
    return tablero, size, minas_colocadas


def realizar_tiro(tablero, columna, fila):
    if tablero[fila-1][columna-1] == "*":
        print("Mina pisada")
        minas = [(i+1, chr(j+65)) for i in range(len(tablero)) for j in range(len(tablero[i])) if tablero[i][j] == "*"]
        minas_str = ",".join([f"{mina[1]}{mina[0]}" for mina in minas])
        return "S-7", minas_str
    elif tablero[fila-1][columna-1] == "o":
        imprimir_tablero(tablero)
        print(f"Casilla ya liberada ({columna},{fila})")
        return "S-8", ""
    else:
        tablero[fila-1][columna-1] = "o"
        imprimir_tablero(tablero)
        print(f"Casilla liberada ({columna},{fila})")
        return "S-9", ""


def recibir_cliente(Client_conn, Client_add):
    cont = 0
    termina = False
    
    with Client_conn:
        print(f"Jugador conectado desde {Client_add}")
        data = Client_conn.recv(buffer_size).decode() # Funcion bloqueante
        if data == "C-1":
            tablero, tam, num_minas = generar_tablero("1")
            imprimir_tablero(tablero)
            Client_conn.sendall(b"S-5") # Listo para recibir tiros y dificultad principiante
            tiros_ganar = (tam * tam) - num_minas
        
        if data == "C-2":
            tablero, tam, num_minas = generar_tablero("2")
            imprimir_tablero(tablero)
            Client_conn.sendall(b"S-6") # Listo para recibir tiros y dificultad avanzado
            tiros_ganar = (tam * tam) - num_minas
        
        tiempo_inicio = time.time()
        while not termina:
            coordenadas = Client_conn.recv(buffer_size).decode() # Funcion bloqueante
            columna = ord(coordenadas[0].upper()) - ord('A') + 1
            fila = int(coordenadas[1])
            print(f"Coordenadas de tiro: ({fila}, {columna})")
            resultado_tiro, minas_str = realizar_tiro(tablero, columna, fila)
        
            if resultado_tiro == "S-9": # Liberar casilla
                cont += 1
            if cont >= tiros_ganar: # Descubrio todas las libres y gana
                Client_conn.sendall("S-10".encode()) # Cliente ha ganado
                print("Usuario ha ganado el juego!")
                termina = True

            Client_conn.sendall(resultado_tiro.encode())
            if resultado_tiro == "S-7": # Mina pisada. Cliente ha perdido 
                Client_conn.sendall(minas_str.encode())
                termina = True
        
        tiempo_final = time.time()
        tiempo_jugado = (tiempo_final - tiempo_inicio)
        tiempo_jugado = str(tiempo_jugado)
        print("Duración del juego: ", tiempo_jugado)

        comando_clien = Client_conn.recv(buffer_size).decode() # El cliente pregunta por el tiempo
        if comando_clien == "C-3":
            Client_conn.sendall(tiempo_jugado.encode())


def iniciar_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPServerSocket:
        TCPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Permite la reutilización del puerto 
        TCPServerSocket.bind((host, int(port)))
        TCPServerSocket.listen()
        print("Esperando por un cliente")

        Client_conn, Client_add = TCPServerSocket.accept()
        print("Esperando al jugador")
        recibir_cliente(Client_conn, Client_add)


host = input("Ingresa la IP (del servidor): ")
port = input("Ingresa el puerto (del servidor): ")
iniciar_server(host, int(port))
print("\nServer acabo")