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

import socket

buffer_size = 1024

def mostrar_estado(comando_serv, tablero):
    if comando_serv == "S-5":
        print("Juego iniciado en PRINCIPIANTE")
        print("Listo para recibir tiros. Ingresa coordenadas en formato LetraNúmero, por ejemplo: A1")
    elif comando_serv == "S-6":
        print("Juego iniciado en AVANZADO")
        print("Listo para recibir tiros. Ingresa coordenadas en formato LetraNúmero, por ejemplo: A1")
    elif comando_serv == "S-7":
        print("Mina pisada")
        imprimir_tablero(tablero)
        print("HAS PERIDO!!!")
    elif comando_serv == "S-8":
        print("Casilla ya liberada")
    elif comando_serv == "S-9":
        print("Casilla liberada")
    elif comando_serv == "S-10":
        imprimir_tablero(tablero)
        print("Has ganado el juego!")
    elif comando_serv == "S-11":
        print("Coordenadas fuera del rango, intenta de nuevo")
    else:
        print(f"Mensaje desconocido: {comando_serv}")

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
        size = 9
    elif dificultad == "2":
        size = 16
    else:
        print("Digite una opción válida")
        return None
    
    tablero = [["-" for _ in range(size)] for _ in range(size)]

    return tablero


def iniciar_cliente(host, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPClientSocket:
            TCPClientSocket.connect((host, port))
            print("Conectado al servidor")
            print("Selecciona la dificultad:")
            print("C-1: Principiante (9x9, 10 minas) \nC-2: Avanzado (16x16, 40 minas)")
            dificultad = input("> ")
            TCPClientSocket.sendall(dificultad.encode())
            comando_serv = TCPClientSocket.recv(buffer_size).decode()
            tablero = generar_tablero(dificultad[-1])
            mostrar_estado(comando_serv, tablero)
            imprimir_tablero(tablero)

            while True:
                comando_coord = input("Ingresa una coordenada (Ej: A1): ")
                columna = ord(comando_coord[0].upper()) - ord('A') + 1
                fila = int(comando_coord[1])

                TCPClientSocket.sendall(comando_coord.encode())
                comando_serv = TCPClientSocket.recv(buffer_size).decode()
                
                if comando_serv == "S-7": # Juego perdido
                    minas_str = TCPClientSocket.recv(buffer_size).decode() # Recive las minas del servidor
                    minas = minas_str.split(',')
                    for mina in minas:
                        fila = int(mina[1:]) - 1
                        columna = ord(mina[0].upper()) - ord('A')
                        tablero[fila][columna] = "*"
                    mostrar_estado(comando_serv, tablero)                    
                    break
                if comando_serv == "S-10": # Juego ganado
                    tablero[fila-1][columna-1] = "o" # Realizar ultimo tiro 
                    mostrar_estado(comando_serv, tablero)
                    TCPClientSocket.sendall(b"C-3") # Preguntar al server el tiempo
                    tiempo_jugado = TCPClientSocket.recv(buffer_size).decode()
                    break

                mostrar_estado(comando_serv, tablero)
                
                tablero[fila-1][columna-1] = "o" # Realizar tiro 
                imprimir_tablero(tablero)

            TCPClientSocket.sendall(b"C-3") # Preguntar al server el tiempo
            tiempo_jugado = TCPClientSocket.recv(buffer_size).decode()
            print("Duración del juego: ", tiempo_jugado)


    except ConnectionError as e:
        print(f"Error de conexión: {e}")
    except Exception as e:
        print(f"Ocurrió un error: {e}")


host = input("Ingresa la IP (del servidor): ")
port = input("Ingresa el puerto (del servidor): ")
iniciar_cliente(host, int(port))
print("\nCliente acabo")