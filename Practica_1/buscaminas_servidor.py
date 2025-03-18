""""
    # Mensajes que debe mostar el cliente: 
    1: "Imprimir 'Elige dificultad'"
    2: "Imprimir 'Casilla liberada'"
    3: "Imprimir 'Mina pisada'"
    4: "Imprimir 'Mina marcada'"

    # Comandos de juego 
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

#Función para elegir la dificultad del juego
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
        while not termina:
            data = Client_conn.recv(buffer_size).decode() # Funcion bloqueante

            if data == "C-1":
                tablero, tam, num_minas = generar_tablero("1")
                imprimir_tablero(tablero)
                Client_conn.sendall(b"S-5") # Listo para recibir tiros y dificultad principiante
                tiros_ganar = (tam * tam) - num_minas
            elif data == "C-2":
                tablero, tam, num_minas = generar_tablero("2")
                imprimir_tablero(tablero)
                Client_conn.sendall(b"S-6") # Listo para recibir tiros y dificultad avanzado
                tiros_ganar = (tam * tam) - num_minas
            else:
                coordenadas = data # Coordenadas
                columna = ord(coordenadas[0].upper()) - ord('A') + 1
                fila = int(coordenadas[1])
                print(f"Coordenadas de tiro: ({fila}, {columna})")
                resultado_tiro, minas_str = realizar_tiro(tablero, columna, fila)
            
                if resultado_tiro == "S-9": # Liberar casilla
                    cont += 1
                if cont >= tiros_ganar: # Descubrio todas las libres y gana
                    Client_conn.sendall("S-10".encode()) # Has ganado
                    print("Usuario ha ganado el juego!")
                    termina = True

                Client_conn.sendall(resultado_tiro.encode())
                if resultado_tiro == "S-7": # Mina pisada
                    Client_conn.sendall(minas_str.encode())
                    termina = True

def iniciar_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPServerSocket:
        TCPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Permite la reutilización del puerto 
        TCPServerSocket.bind((host, int(port)))
        TCPServerSocket.listen()
        print("Esperando por un cliente")

        Client_conn, Client_add = TCPServerSocket.accept()
        print("Esperando al jugador")
        recibir_cliente(Client_conn, Client_add)

# host = input("Ingresa la IP: ")
# port = int(input("Ingresa el puerto: "))
host = "localhost"
port = 65432
iniciar_server(host, port)
print("Server acabo")